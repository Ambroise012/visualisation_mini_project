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

## Visualisation 1 — Évolution temporelle & effets de mode

> **Question adressée :** Comment les prénoms évoluent-ils dans le temps ? Certains sont-ils des phénomènes de mode ?

**Notebook :** [visu1.ipynb](visu1.ipynb)

### Description

Line chart interactif affichant l'évolution des 10 prénoms les plus populaires et des prénoms détectés comme « effets de mode » (pic de popularité marqué, déclin rapide).

| Contrôle | Effet |
|----------|-------|
| **Affichage** (radio) | Bascule entre nombre de naissances et pourcentage annuel |
| **Type** (radio) | Affiche tous les prénoms ou uniquement les effets de mode |
| **Prénom** (liste) | Isole un prénom spécifique |

---

## Visualisation 2 — Répartition géographique par région

> **Question adressée :** Y a-t-il un effet régional ? La popularité d'un prénom varie-t-elle selon les régions ?

**Notebook :** [Visu2.ipynb](Visu2.ipynb)

### Description

Dashboard composé d'une carte choroplèthe de France par région et d'un classement horizontal des régions, mis à jour en temps réel.

| Contrôle | Effet |
|----------|-------|
| **Année** (slider 1900–2020) | Fait évoluer la carte et le classement |
| **Prénom** (liste) | Choisit le prénom à observer |

---

## Visualisation 3 — Gender Space × Évolution miroir

> **Question adressée :** Y a-t-il des effets de genre ? La popularité des prénoms partagés entre filles et garçons évolue-t-elle de façon cohérente ?

**Notebook :** [visu3.ipynb](visu3.ipynb)

### Aperçu

![Visualisation 3 — Gender Space et graphique miroir](visualisation3.png)

### Démonstration interactive

https://github.com/longhorncow/visualisation_mini_project/raw/visu3/Visualisation3.mp4

![Télécharger / visionner la vidéo de démonstration](Visualisation3.mp4)

### Description

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

### Contrôles interactifs

| Contrôle | Effet |
|----------|-------|
| **Prénom** (champ texte) | Met en évidence les prénoms commençant par les lettres saisies dans le scatter |
| **Année début / fin** (sliders) | Filtre la plage temporelle — scatter et graphique miroir s'adaptent simultanément |
| **Équilibre min** (slider 0 – 0.5) | Part minimale du sexe minoritaire : `0.05` = au moins 5 % de l'autre sexe requis · `0` = tous les prénoms · `0.5` = uniquement 50/50 |
| **Clic sur une bulle** | Affiche l'évolution miroir du prénom sélectionné |

---

## Installation et exécution

```bash
# Créer l'environnement (Python 3.12)
uv venv
uv pip install altair pandas geopandas jupyter

# Activer l'environnement
source .venv/bin/activate

# Lancer Jupyter
jupyter notebook
```

Ouvrir ensuite [visu1.ipynb](visu1.ipynb), [Visu2.ipynb](Visu2.ipynb) ou [visu3.ipynb](visu3.ipynb) selon la visualisation souhaitée.

---

## Structure du dépôt

```
├── Names_hints/
│   ├── dpt2020.csv                          # Données INSEE (prénoms × département × année)
│   ├── departements-version-simplifiee.geojson
│   └── departements-avec-outre-mer.geojson
├── visu1.ipynb                              # Visualisation 1 — Évolution temporelle & effets de mode
├── Visu2.ipynb                              # Visualisation 2 — Carte par région
└── visu3.ipynb                              # Visualisation 3 — Gender Space × Évolution miroir
```

---

## Données

- **Source** : INSEE — [Fichier des prénoms](https://www.data.gouv.fr/fr/datasets/fichier-des-prenoms-edition-2016/)
- **Période** : 1900 – 2020
- **Granularité** : département × année × sexe × prénom
- **Colonnes** : `sexe` (1 = masculin, 2 = féminin) · `preusuel` · `annais` · `dpt` · `nombre`
- Les prénoms rares (`_PRENOMS_RARES`) et les années inconnues (`XXXX`) sont exclus du traitement.
