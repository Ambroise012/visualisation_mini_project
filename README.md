# Mini-Projet — Prénoms en France (1900–2020)

> IGR204 · Télécom Paris  
> Données : INSEE — prénoms enregistrés en France métropolitaine, par département, de 1900 à 2020.

---

## Contexte et questions

Le projet demande de répondre à trois familles de questions à travers des visualisations interactives :

| # | Question centrale |
|---|-------------------|
| **1** | Comment les prénoms évoluent-ils dans le temps ? Y a-t-il des prénoms durablement populaires, d'autres éphémères ou issus d'un effet de mode ? |
| **2** | Y a-t-il un effet régional ? Certains prénoms sont-ils populaires dans certaines régions seulement ? Les prénoms populaires le sont-ils partout en France ? |
| **3** | Y a-t-il des effets de genre ? La popularité des prénoms donnés aux deux sexes évolue-t-elle de façon cohérente ? |

---

## Visualisation 3 — Gender Space × Évolution miroir

> **Question adressée :** Y a-t-il des effets de genre ? La popularité des prénoms partagés entre filles et garçons évolue-t-elle de façon cohérente ?

### Aperçu

![Visualisation 3 — Gender Space et graphique miroir](visualisation3.png)

### Démonstration interactive

https://github.com/longhorncow/visualisation_mini_project/raw/visu3/Visualisation3.mp4

> ▶ [Télécharger / visionner la vidéo de démonstration](Visualisation3.mp4)

---

### Description de la visualisation

La visualisation est composée de **deux graphiques liés** :

#### Panneau droit — Gender Space (scatter log-log)

Chaque bulle représente un prénom. Sa position sur les axes log indique sa part parmi les naissances féminines (axe Y) et masculines (axe X) sur la période sélectionnée.

- **Diagonale y = x** : zone « mixte » — popularité identique dans les deux sexes
- **Au-dessus de la diagonale** : prénom plutôt féminin
- **En-dessous** : prénom plutôt masculin
- **Couleur** : année du pic de popularité (palette plasma, 1900 → jaune, 1920 → violet, 2020 → rose)
- **Taille** : nombre total de naissances sur la période

#### Panneau gauche — Graphique miroir

Sélectionner un prénom dans le scatter affiche son évolution temporelle en miroir :

- **Rose (haut)** : part des naissances féminines portant ce prénom
- **Bleu (bas)** : part des naissances masculines (axe inversé)
- L'axe s'adapte automatiquement à la plage d'années sélectionnée

---

### Contrôles interactifs

| Contrôle | Effet |
|----------|-------|
| **Prénom** (champ texte) | Met en évidence les prénoms commençant par les lettres saisies dans le scatter |
| **Année début / fin** (sliders) | Filtre la plage temporelle — scatter et graphique miroir s'adaptent simultanément |
| **Équilibre min** (slider 0 – 0.5) | Part minimale du sexe minoritaire : `0.05` = au moins 5 % de l'autre sexe requis · `0` = tous les prénoms · `0.5` = uniquement 50/50 |
| **Clic sur une bulle** | Affiche l'évolution miroir du prénom sélectionné |

---

### Choix de design

**Pourquoi un scatter log-log ?**  
La popularité des prénoms suit une distribution très asymétrique : quelques prénoms très populaires, une longue traîne de prénoms rares. L'échelle logarithmique permet de voir à la fois les grands prénoms (CAMILLE, ALEX) et les prénoms plus marginaux sans que les premiers écrasent les seconds.

**Pourquoi un graphique miroir (area chart symétrique) ?**  
Superposer les deux courbes sur le même axe rendrait la comparaison difficile pour des prénoms déséquilibrés (ex. CAMILLE : 70 % filles). Le miroir garantit une lecture symétrique et immédiate du rapport filles/garçons.

**Pourquoi lier les deux graphiques par clic ?**  
Le scatter donne une vue globale de l'espace des prénoms mixtes à un instant donné ; le graphique miroir apporte la dimension temporelle pour un prénom spécifique. La liaison par clic évite la surcharge visuelle d'afficher toutes les évolutions simultanément.

**Pourquoi le filtre d'équilibre ?**  
Sans filtre, les prénoms très asymétriques (99 % filles) polluent le scatter et masquent les prénoms véritablement mixtes. Le slider permet de zoomer progressivement sur les prénoms partagés.

---

### Critique de la solution

**Points forts**
- L'interaction scatter → miroir répond directement à la question : on voit en un clic si l'évolution d'un prénom est cohérente entre les deux sexes.
- Le filtre d'équilibre isole efficacement les prénoms mixtes (CAMILLE, CHARLIE, SASHA…).
- Le slider de plage temporelle permet de comparer différentes époques sans recharger.

**Limites**
- Les prénoms absents d'une décennie disparaissent du scatter même s'ils étaient populaires à d'autres périodes — la couleur « année du pic » compense partiellement ce manque.
- L'encodage de la taille des bulles est difficile à calibrer 

---

## Installation et exécution

```bash
# Créer l'environnement (Python 3.12)
uv venv
uv pip install altair pandas

# Activer l'environnement
source .venv/bin/activate

# Générer la visualisation HTML
python visualisation3.py
# → ouvre visualisation3.html dans un navigateur
```

**Ou directement dans le notebook :**

```bash
uv pip install altair pandas jupyter
.venv/bin/jupyter notebook visualisation3.ipynb
```

---

## Structure du dépôt

```
├── Names_hints/
│   ├── dpt2020.csv                          # Données INSEE (prénoms × département × année)
│   ├── departements-version-simplifiee.geojson
│   └── departements-avec-outre-mer.geojson
├── visualisation3.py                        # Script principal — génère visualisation3.html
├── visualisation3.png                       # Capture d'écran
└── Visualisation3.mp4                       # Vidéo de démonstration
```

---

## Données

- **Source** : INSEE — [Fichier des prénoms](https://www.data.gouv.fr/fr/datasets/fichier-des-prenoms-edition-2016/)
- **Période** : 1900 – 2020
- **Granularité** : département × année × sexe × prénom
- **Colonnes** : `sexe` (1 = masculin, 2 = féminin) · `preusuel` · `annais` · `dpt` · `nombre`
- Les prénoms rares (`_PRENOMS_RARES`) et les années inconnues (`XXXX`) sont exclus du traitement.
