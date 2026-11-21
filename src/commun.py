"""Éléments partagés par les pages de l'application : modèle, palette, mise en forme."""
import base64
import json
import textwrap
from functools import lru_cache
from pathlib import Path

import lightgbm as lgb
import streamlit as st

RACINE = Path(__file__).resolve().parent.parent
MODELE = RACINE / "modele"

# Palette « Pierre de Bordeaux »
TERRA, TERRA_FONCE, ARDOISE, GRIS = "#B5562F", "#9A4626", "#2F3437", "#5E574E"

# Huit classes de prix au m², les mêmes que sur la carte du notebook 02
BORNES = list(range(2000, 6001, 500))
COULEURS_CLASSES = ["#FBE7B5", "#F6C77D", "#EFA055", "#E07B39",
                    "#C8572A", "#A53D20", "#7E2A17", "#521A10"]
SOUS_BORNES, AU_DESSUS = "#FFF6DD", "#2E0E08"

# Pages de l'application : chemin dans l'adresse et nom dans le menu
PAGES = [("", "Accueil"), ("estimation", "Estimer"), ("carte", "Carte des prix"), ("a_propos", "À propos")]

LIENS = {
    "email": "yayefatou.lam@icloud.com",
    "linkedin": "https://www.linkedin.com/in/yaye-fatou-lam-258925412",
    "github": "https://github.com/yayefatou-lam",
    "depot": "https://github.com/yayefatou-lam/prix-logements-bordeaux",
    "notebooks": "https://nbviewer.org/github/yayefatou-lam/prix-logements-bordeaux/tree/main/notebooks/",
}


@st.cache_resource
def charger_modele():
    """Charge le modèle et ses informations une seule fois, au démarrage."""
    modele = lgb.Booster(model_file=str(MODELE / "lgbm_prix_m2.txt"))
    infos = json.loads((MODELE / "infos.json").read_text(encoding="utf-8"))
    return modele, infos


def euros(x, arrondi=1):
    """Montant arrondi, au format français : 312 000 €."""
    return f"{round(x / arrondi) * arrondi:,.0f} €".replace(",", " ")


def nombre(x, decimales=0):
    """Nombre au format français : 57 244 ou 11,6."""
    return f"{x:,.{decimales}f}".replace(",", " ").replace(".", ",")


def html(code):
    """Affiche du HTML. Sans indentation ni ligne vide, sinon Markdown le prend pour du code."""
    lignes = [l for l in textwrap.dedent(code).splitlines() if l.strip()]
    st.markdown("\n".join(l.strip() for l in lignes), unsafe_allow_html=True)


@lru_cache
def image_base64(nom):
    """Image du dossier assets, intégrée directement dans le HTML."""
    return base64.b64encode((RACINE / "assets" / nom).read_bytes()).decode()


LOGO = """<svg width="34" height="34" viewBox="0 0 34 34" aria-hidden="true">
<path d="M17 2 L30 9.5 V24.5 L17 32 L4 24.5 V9.5 Z" fill="#B5562F"></path>
<path d="M11 22 V15 L17 11 L23 15 V22" fill="none" stroke="#FFFDF9" stroke-width="2.2" stroke-linejoin="round"></path>
</svg>"""


def barre_navigation(page_active):
    """Style commun et barre du haut : logo, liens des pages, et menu ☰ sur téléphone.

    Le style est envoyé dans le même bloc que la barre : un bloc à part ajouterait
    un espace vide en haut de la page.
    """
    liens = "".join(
        f'<a href="/{chemin}" target="_self" class="{"actif" if chemin == page_active else ""}">{nom}</a>'
        for chemin, nom in PAGES
    )
    html(STYLE + f"""
    <div id="haut"></div>
    <nav class="barre" aria-label="Navigation principale">
    <a href="/" target="_self" class="marque">{LOGO}
    <span><b>Prix des logements</b><small>Bordeaux Métropole</small></span></a>
    <div class="liens">{liens}</div>
    <details class="menu"><summary aria-label="Ouvrir le menu">☰</summary>
    <div class="menu-liens">{liens}</div></details>
    </nav>
    """)


def pied_de_page():
    """Pied de page et bouton de retour en haut."""
    html(f"""
    <footer class="pied">
    <span>Projet de data science · Yaye Fatou Lam</span>
    <span>Données : DVF géolocalisées (DGFiP, Etalab) · <a href="{LIENS['depot']}">Code sur GitHub</a></span>
    </footer>
    <a class="retour-haut" href="#haut" title="Revenir en haut" aria-label="Revenir en haut">↑</a>
    """)


STYLE = """
<style>
/* Masque l'habillage de Streamlit pour un rendu d'application */
header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
[data-testid="stMainBlockContainer"], .block-container {
  max-width: 1200px; padding: 0 32px 0 !important; }
[data-testid="stMain"] { padding-top: 0 !important; }
[data-testid="stMainBlockContainer"] > div > div:first-child { margin-top: 0; }
html { scroll-behavior: smooth; }

/* Bandes pleine largeur : le fond déborde de la colonne centrale */
.pleine-largeur { box-shadow: 0 0 0 100vmax #FFFDF9; clip-path: inset(0 -100vmax); background: #FFFDF9; }

/* Barre de navigation */
.barre { display: flex; align-items: center; justify-content: space-between; gap: 24px; height: 72px;
  position: relative; isolation: isolate; z-index: 100; margin-bottom: 8px; }
/* Le bloc de la barre passe au-dessus du reste de la page, pour le menu déroulant */
[data-testid="stElementContainer"]:has(.barre), .stMarkdown:has(.barre) { position: relative; z-index: 100; }
/* Fond blanc sur toute la largeur de l'écran, sans couper le menu déroulant */
.barre::before { content: ""; position: absolute; top: 0; bottom: 0; left: -100vmax; right: -100vmax;
  z-index: -1; background: #FFFDF9; border-bottom: 1px solid #E6DED2; }
.barre a { text-decoration: none !important; }
.marque { display: flex; align-items: center; gap: 12px; color: #2F3437 !important; }
.marque span { display: flex; flex-direction: column; line-height: 1.15; }
.marque b { font-size: 17px; }
.marque small { font-size: 13px; color: #6F675C; }
.liens { display: flex; align-items: center; gap: 32px; height: 100%; }
.liens a { color: #5E574E !important; font-weight: 500; font-size: 15px; height: 100%;
  display: flex; align-items: center; border-bottom: 2px solid transparent; }
.liens a.actif { color: #2F3437 !important; font-weight: 600; border-bottom-color: #B5562F; }
.liens a:hover { color: #2F3437 !important; }
.menu { display: none; position: relative; }
.menu summary { list-style: none; cursor: pointer; width: 44px; height: 44px; border: 1px solid #E6DED2;
  border-radius: 10px; background: #FFFFFF; display: flex; align-items: center; justify-content: center;
  font-size: 20px; }
.menu summary::-webkit-details-marker { display: none; }
.menu-liens { position: absolute; right: 0; top: 52px; z-index: 1000; background: #FFFDF9;
  border: 1px solid #E6DED2; border-radius: 12px; box-shadow: 0 8px 24px rgba(47, 52, 55, 0.14);
  padding: 8px; display: flex; flex-direction: column; min-width: 200px; }
.menu-liens a { color: #2F3437 !important; padding: 12px 14px; border-radius: 8px; font-size: 16px; }
.menu-liens a.actif { background: #FBEFE7; color: #8E3F1F !important; font-weight: 600; }
@media (max-width: 760px) {
  .liens { display: none; }
  .menu { display: block; }
  [data-testid="stMainBlockContainer"], .block-container { padding: 0 18px !important; }
}

/* Textes et boutons */
h1, h2, h3 { color: #2F3437; letter-spacing: -0.01em; }
.surtitre { margin: 0; font-size: 14px; font-weight: 600; letter-spacing: 0.06em;
  text-transform: uppercase; color: #9A4626; }
.bouton { display: inline-block; text-decoration: none !important; font-weight: 600; font-size: 16px;
  padding: 14px 24px; border-radius: 10px; text-align: center; }
.bouton.plein { background: #B5562F; color: #FFFFFF !important; }
.bouton.plein:hover { background: #9A4626; }
.bouton.contour { background: #FFFDF9; color: #2F3437 !important; border: 1px solid #D9CFC0; }
.bouton.contour:hover { border-color: #B5562F; }
.carte-blanche { background: #FFFDF9; border: 1px solid #E6DED2; border-radius: 16px; }
.stMarkdown a:not(.bouton):not(.retour-haut):not(.marque):not(.carte-lien) { color: #B5562F; }

/* Boutons et champs de Streamlit aux couleurs du projet */
.stButton button, .stFormSubmitButton button { border-radius: 10px; min-height: 48px; font-weight: 600; }
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input { background: #FFFFFF; }
[data-testid="stVerticalBlockBorderWrapper"] { background: #FFFDF9; border-radius: 16px; }

/* Pied de page */
.pied { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 12px; padding: 24px 0;
  margin-top: 56px; font-size: 14px; color: #6F675C; border-top: 1px solid #E6DED2;
  background: #FFFDF9; box-shadow: 0 0 0 100vmax #FFFDF9; clip-path: inset(0 -100vmax); }

/* Bouton de retour en haut de page, en bas à droite */
#haut { scroll-margin-top: 10rem; }
.retour-haut { position: fixed; right: 1.5rem; bottom: 1.5rem; z-index: 1000;
  width: 2.8rem; height: 2.8rem; border-radius: 50%;
  background: #B5562F; color: #FFFFFF !important; text-decoration: none !important;
  display: none; align-items: center; justify-content: center;
  font-size: 1.4rem; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.18); }
.retour-haut:hover { background: #9A4626; }
/* Le bouton n'apparaît que sur téléphone, où les pages deviennent longues */
@media (max-width: 760px) { .retour-haut { display: flex; } }
</style>
"""
