"""
Entraîne le modèle de l'application à partir des données DVF les plus récentes.

Étapes : téléchargement, nettoyage (règles du journal NETTOYAGE.md), mesure de
l'erreur et de la fourchette sur la dernière année, entraînement final sur toutes
les années, puis écriture de modele/lgbm_prix_m2.txt et modele/infos.json.

Lancement, depuis la racine du projet :  python3 -m src.entrainer
"""
import json
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd

from src.variables import construire_variables, sans_vides

RACINE = Path(__file__).resolve().parent.parent
ANNEES = [2021, 2022, 2023, 2024, 2025]
URL = "https://files.data.gouv.fr/geo-dvf/latest/csv/{annee}/departements/33.csv.gz"

# Les 28 communes de Bordeaux Métropole (codes INSEE)
COMMUNES_BM = [
    "33003", "33004", "33013", "33032", "33039", "33056", "33063", "33065",
    "33069", "33075", "33096", "33119", "33162", "33167", "33192", "33200",
    "33249", "33273", "33281", "33312", "33318", "33376", "33434", "33449",
    "33487", "33519", "33522", "33550",
]
LOCAL_COM = "Local industriel. commercial ou assimilé"

# Réglages retenus dans le notebook 03 (recherche aléatoire, validation 2024)
PARAMS = dict(
    objective="regression_l1", num_leaves=63, min_child_samples=30, subsample=1.0,
    colsample_bytree=0.6, reg_lambda=0.0, learning_rate=0.03, subsample_freq=1,
    n_estimators=2089, random_state=42, verbose=-1,
)


def telecharger(annees=ANNEES):
    """Lit les fichiers DVF géolocalisés de la Gironde directement sur data.gouv.fr."""
    types_texte = {"code_commune": str, "code_postal": str, "id_parcelle": str,
                   "code_departement": str, "ancien_code_commune": str}
    morceaux = []
    for annee in annees:
        df = pd.read_csv(URL.format(annee=annee), dtype=types_texte, low_memory=False)
        print(f"  {annee} : {len(df)} lignes")
        morceaux.append(df)
    dvf = pd.concat(morceaux, ignore_index=True)
    dvf["date_mutation"] = pd.to_datetime(dvf["date_mutation"])
    return dvf


def nettoyer(dvf):
    """Applique les règles du journal de nettoyage : une ligne par vente d'un seul logement."""
    etapes = {"Ventes en Gironde": dvf["id_mutation"].nunique()}

    bm = dvf[dvf["code_commune"].isin(COMMUNES_BM)]
    etapes["dont Bordeaux Métropole"] = bm["id_mutation"].nunique()

    bm = bm[bm["nature_mutation"] == "Vente"]
    etapes["dont nature « Vente »"] = bm["id_mutation"].nunique()

    # Composition de chaque vente : nombre de locaux de chaque type
    compo = (bm.dropna(subset=["type_local"])
               .groupby(["id_mutation", "type_local"]).size()
               .unstack(fill_value=0))
    for col in ["Appartement", "Maison", "Dépendance", LOCAL_COM]:
        if col not in compo:
            compo[col] = 0
    logements = compo["Appartement"] + compo["Maison"]
    garder = compo.index[(logements == 1) & (compo[LOCAL_COM] == 0)]
    etapes["dont un seul logement, sans local commercial"] = len(garder)

    # Une ligne par vente : la ligne du logement
    ventes = bm[bm["id_mutation"].isin(garder)]
    cols = ["id_mutation", "date_mutation", "valeur_fonciere", "code_commune", "nom_commune",
            "type_local", "surface_reelle_bati", "nombre_pieces_principales",
            "longitude", "latitude"]
    table = (ventes[ventes["type_local"].isin(["Appartement", "Maison"])][cols]
             .set_index("id_mutation"))
    table["nb_dependances"] = compo.loc[table.index, "Dépendance"]

    # Surface de terrain : chaque couple (parcelle, type de sol) compté une seule fois
    terrain = (ventes.drop_duplicates(["id_mutation", "id_parcelle", "code_nature_culture",
                                       "surface_terrain"])
                     .groupby("id_mutation")["surface_terrain"].sum(min_count=1))
    table["surface_terrain"] = terrain
    # Pour un appartement, c'est la parcelle de tout l'immeuble : non pertinent
    table.loc[table["type_local"] == "Appartement", "surface_terrain"] = np.nan

    table["prix_m2"] = table["valeur_fonciere"] / table["surface_reelle_bati"]

    # Règles de cohérence (journal, règles 1 à 8)
    regles = {
        "prix ou surface manquants": table["prix_m2"].isna(),
        "coordonnées manquantes": table["latitude"].isna() | table["longitude"].isna(),
        "surface < 9 m²": table["surface_reelle_bati"] < 9,
        "prix au m² < 1 000 €": table["prix_m2"] < 1000,
        "prix au m² > 15 000 €": table["prix_m2"] > 15000,
        "0 pièce": table["nombre_pieces_principales"] == 0,
        "plus de 15 pièces": table["nombre_pieces_principales"] > 15,
        "plus de 5 dépendances": table["nb_dependances"] > 5,
    }
    a_ecarter = pd.concat(regles, axis=1).any(axis=1)
    table = table[~a_ecarter].copy()
    etapes["dont données cohérentes (8 règles)"] = len(table)

    for nom, n in etapes.items():
        print(f"  {nom:<48}{n:>8}")
    return table


def evaluer(y_vrai, y_pred):
    """Erreur moyenne (€/m²), erreur relative médiane et part des ventes à ±10 %."""
    erreur_rel = (y_pred - y_vrai).abs() / y_vrai
    return {
        "mae": round(float((y_pred - y_vrai).abs().mean())),
        "erreur_relative_mediane": round(float(erreur_rel.median()), 3),
        "part_10_pct": round(float((erreur_rel <= 0.10).mean()), 3),
    }


def main():
    print("1. Téléchargement")
    dvf = telecharger()
    print("2. Nettoyage")
    table = nettoyer(dvf)

    X = sans_vides(construire_variables(table))
    y = table["prix_m2"]
    annee = table["date_mutation"].dt.year
    derniere = int(annee.max())
    test = annee == derniere

    print(f"3. Contrôle : entraînement avant {derniere}, test sur {derniere}")
    modele = lgb.LGBMRegressor(**PARAMS)
    modele.fit(X[~test], np.log(y[~test]))
    pred = pd.Series(np.exp(modele.predict(X[test])), index=y[test].index)
    scores = evaluer(y[test], pred)
    print(f"  {scores}")

    # Fourchette : rapport prix réel / prix prédit sur la dernière année
    ratio = y[test] / pred
    quantiles = {f"q{int(q * 100)}": round(float(ratio.quantile(q)), 3)
                 for q in [0.10, 0.25, 0.75, 0.90]}
    print(f"  Fourchette : {quantiles}")

    print("4. Entraînement final sur toutes les années")
    modele_final = lgb.LGBMRegressor(**PARAMS)
    modele_final.fit(X, np.log(y))

    dossier = RACINE / "modele"
    dossier.mkdir(parents=True, exist_ok=True)
    modele_final.booster_.save_model(str(dossier / "lgbm_prix_m2.txt"))
    infos = {
        "quantiles_ratio": quantiles,
        "periode": f"{int(annee.min())}-{derniere}",
        "prix_a_date": table["date_mutation"].max().strftime("%Y-%m"),
        "ventes": int(len(table)),
        "scores_test": {"annee": derniere, **scores},
    }
    (dossier / "infos.json").write_text(json.dumps(infos, indent=2, ensure_ascii=False),
                                        encoding="utf-8")
    print(f"5. Modèle et informations enregistrés dans {dossier}")


if __name__ == "__main__":
    main()
