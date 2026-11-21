"""Page À propos : l'auteure à gauche, le projet raconté en quatre étapes à droite."""
from src.commun import LIENS, charger_modele, html, nombre

_, infos = charger_modele()
scores = infos["scores_test"]

etapes = [
    ("Les données", f"Le fichier DVF de la Gironde, ramené à {nombre(infos['ventes'])} ventes d'un seul "
                    "logement à Bordeaux Métropole, avec 8 règles de nettoyage documentées."),
    ("L'exploration", "Le prix au m² des maisons a reculé de 12 % depuis le pic de 2022 ; la distance au "
                      "centre et la rive de la Garonne pèsent le plus."),
    ("Le modèle", "Huit approches comparées, de la régression linéaire au gradient boosting. Le LightGBM "
                  f"retenu, testé sur les ventes de {scores['annee']}, se trompe de "
                  f"{nombre(100 * scores['erreur_relative_mediane'], 1)} % en médiane."),
    ("L'application", "Estimation à l'adresse avec une fourchette mesurée, et carte des prix par quartier."),
]
frise = "".join(
    f'<li><div class="puce"><span>{i}</span>{"<i></i>" if i < len(etapes) else ""}</div>'
    f'<div class="texte"><h3>{titre}</h3><p>{texte}</p></div></li>'
    for i, (titre, texte) in enumerate(etapes, 1)
)
outils = "".join(f"<span>{o}</span>" for o in
                 ["Python", "pandas", "scikit-learn", "LightGBM", "SHAP", "Streamlit"])

html(f"""
<div class="a-propos">

<aside class="carte-blanche auteure" aria-label="L'auteure">
<h1>Yaye Fatou LAM</h1>
<p class="formation">Étudiante en Master 2 Mathématiques appliquées, statistique · parcours Image,
Optimisation et Sciences des Données · Université de Bordeaux</p>
<div class="recherche">
<span>Recherche</span>
<p><strong>Stage de fin d'études</strong> en data science, data analysis, IA ou vision par ordinateur,
à partir de <strong>mars 2027</strong>.</p>
</div>
<a class="bouton plein" href="mailto:{LIENS['email']}">Me contacter</a>
<div class="reseaux">
<a class="bouton contour" href="{LIENS['linkedin']}" target="_blank">LinkedIn</a>
<a class="bouton contour" href="{LIENS['github']}" target="_blank">GitHub</a>
</div>
<p class="email">{LIENS['email']}</p>
</aside>

<section class="projet" aria-label="Le projet">
<p class="surtitre">Le projet</p>
<h2>Des ventes notariées à une estimation en ligne</h2>
<p class="intro">Un projet personnel de data science, de bout en bout : récupérer le fichier public des
ventes immobilières (DVF), le nettoyer, comprendre ce qui fait le prix, entraîner un modèle et le mettre
à disposition dans cette application.</p>
<ol class="frise">{frise}</ol>
<div class="outils"><b>Outils</b><div>{outils}</div></div>
<div class="liens-projet">
<a class="carte-blanche carte-lien" href="{LIENS['notebooks']}" target="_blank">
<b>Lire les notebooks →</b><span>Données, exploration et modèle, pas à pas</span></a>
<a class="carte-blanche carte-lien" href="{LIENS['depot']}" target="_blank">
<b>Voir le code →</b><span>Dépôt GitHub et journal de nettoyage</span></a>
</div>
<p class="limites">Limites : DVF ne renseigne ni l'état du bien, ni l'étage, ni le DPE. L'estimation situe
un bien par rapport aux ventes passées, ce n'est pas une expertise.</p>
</section>

</div>

""")

html("""
<style>
.a-propos { display: flex; flex-wrap: wrap; gap: 48px; align-items: flex-start; padding: 48px 0 8px; }
.auteure { flex: 1 1 400px; max-width: 460px; padding: 36px; display: flex; flex-direction: column; gap: 20px; }
.auteure h1 { margin: 0; padding: 0; font-size: 34px; font-weight: 800; }
.auteure .formation { margin: 0; font-size: 16px; line-height: 1.55; color: #5E574E; }
.recherche { background: #FBEFE7; border-radius: 12px; padding: 20px; display: flex; flex-direction: column; gap: 6px; }
.recherche span { font-size: 13px; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; color: #9A4626; }
.recherche p { margin: 0; font-size: 17px; line-height: 1.5; color: #2F3437; }
.auteure .reseaux { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.auteure .email { margin: 0; text-align: center; font-size: 14px; color: #6F675C; }
.projet { flex: 999 1 520px; min-width: 0; display: flex; flex-direction: column; gap: 24px; }
.projet h2 { margin: 0; padding: 0; font-size: 34px; line-height: 1.15; font-weight: 800; }
.projet .intro { margin: 0; font-size: 17px; line-height: 1.6; color: #4D473F; }
.frise { margin: 0; padding: 0; list-style: none; }
.frise li { display: flex; gap: 18px; }
.frise .puce { display: flex; flex-direction: column; align-items: center; }
.frise .puce span { width: 34px; height: 34px; flex: none; border-radius: 50%; background: #B5562F; color: #FFFFFF;
  font-weight: 700; font-size: 15px; display: flex; align-items: center; justify-content: center; }
.frise .puce i { flex: 1; width: 2px; background: #E6DED2; }
.frise .texte { padding-bottom: 22px; }
.frise h3 { margin: 4px 0 4px; padding: 0; font-size: 18px; font-weight: 700; }
.frise p { margin: 0; font-size: 15px; line-height: 1.55; color: #5E574E; }
.outils { display: flex; flex-direction: column; gap: 10px; }
.outils b { font-size: 14px; }
.outils div { display: flex; flex-wrap: wrap; gap: 8px; }
.outils span { font-size: 14px; padding: 7px 12px; border-radius: 999px; background: #FFFDF9; border: 1px solid #E6DED2; }
.liens-projet { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.carte-lien { padding: 20px; display: flex; flex-direction: column; gap: 4px; text-decoration: none !important;
  color: #2F3437 !important; }
.carte-lien:hover { border-color: #B5562F; }
.carte-lien span { font-size: 14px; color: #5E574E; }
.projet .limites { margin: 0; font-size: 13px; line-height: 1.5; color: #6F675C; }
@media (max-width: 760px) {
  .a-propos { padding-top: 24px; gap: 32px; }
  .auteure { max-width: none; padding: 24px; }
  .liens-projet { grid-template-columns: 1fr; }
  .projet h2 { font-size: 28px; }
}
</style>
""")
