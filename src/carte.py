"""
Prépare les données de la page « Carte des prix » de l'application.

Les ventes sont regroupées en hexagones H3 (résolution 8, environ 800 m de large,
comme sur la carte du notebook 02), et seuls les hexagones d'au moins 10 ventes sont
gardés. Un second fichier place le nom de chaque commune. Les fichiers produits ne
contiennent que des médianes : aucune vente ni aucune adresse.

Lancement, depuis la racine du projet, après le notebook 01 :  python3 -m src.carte
"""
from pathlib import Path

import h3
import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
RESOLUTION = 8
MIN_VENTES = 10


def agreger(table):
    """Prix médian au m² et nombre de ventes par hexagone, pour chaque type et pour l'ensemble."""
    ventes = table[["type_local", "latitude", "longitude", "prix_m2"]].copy()
    ventes["hexagone"] = [h3.latlng_to_cell(lat, lon, RESOLUTION)
                          for lat, lon in zip(ventes["latitude"], ventes["longitude"])]
    # Une copie de toutes les ventes sous le type « Tous »
    ventes = pd.concat([ventes, ventes.assign(type_local="Tous")], ignore_index=True)

    carte = (ventes.groupby(["type_local", "hexagone"])["prix_m2"]
                   .agg(prix_m2="median", ventes="size")
                   .reset_index())
    carte = carte[carte["ventes"] >= MIN_VENTES]
    carte["prix_m2"] = carte["prix_m2"].round(-1).astype(int)
    return carte


def communes(table):
    """Position du nom de chaque commune sur la carte : point médian de ses ventes."""
    return (table.groupby("nom_commune")[["latitude", "longitude"]].median()
                 .round(4).reset_index())


def main():
    table = pd.read_parquet(RACINE / "data" / "ventes_bm_2021_2025.parquet")
    carte = agreger(table)
    sortie = RACINE / "modele" / "carte_prix.csv"
    carte.to_csv(sortie, index=False)
    communes(table).to_csv(RACINE / "modele" / "carte_communes.csv", index=False)
    print(f"{len(carte)} hexagones enregistrés dans {sortie}")
    print(carte.groupby("type_local")["ventes"].agg(["size", "sum"]))


if __name__ == "__main__":
    main()
