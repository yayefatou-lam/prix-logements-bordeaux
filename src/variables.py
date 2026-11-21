"""Préparation des variables du modèle, partagée par les notebooks et l'application."""
import numpy as np
import pandas as pd

# Point de référence : place de la Comédie, centre de Bordeaux
CENTRE_LAT, CENTRE_LON = 44.8427, -0.5745


def distance_km(lat, lon, lat0=CENTRE_LAT, lon0=CENTRE_LON):
    """Distance à vol d'oiseau en km (formule de haversine)."""
    lat, lon, lat0, lon0 = map(np.radians, [lat, lon, lat0, lon0])
    a = np.sin((lat - lat0) / 2) ** 2 + np.cos(lat) * np.cos(lat0) * np.sin((lon - lon0) / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(a))


def construire_variables(df):
    """Transforme une table de ventes (colonnes DVF) en variables pour le modèle."""
    X = pd.DataFrame(index=df.index)
    X["maison"] = (df["type_local"] == "Maison").astype(int)
    X["surface"] = df["surface_reelle_bati"]
    X["pieces"] = df["nombre_pieces_principales"]
    X["surface_terrain"] = df["surface_terrain"]      # Vide pour les appartements
    X["nb_dependances"] = df["nb_dependances"]
    X["latitude"] = df["latitude"]
    X["longitude"] = df["longitude"]
    X["distance_centre_km"] = distance_km(df["latitude"], df["longitude"])
    # Nombre de mois écoulés depuis janvier 2021 (0 = janvier 2021)
    X["mois"] = (df["date_mutation"].dt.year - 2021) * 12 + df["date_mutation"].dt.month - 1
    return X


def sans_vides(X):
    """Terrain manquant remplacé par 0, avec un indicateur, comme pendant l'entraînement."""
    X = X.copy()
    X["a_terrain"] = X["surface_terrain"].notna().astype(int)
    X["surface_terrain"] = X["surface_terrain"].fillna(0)
    return X
