"""Page d'estimation : formulaire à gauche, prix estimé et fourchette à droite."""
import numpy as np
import pandas as pd
import pydeck as pdk
import requests
import streamlit as st

from src.commun import charger_modele, euros, html
from src.entrainer import COMMUNES_BM
from src.variables import construire_variables, sans_vides

URL_GEOCODAGE = "https://data.geopf.fr/geocodage/search"  # Service de géocodage de l'IGN (Géoplateforme)


@st.cache_data(show_spinner=False)
def geocoder(adresse):
    """Renvoie (libellé, latitude, longitude) de la première adresse trouvée dans la métropole, sinon None."""
    reponse = requests.get(URL_GEOCODAGE, params={"q": adresse, "limit": 5}, timeout=10)
    reponse.raise_for_status()
    for lieu in reponse.json().get("features", []):
        if lieu["properties"].get("citycode") in COMMUNES_BM:
            lon, lat = lieu["geometry"]["coordinates"]
            return lieu["properties"]["label"], lat, lon
    return None


def profil_rare(type_local, surface, pieces, terrain):
    """Caractéristiques peu représentées dans les ventes, où l'estimation est moins fiable."""
    alertes = []
    if type_local == "Maison" and surface < 50:
        alertes.append("maison de moins de 50 m²")
    if type_local == "Maison" and surface > 300:
        alertes.append("maison de plus de 300 m²")
    if type_local == "Appartement" and surface > 200:
        alertes.append("appartement de plus de 200 m²")
    if surface / pieces < 9:
        alertes.append("moins de 9 m² par pièce")
    if terrain > 2000:
        alertes.append("terrain de plus de 2 000 m²")
    return alertes


def position(valeur, bas, haut):
    """Position d'un prix sur la barre de la fourchette, en pourcentage de sa largeur."""
    return round(100 * (valeur - bas) / (haut - bas), 1)


def afficher_resultat(r, q, annee):
    """Carte sombre du résultat : prix, prix au m² et fourchette dessinée en barre."""
    prix = r["prix"]
    bornes = {k: prix * v for k, v in q.items()}
    # La barre va un peu au-delà de la fourchette à 80 % pour lui laisser de l'air
    bas, haut = bornes["q10"] * 0.92, bornes["q90"] * 1.06
    html(f"""
    <section class="resultat" aria-label="Résultat de l'estimation">
    <span class="resume">{r['resume']}</span>
    <div class="montants">
    <div><span>Prix estimé</span><b class="prix">{euros(prix, 1000)}</b></div>
    <div><span>Prix au m²</span><b class="m2">{euros(r['prix_m2'], 10)}</b></div>
    </div>
    <div class="fourchette">
    <span class="titre-fourchette">Fourchette, mesurée sur les ventes de {annee}</span>
    <div class="barre-fourchette">
    <div class="piste"></div>
    <div class="zone80" style="left: {position(bornes['q10'], bas, haut)}%; right: {100 - position(bornes['q90'], bas, haut)}%"></div>
    <div class="zone50" style="left: {position(bornes['q25'], bas, haut)}%; right: {100 - position(bornes['q75'], bas, haut)}%"></div>
    <div class="repere" style="left: {position(prix, bas, haut)}%"></div>
    </div>
    <div class="valeurs"><span>{euros(bornes['q10'], 1000)}</span>
    <b>{euros(bornes['q25'], 1000)} – {euros(bornes['q75'], 1000)}</b>
    <span>{euros(bornes['q90'], 1000)}</span></div>
    <p>En orange : une vente sur deux tombe dans cette zone. Des deux valeurs extrêmes : huit ventes sur dix.</p>
    </div>
    </section>
    """)


modele, infos = charger_modele()
q = infos["quantiles_ratio"]
annee_test = infos["scores_test"]["annee"]
date_prix = pd.Timestamp(infos["prix_a_date"] + "-01")
MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]

html(f"""
<div class="entete-page">
<h1>Estimer un logement</h1>
<p>Modèle entraîné sur les ventes DVF {infos['periode']} · estimation aux prix de
{MOIS[date_prix.month - 1]} {date_prix.year}</p>
</div>
""")

gauche, droite = st.columns([1, 1.15], gap="large")

with gauche:
    with st.container(border=True):
        # Le type est hors du formulaire pour afficher le champ « terrain » seulement pour une maison
        type_local = st.segmented_control("Type de logement", ["Appartement", "Maison"],
                                          default="Appartement", required=True, width="stretch")
        with st.form("bien", border=False):
            adresse = st.text_input("Adresse", placeholder="Ex. : 10 cours de l'Intendance, Bordeaux")
            col1, col2 = st.columns(2)
            surface = col1.number_input("Surface habitable (m²)", min_value=9, max_value=400, value=60)
            pieces = col2.number_input("Pièces", min_value=1, max_value=15, value=3)
            col3, col4 = st.columns(2)
            dependances = col3.number_input("Garage, cave, parking", min_value=0, max_value=5, value=0)
            terrain = 0
            if type_local == "Maison":
                terrain = col4.number_input("Terrain (m²)", min_value=0, max_value=5000, value=300)
            valider = st.form_submit_button("Estimer le prix", type="primary", width="stretch")

    if valider:
        if not adresse.strip():
            st.warning("Indique une adresse.")
        else:
            try:
                lieu = geocoder(adresse)
            except requests.RequestException:
                lieu = "erreur"
            if lieu == "erreur":
                st.error("Le service de géocodage ne répond pas. Réessaie dans quelques instants.")
            elif lieu is None:
                st.error("Adresse introuvable dans Bordeaux Métropole. Précise la commune ou le numéro.")
            else:
                libelle, lat, lon = lieu
                # Le bien saisi, avec les mêmes colonnes que la table DVF nettoyée
                bien = pd.DataFrame([{
                    "type_local": type_local,
                    "surface_reelle_bati": surface,
                    "nombre_pieces_principales": pieces,
                    "surface_terrain": terrain if terrain > 0 else np.nan,
                    "nb_dependances": dependances,
                    "latitude": lat,
                    "longitude": lon,
                    "date_mutation": date_prix,
                }])
                X = sans_vides(construire_variables(bien))
                prix_m2 = float(np.exp(modele.predict(X)[0]))   # Le modèle prédit le log du prix au m²
                terrain_txt = f" · terrain {terrain} m²" if type_local == "Maison" else ""
                # Gardé en mémoire de session pour rester affiché si la page se recharge
                st.session_state["resultat"] = {
                    "prix": prix_m2 * surface, "prix_m2": prix_m2, "libelle": libelle,
                    "lat": lat, "lon": lon,
                    "resume": f"{type_local} · {surface} m² · {pieces} pièce{'s' if pieces > 1 else ''}{terrain_txt}",
                    "alertes": profil_rare(type_local, surface, pieces, terrain),
                }

with droite:
    r = st.session_state.get("resultat")
    if r is None:
        html("""
        <div class="attente">
        <b>Votre estimation apparaîtra ici</b>
        <p>Renseignez l'adresse et les caractéristiques du logement, puis cliquez sur « Estimer le prix ».</p>
        </div>
        """)
    else:
        afficher_resultat(r, q, annee_test)
        if r["alertes"]:
            st.warning(
                f"**Profil rare** ({', '.join(r['alertes'])}). Peu de ventes de ce genre ont servi à "
                "l'apprentissage : l'estimation est moins fiable que ne l'indique la fourchette.",
                icon=":material/info:",
            )
        point = pdk.Layer("ScatterplotLayer", pd.DataFrame({"lat": [r["lat"]], "lon": [r["lon"]]}),
                          get_position="[lon, lat]", get_fill_color=[181, 86, 47, 255],
                          get_line_color=[255, 255, 255, 255], line_width_min_pixels=3,
                          stroked=True, get_radius=10, radius_min_pixels=9, radius_max_pixels=12)
        vue = pdk.ViewState(latitude=r["lat"], longitude=r["lon"], zoom=14.5)
        st.pydeck_chart(pdk.Deck(layers=[point], initial_view_state=vue, map_provider="carto",
                                 map_style=pdk.map_styles.CARTO_ROAD), height=260)
        html(f'<p class="adresse">📍 {r["libelle"]}</p>')
    html("""
    <p class="limites">DVF ne renseigne ni l'état du bien, ni l'étage, ni le DPE, ni la vue. Cette estimation
    situe un bien par rapport aux ventes passées : ce n'est pas une expertise.</p>
    """)

html("""
<style>
.entete-page { padding: 40px 0 20px; }
.entete-page h1 { margin: 0; padding: 0; font-size: 40px; font-weight: 800; }
.entete-page p { margin: 6px 0 0; font-size: 16px; color: #5E574E; }
.resultat { background: #2F3437; color: #FFFFFF; border-radius: 16px; padding: 30px;
  display: flex; flex-direction: column; gap: 18px; margin-bottom: 12px; }
.resultat .resume { font-size: 14px; color: #D4CCC0; }
.resultat .montants { display: flex; flex-wrap: wrap; align-items: flex-end; gap: 28px; }
.resultat .montants div { display: flex; flex-direction: column; gap: 4px; }
.resultat .montants span { font-size: 14px; color: #D4CCC0; }
.resultat .prix { font-size: 52px; font-weight: 800; letter-spacing: -0.02em; line-height: 1.05; }
.resultat .m2 { font-size: 26px; font-weight: 700; color: #F0B595; padding-bottom: 6px; }
.fourchette { display: flex; flex-direction: column; gap: 10px; }
.titre-fourchette { font-size: 14px; font-weight: 600; }
.barre-fourchette { position: relative; height: 34px; }
.barre-fourchette div { position: absolute; }
.piste { left: 0; right: 0; top: 13px; height: 8px; border-radius: 4px; background: #4A4F52; }
.zone80 { top: 13px; height: 8px; border-radius: 4px; background: #8C4A2E; }
.zone50 { top: 11px; height: 12px; border-radius: 6px; background: #E07B39; }
.repere { top: 4px; width: 4px; height: 26px; margin-left: -2px; border-radius: 2px; background: #FFFFFF; }
.fourchette .valeurs { display: flex; justify-content: space-between; gap: 8px; font-size: 13px; color: #D4CCC0; }
.fourchette .valeurs b { color: #FFFFFF; }
.fourchette p { margin: 0; font-size: 14px; line-height: 1.5; color: #D4CCC0; }
.attente { border: 2px dashed #D9CFC0; border-radius: 16px; padding: 48px 32px; text-align: center; color: #5E574E; }
.attente b { font-size: 18px; color: #2F3437; }
.attente p { margin: 8px 0 0; }
.adresse { margin: 8px 0 0; font-size: 14px; color: #5E574E; }
.limites { margin: 12px 0 0; font-size: 13px; line-height: 1.5; color: #6F675C; }
@media (max-width: 760px) {
  .entete-page h1 { font-size: 30px; }
  .resultat .prix { font-size: 40px; }
}
</style>
""")
