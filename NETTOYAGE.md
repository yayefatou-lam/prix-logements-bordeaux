# Journal de nettoyage

Ce fichier explique chaque décision prise pour passer des données brutes à la table utilisée par le modèle. Les décomptes viennent du notebook [`01_donnees.ipynb`](notebooks/01_donnees.ipynb) (livraison DVF d'avril 2026) ; le script [`src/entrainer.py`](src/entrainer.py) applique exactement les mêmes règles, et le notebook vérifie que les deux tables sont identiques.

## Du fichier brut à la table finale

| Étape | Ventes restantes |
|---|---:|
| Ventes en Gironde, 2021-2025 | 187 909 |
| dont Bordeaux Métropole | 88 033 |
| dont nature « Vente » | 75 896 |
| dont un seul logement, sans local commercial | 58 514 |
| dont données cohérentes (8 règles) | **57 244** |

Table finale : 35 046 appartements et 22 198 maisons.

## Décisions

**1. Source.** Demandes de valeurs foncières (DVF) géolocalisées, publiées par Etalab sur [data.gouv.fr](https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres-geolocalisees) (livraison d'avril 2026). Fichiers de la Gironde (33), années complètes 2021 à 2025.

**2. Zone.** Les 28 communes de Bordeaux Métropole, filtrées par code INSEE. Contrôle : les 28 communes sont bien présentes dans les données.

**3. Nature de la vente.** Seules les ventes classiques (« Vente ») sont gardées. Sont écartées les ventes sur plan (VEFA), les échanges, les adjudications, les expropriations et les ventes de terrain à bâtir, dont les prix ne suivent pas le même marché.

**4. Une ligne par vente.** Dans DVF, une vente s'étale sur plusieurs lignes (une par local et par parcelle), et le prix total est répété sur chaque ligne. Quand une vente contient plusieurs logements, il est impossible de savoir ce qu'a coûté chacun. Seules les ventes d'un seul appartement ou d'une seule maison sont gardées. Sont écartées les ventes sans logement (garages, caves, terrains seuls), les ventes de plusieurs logements, et 715 ventes comprenant aussi un local commercial.

**5. Dépendances.** Une vente « logement + garage ou cave » est gardée : le prix inclut la dépendance. Le nombre de dépendances devient une variable du modèle.

**6. Surface de terrain.** Pour un appartement, `surface_terrain` est la surface de la parcelle de tout l'immeuble, pas un jardin privatif : la variable est vidée pour les appartements. Pour une maison, c'est la somme des parcelles de la vente, chaque couple (parcelle, type de sol) compté une seule fois. Environ 9 % des maisons n'ont aucune parcelle associée (probablement des maisons en copropriété) : la valeur reste manquante.

**7. Variable cible.** Prix au m² = valeur foncière / surface réelle bâtie. La surface Carrez n'est pas utilisée : elle ne concerne que les lots de copropriété et manque souvent.

**8. Règles de cohérence.** Une vente est écartée si au moins une règle la vise (1 270 ventes, soit 2,2 %) :

| Règle | Appartements | Maisons | Justification |
|---|---:|---:|---|
| Prix ou surface manquants | 18 | 11 | prix au m² incalculable |
| Coordonnées manquantes | 464 | 313 | parcelle non géocodée, localisation impossible |
| Surface < 9 m² | 3 | 1 | sous le minimum légal d'un logement décent |
| Prix au m² < 1 000 € | 152 | 213 | ventes à prix symbolique (dont des ventes à 1 €) |
| Prix au m² > 15 000 € | 23 | 30 | surfaces mal saisies (ex. maison de 6 pièces déclarée à 2 m²) |
| 0 pièce | 22 | 1 | incohérent pour un logement |
| Plus de 15 pièces | 3 | 2 | probable erreur de saisie |
| Plus de 5 dépendances | 22 | 4 | logement vendu avec des parkings en lot : le prix ne reflète plus le logement |

Une vente peut tomber sous plusieurs règles : le total sans double compte est de 1 270.

Les seuils sont fixés à partir de critères justifiables plutôt qu'aux centiles, pour ne pas écarter des ventes valides par construction. Un prix au m² très élevé révèle presque toujours une erreur sur la surface, pas sur le prix.

**9. Données non publiées.** Les conditions d'utilisation de DVF interdisent leur indexation par les moteurs de recherche. Le dépôt ne contient donc pas les données, seulement le code qui les télécharge depuis data.gouv.fr, et les notebooks n'affichent aucune adresse.
