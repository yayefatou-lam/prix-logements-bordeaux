"""Mise en forme commune des tableaux des notebooks (palette « Pierre de Bordeaux »)."""
import numbers

import pandas as pd

PIERRE, ENCRE = "#EFE6D8", "#2F3437"
SAUGE_FOND, SAUGE = "#E8ECDF", "#55623F"   # Zone normale, plausible ou meilleur résultat
OCRE_FOND, OCRE = "#F5E6D8", "#8A6420"     # Valeurs suspectes, fragiles ou référence


def _format(decimales):
    """Nombres à la française : 1 079 405 ; 11,6 ; tiret pour une valeur manquante."""
    def nombre(v):
        if isinstance(v, numbers.Number) and not isinstance(v, bool):
            if pd.isna(v):
                return "–"
            return f"{v:,.{decimales}f}".replace(",", " ").replace(".", ",")
        return v
    return nombre


def fr(x, decimales=0):
    """Nombre à la française pour les phrases : fr(57244) -> '57 244', fr(2.24, 1) -> '2,2'."""
    return f"{x:,.{decimales}f}".replace(",", " ").replace(".", ",")


def tableau(df, sauge=(), ocre=(), gras=(), decimales=0, legende=None):
    """
    Affiche un tableau lisible : police plus grande, lignes en sauge (zone normale,
    meilleur résultat) ou en ocre (valeurs suspectes, référence).
    decimales : un entier pour tout le tableau, ou un dictionnaire {colonne: décimales}.
    """
    if isinstance(df, pd.Series):
        df = df.to_frame()
    if isinstance(decimales, dict):
        formats = {c: _format(decimales.get(c, 0)) for c in df.columns}
    else:
        formats = {c: _format(decimales) for c in df.columns}

    style = (df.style
             .format(formats, escape="html")
             .format_index(escape="html", axis=0)
             .format_index(escape="html", axis=1)
             .set_table_styles([
                 {"selector": "", "props": [("font-size", "14px"), ("border-collapse", "collapse")]},
                 {"selector": "th", "props": [("background-color", PIERRE), ("color", ENCRE),
                                              ("padding", "8px 14px"), ("text-align", "right")]},
                 {"selector": "td", "props": [("padding", "8px 14px"), ("text-align", "right")]},
                 {"selector": "caption", "props": [("caption-side", "bottom"), ("color", "#7C7368"),
                                                   ("font-size", "12px"), ("padding-top", "8px")]},
             ]))
    for lignes, fond, texte in [(sauge, SAUGE_FOND, SAUGE), (ocre, OCRE_FOND, OCRE)]:
        if len(lignes):
            style = style.set_properties(subset=pd.IndexSlice[list(lignes), :],
                                         **{"background-color": fond, "color": texte, "font-weight": "bold"})
    if len(gras):
        style = style.set_properties(subset=pd.IndexSlice[list(gras), :], **{"font-weight": "bold"})
    if legende:
        style = style.set_caption(legende)
    return style
