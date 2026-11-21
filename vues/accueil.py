"""Page d'accueil : ce que fait l'application et comment elle fonctionne."""
from src.commun import charger_modele, html, image_base64, nombre

_, infos = charger_modele()
scores = infos["scores_test"]

html(f"""
<section class="accueil-haut">
<div class="accroche">
<p class="surtitre">Bordeaux Métropole · 28 communes</p>
<h1>Combien vaut votre logement ?</h1>
<p class="intro">Une estimation du prix d'un appartement ou d'une maison, calculée à partir des ventes
réellement enregistrées chez les notaires entre {infos['periode'].replace('-', ' et ')}.</p>
<div class="boutons">
<a class="bouton plein" href="/estimation" target="_self">Estimer un logement</a>
<a class="bouton contour" href="/carte" target="_self">Voir la carte des prix</a>
</div>
<p class="note">Gratuit · sans inscription · aucune donnée conservée</p>
</div>
<figure class="illustration">
<img src="data:image/png;base64,{image_base64('quais.png')}"
alt="Illustration des façades de la place de la Bourse et de leur reflet dans le miroir d'eau">
<figcaption>Place de la Bourse et miroir d'eau</figcaption>
</figure>
</section>

<section class="chiffres pleine-largeur" aria-label="Chiffres clés">
<div><b>{nombre(infos['ventes'])}</b><span>ventes analysées, {infos['periode']}</span></div>
<div><b>{nombre(100 * scores['erreur_relative_mediane'], 1)} %</b><span>d'erreur médiane sur les ventes de {scores['annee']}</span></div>
<div><b>{nombre(100 * scores['part_10_pct'])} %</b><span>des ventes estimées à ±10 % près</span></div>
<div><b>28</b><span>communes couvertes</span></div>
</section>

<section class="etapes">
<h2>Comment ça marche</h2>
<div class="grille-etapes">
<div class="carte-blanche etape"><span class="num">1</span><h3>Indiquez l'adresse</h3>
<p>Elle est localisée avec le service de géocodage de l'IGN. Le quartier est ce qui pèse le plus sur le prix.</p></div>
<div class="carte-blanche etape"><span class="num">2</span><h3>Décrivez le bien</h3>
<p>Type, surface, nombre de pièces, dépendances et, pour une maison, la surface du terrain.</p></div>
<div class="carte-blanche etape"><span class="num">3</span><h3>Obtenez une fourchette</h3>
<p>Un prix estimé et une fourchette mesurée sur les ventes de {scores['annee']}, pour savoir quelle confiance lui accorder.</p></div>
</div>
</section>

""")

html("""
<style>
.accueil-haut { display: flex; flex-wrap: wrap; align-items: center; gap: 56px; padding: 56px 0 56px; }
.accroche { flex: 1 1 440px; display: flex; flex-direction: column; gap: 20px; }
.accroche h1 { margin: 0; padding: 0; font-size: 56px; line-height: 1.05; font-weight: 800; }
.accroche .intro { margin: 0; font-size: 19px; line-height: 1.55; color: #4D473F; max-width: 520px; }
.accroche .boutons { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 6px; }
.accroche .note { margin: 0; font-size: 14px; color: #6F675C; }
.illustration { flex: 1 1 440px; margin: 0; background: #EFE6D8; border-radius: 20px; padding: 40px 32px 20px;
  display: flex; flex-direction: column; align-items: center; gap: 8px; }
.illustration img { width: 100%; max-width: 520px; height: auto; }
.illustration figcaption { align-self: flex-end; font-size: 12px; color: #6F675C; }
.chiffres { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 24px; padding: 36px 0;
  border-top: 1px solid #E6DED2; border-bottom: 1px solid #E6DED2; }
.chiffres div { display: flex; flex-direction: column; gap: 6px; }
.chiffres b { font-size: 36px; font-weight: 800; color: #B5562F; line-height: 1.1; }
.chiffres div > span { font-size: 15px; color: #5E574E; }
.etapes { padding: 56px 0 8px; display: flex; flex-direction: column; gap: 24px; }
.etapes h2 { margin: 0; padding: 0; font-size: 30px; font-weight: 700; }
.grille-etapes { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px; }
.etape { padding: 28px; display: flex; flex-direction: column; gap: 10px; }
.etape .num { width: 36px; height: 36px; border-radius: 50%; background: #F3E3D8; color: #9A4626;
  font-weight: 700; display: flex; align-items: center; justify-content: center; }
.etape h3 { margin: 0; padding: 0; font-size: 19px; font-weight: 700; }
.etape p { margin: 0; font-size: 15px; line-height: 1.55; color: #5E574E; }
@media (max-width: 760px) {
  .accueil-haut { padding: 28px 0; gap: 28px; }
  .accroche h1 { font-size: 36px; }
  .accroche .intro { font-size: 16px; }
  .accroche .bouton { width: 100%; }
  .chiffres { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .chiffres b { font-size: 26px; }
  .grille-etapes { grid-template-columns: 1fr; }
}
</style>
""")
