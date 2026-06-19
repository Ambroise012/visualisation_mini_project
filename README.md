# Mini Project — Baby Names in France (1900–2020)

> IGR204 · Télécom Paris
> Dataset: INSEE — First names registered in metropolitan France by department, from 1900 to 2020.

---

## Context and Research Questions

The project aims to answer three main questions through interactive visualizations:

| #     | Research Question                                                                                                                         |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **1** | How do first names evolve over time? Are some names consistently popular while others are short-lived trends?                             |
| **2** | Are there regional effects? Are some names popular only in specific regions? Are the most popular names equally widespread across France? |
| **3** | Are there gender-related effects? Do names given to both boys and girls evolve similarly over time?                                       |

---

## Visualization 1 — Temporal Evolution & Trend Effects

> **Research Question:** How do first names evolve over time? Can some names be identified as temporary trends?

**Notebook:** [visu1.ipynb](visu1.ipynb)

### Preview

![Visualization 1](visu1.png)

### Description

Interactive line chart showing the evolution of the 10 most popular first names and names identified as **trend-driven names** (sharp popularity peak followed by a rapid decline).

| Control                          | Effect                                                |
| -------------------------------- | ----------------------------------------------------- |
| **Display Mode** (radio buttons) | Switch between number of births and annual percentage |
| **Type** (radio buttons)         | Display all names or only trend-driven names          |
| **First Name** (dropdown list)   | Isolate a specific name                               |

---

## Visualization 2 — Geographic Distribution by Region

> **Research Question:** Are there regional effects? Does the popularity of a name vary across regions?

**Notebook:** [Visu2.ipynb](Visu2.ipynb)

### Preview

![Visualization 2](visu2.png)

### Description

Dashboard combining a choropleth map of France by region and a horizontal ranking of regions, updated in real time.

| Control                        | Effect                           |
| ------------------------------ | -------------------------------- |
| **Year** (slider 1900–2020)    | Updates both the map and ranking |
| **First Name** (dropdown list) | Select the name to explore       |

---

## Visualization 3 — Gender Space × Mirrored Evolution

> **Research Question:** Are there gender effects? Do names shared by girls and boys evolve similarly over time?

**Notebook:** [visu3.ipynb](visu3.ipynb)

### Preview

![Visualization 3 — Gender Space and mirrored chart](visualisation3.png)

### Interactive Demonstration

> ▶ [Download / watch the demonstration video](Visualisation3.mp4)

### Description

The visualization consists of **two linked charts**:

#### Right Panel — Gender Space (log-log scatter plot)

Each bubble represents a first name. Its position on the logarithmic axes indicates its share among female births (Y-axis) and male births (X-axis) during the selected period.

* **Diagonal y = x**: balanced names — equally popular among both sexes
* **Above the diagonal**: predominantly female names
* **Below the diagonal**: predominantly male names
* **Color**: year of peak popularity (Plasma color scale, 1900 → yellow, 2020 → pink)
* **Size**: total number of births during the selected period

#### Left Panel — Mirrored Evolution Chart

Selecting a name in the scatter plot displays its temporal evolution:

* **Pink (top)**: share of female births with that name
* **Blue (bottom)**: share of male births with that name (inverted axis)
* The chart automatically adapts to the selected year range

### How it answers the research question

The visualisation answers the question in two complementary steps:

**1 — Gender Space scatter: snapshot of asymmetry**
A name whose popularity evolves *consistently* across sexes would stay near the diagonal y = x regardless of the year range. In practice almost every bubble drifts away from it — gender effects exist.

**2 — Mirror chart: temporal consistency**
Clicking a name and sliding the year range reveals whether the girls/boys ratio has been stable over time:

| Name | What the mirror shows | Interpretation |
|------|-----------------------|----------------|
| **CAMILLE** | Female area swells from the 1970s; male area nearly flat | Popularity rose sharply for girls but not boys — **inconsistent** evolution |
| **ALEX** | Near-symmetric mirror, stable across the century | Similar popularity in both sexes — **consistent** evolution |
| **DOMINIQUE** | Male-dominant before ~1970, female-dominant after | A full "side switch" — gender effect present *and* reversed over time |

**3 — Sliders as epoch comparison**
Restricting the range to 1950–1970 then 1990–2010 on the same name shows whether an imbalance is recent or historical.

> **Note:** the visualisation shows temporal correlation, not causation. The INSEE sex = 1 / 2 categories are a binary simplification that does not reflect the full spectrum of gender identities.

### Interactive Controls

| Control                             | Effect                                                                                                                                |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Name** (text field)               | Highlights names starting with the entered letters in the scatter plot                                                                |
| **Start Year / End Year** (sliders) | Filters the time range; both charts update simultaneously                                                                             |
| **Min. balance** (slider 0–0.5)     | Minimum share of the minority sex: `0.05` = at least 5% · `0` = all names · `0.5` = 50/50 only |
| **Click on a bubble**               | Displays the mirrored evolution of the selected name                                                                                  |

### Design choices

**Why a log-log scatter?**
Name popularity follows a highly skewed distribution. The logarithmic scale makes both very popular names (CAMILLE, ALEX) and rarer ones visible without the former overwhelming the latter.

**Why a mirrored area chart?**
Overlaying two lines on the same axis makes comparison difficult for asymmetric names (e.g. CAMILLE: 70% female). The mirror guarantees a symmetric, immediate reading of the female/male ratio.

**Why link the two charts by click?**
The scatter gives a global view of the mixed-name space at a given moment; the mirror chart adds the temporal dimension for a specific name. Linking by click avoids the visual overload of showing all evolutions simultaneously.

**Why the balance filter?**
Without filtering, highly asymmetric names (99% female) crowd the scatter and hide truly mixed names. The slider lets users zoom progressively onto shared names.

---

## Installation and Execution

```bash
# Create the environment (Python 3.12)
uv venv
uv pip install altair pandas geopandas jupyter

# Activate the environment
source .venv/bin/activate

# Launch Jupyter
jupyter notebook
```

Then open either [visu1.ipynb](visu1.ipynb), [Visu2.ipynb](Visu2.ipynb), or [visu3.ipynb](visu3.ipynb) depending on the visualization you want to explore.

---

## Repository Structure

```text
├── Names_hints/
│   ├── dpt2020.csv                          # INSEE dataset (first name × department × year)
│   ├── departements-version-simplifiee.geojson
│   └── departements-avec-outre-mer.geojson
├── visu1.ipynb                              # Visualization 1 — Temporal evolution & trend effects
├── Visu2.ipynb                              # Visualization 2 — Regional map
├── visu3.ipynb                              # Visualization 3 — Gender Space × Mirrored evolution
├── visualisation3.html                      # Interactive HTML export (visu 3)
├── visualisation3.png                       # Screenshot (visu 3)
└── Visualisation3.mp4                       # Demonstration video (visu 3)
```

---

## Dataset

* **Source:** INSEE — [French First Names Dataset](https://www.data.gouv.fr/fr/datasets/fichier-des-prenoms-edition-2016/)
* **Period:** 1900–2020
* **Granularity:** department × year × sex × first name
* **Columns:** `sexe` (1 = male, 2 = female), `preusuel`, `annais`, `dpt`, `nombre`
* Rare names (`_PRENOMS_RARES`) and unknown years (`XXXX`) are excluded from the analysis.
