"""
Prix des logements à Bordeaux Métropole : point d'entrée de l'application.

Ce fichier gère ce qui est commun à toutes les pages : la barre de navigation,
le style, le pied de page et le bouton de retour en haut. Le contenu de chaque
page est dans vues/ (un dossier nommé « pages » activerait l'ancien menu
automatique de Streamlit).

Lancement, depuis la racine du projet :  streamlit run app.py
"""
import streamlit as st

from src.commun import barre_navigation, pied_de_page

st.set_page_config(page_title="Prix des logements · Bordeaux Métropole", page_icon="🏠",
                   layout="wide")

# Les quatre pages ; le menu natif de Streamlit est masqué au profit de la barre du haut
page = st.navigation([
    st.Page("vues/accueil.py", title="Accueil", url_path="", default=True),
    st.Page("vues/estimation.py", title="Estimer un logement", url_path="estimation"),
    st.Page("vues/carte.py", title="Carte des prix", url_path="carte"),
    st.Page("vues/a_propos.py", title="À propos", url_path="a_propos"),
], position="hidden")

barre_navigation(page.url_path)
page.run()
pied_de_page()
