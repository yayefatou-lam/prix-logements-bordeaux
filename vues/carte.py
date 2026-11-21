"""Carte interactive des prix médians au m², par hexagone de 800 m environ."""
import pandas as pd
import pydeck as pdk
import streamlit as st

from src.commun import (AU_DESSUS, BORNES, COULEURS_CLASSES, MODELE, SOUS_BORNES,
                        charger_modele, html, nombre)
from src.variables import CENTRE_LAT, CENTRE_LON


@st.cache_data
def charger_carte():
    """Médianes par hexagone (au moins 10 ventes) et position des noms de communes, préparées par src/carte.py."""
    return pd.read_csv(MODELE / "carte_prix.csv"), pd.read_csv(MODELE / "carte_communes.csv")


def couleur(prix):
    """Couleur de la classe de prix, en [rouge, vert, bleu, opacité] pour pydeck."""
    if prix < BORNES[0]:
        code = SOUS_BORNES
    elif prix >= BORNES[-1]:
        code = AU_DESSUS
    else:
        code = COULEURS_CLASSES[sum(prix >= b for b in BORNES[1:])]
    # Opacité partielle : les rues et le fond de carte restent visibles sous les hexagones
    return [int(code[i:i + 2], 16) for i in (1, 3, 5)] + [165]


_, infos = charger_modele()
carte, communes = charger_carte()

panneau, zone_carte = st.columns([1, 2.6], gap="large")

with panneau:
    html(f"""
    <div class="entete-carte">
    <h1>Carte des prix</h1>
    <p>Prix médian au m² des ventes {infos['periode']}, par zone d'environ 800 m. Seules les zones
    d'au moins 10 ventes apparaissent.</p>
    </div>
    """)
    choix = st.segmented_control("Type de logement", ["Tous", "Appartement", "Maison"], default="Tous",
                                 required=True, width="stretch", label_visibility="collapsed")
    cases = "".join(
        f'<span class="case"><i style="background:{c}"></i>{nombre(b)}</span>'
        for b, c in zip(BORNES[:-1], COULEURS_CLASSES)
    )
    html(f"""
    <div class="legende">
    <b>Prix médian (€/m²)</b>
    <div class="cases">{cases}</div>
    <small>En dessous de {nombre(BORNES[0])} € : couleur la plus claire ;
    au-delà de {nombre(BORNES[-1])} € : la plus foncée.</small>
    </div>
    <p class="aide">Survolez une zone pour voir son prix médian et son nombre de ventes.
    Seules des médianes par zone sont affichées : aucune vente individuelle ni aucune adresse.</p>
    """)

zones = carte[carte["type_local"] == choix].copy()
zones["couleur"] = zones["prix_m2"].map(couleur)
zones["prix_texte"] = zones["prix_m2"].map(lambda p: f"{nombre(p)} €/m²")
zones["ventes_texte"] = zones["ventes"].map(nombre)

hexagones = pdk.Layer(
    "H3HexagonLayer", zones, get_hexagon="hexagone", get_fill_color="couleur",
    get_line_color=[255, 255, 255, 140], line_width_min_pixels=0.6,
        pickable=True, auto_highlight=True, highlight_color=[255, 255, 255, 110], extruded=False,
)
# Noms des communes par-dessus les hexagones, pour se repérer
noms = pdk.Layer(
    "TextLayer", communes, get_position="[longitude, latitude]", get_text="nom_commune",
    get_size=13, get_color=[47, 52, 55, 255], get_text_anchor='"middle"',
    get_alignment_baseline='"center"', font_family='"Inter", "Helvetica Neue", Arial, sans-serif',
    font_weight=600, outline_width=3, outline_color=[255, 253, 249, 255],
    font_settings={"sdf": True}, character_set="auto",
)
vue = pdk.ViewState(latitude=CENTRE_LAT, longitude=CENTRE_LON, zoom=10.8)
infobulle = {"html": "<b>{prix_texte}</b><br/>{ventes_texte} ventes",
             "style": {"backgroundColor": "#2F3437", "color": "white", "fontSize": "13px",
                       "fontFamily": "Inter, sans-serif", "borderRadius": "8px"}}

with zone_carte:
    st.pydeck_chart(pdk.Deck(layers=[hexagones, noms], initial_view_state=vue, tooltip=infobulle,
                             map_provider="carto", map_style=pdk.map_styles.CARTO_ROAD), height=640)

html("""
<style>
.entete-carte { padding: 32px 0 8px; }
.entete-carte h1 { margin: 0; padding: 0; font-size: 34px; font-weight: 800; }
.entete-carte p { margin: 8px 0 0; font-size: 15px; line-height: 1.5; color: #5E574E; }
.legende { display: flex; flex-direction: column; gap: 8px; margin-top: 8px; }
.legende b { font-size: 14px; }
.legende .cases { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 6px 4px; }
.legende .case { display: flex; flex-direction: column; gap: 3px; font-size: 12px; color: #5E574E; }
.legende .case i { display: block; height: 10px; border-radius: 2px; }
.legende small { font-size: 12px; color: #6F675C; line-height: 1.4; }
.aide { margin: 16px 0 0; padding-top: 16px; border-top: 1px solid #E6DED2; font-size: 13px;
  line-height: 1.5; color: #6F675C; }
[data-testid="stDeckGlJsonChart"] { border-radius: 16px; overflow: hidden; margin-top: 32px; }
@media (max-width: 760px) { [data-testid="stDeckGlJsonChart"] { margin-top: 0; } }
</style>
""")
