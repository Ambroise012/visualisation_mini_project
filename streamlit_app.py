"""
Mini Project — Baby Names in France (1900–2020)
Application Streamlit regroupant les 3 visualisations du projet.

    streamlit run streamlit_app.py

Les trois onglets reprennent fidèlement les notebooks `visu1.ipynb`,
`Visu2.ipynb` et `visu3.ipynb` de la branche `main`.
"""

import json
from pathlib import Path
from urllib.request import urlopen

import altair as alt
import pandas as pd
import streamlit as st

alt.data_transformers.disable_max_rows()

BASE_DIR = Path(__file__).parent
HINTS_DIR = BASE_DIR / "Names_hints"
CSV_PATH = HINTS_DIR / "dpt2020.csv"
GEO_REG_PATH = HINTS_DIR / "regions_fr.geojson"
GEO_DEPT_PATH = HINTS_DIR / "departements-version-simplifiee.geojson"

REG_GEOJSON_URL = "https://france-geojson.gregoiredavid.fr/repo/regions.geojson"


# ──────────────────────────────────────────────────────────────────────────────
# Chargement des données (mis en cache)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_names() -> pd.DataFrame:
    """Charge et nettoie le fichier des prénoms par département (1900–2020)."""
    names = pd.read_csv(CSV_PATH, sep=";")
    names = names[names.preusuel != "_PRENOMS_RARES"]
    names = names[names.dpt != "XX"]
    names["annais"] = pd.to_numeric(names["annais"], errors="coerce")
    names = names.dropna(subset=["annais"])
    names["annais"] = names["annais"].astype(int)
    names = names[names["annais"].between(1900, 2020)]
    return names


@st.cache_data
def load_geojson(path_str: str, url: str | None = None) -> dict:
    """Charge un GeoJSON local (téléchargé et mis en cache si absent)."""
    path = Path(path_str)
    if path.exists() and path.stat().st_size > 200:
        with path.open("rb") as f:
            if f.read(1) != b"\x89":  # pas un PNG mal nommé
                with path.open("r", encoding="utf-8") as fh:
                    return json.load(fh)
    if url is None:
        raise FileNotFoundError(path)
    with urlopen(url) as r:
        geo = json.loads(r.read().decode("utf-8"))
    with path.open("w", encoding="utf-8") as f:
        json.dump(geo, f, ensure_ascii=False)
    return geo


# Département → région administrative (métropole) — utilisé par la visu 2
DEPT_TO_REG = {
    "75": "Île-de-France", "77": "Île-de-France", "78": "Île-de-France",
    "91": "Île-de-France", "92": "Île-de-France", "93": "Île-de-France",
    "94": "Île-de-France", "95": "Île-de-France",
    "18": "Centre-Val de Loire", "28": "Centre-Val de Loire", "36": "Centre-Val de Loire",
    "37": "Centre-Val de Loire", "41": "Centre-Val de Loire", "45": "Centre-Val de Loire",
    "21": "Bourgogne-Franche-Comté", "25": "Bourgogne-Franche-Comté", "39": "Bourgogne-Franche-Comté",
    "58": "Bourgogne-Franche-Comté", "70": "Bourgogne-Franche-Comté", "71": "Bourgogne-Franche-Comté",
    "89": "Bourgogne-Franche-Comté", "90": "Bourgogne-Franche-Comté",
    "14": "Normandie", "27": "Normandie", "50": "Normandie", "61": "Normandie", "76": "Normandie",
    "02": "Hauts-de-France", "59": "Hauts-de-France", "60": "Hauts-de-France",
    "62": "Hauts-de-France", "80": "Hauts-de-France",
    "08": "Grand Est", "10": "Grand Est", "51": "Grand Est", "52": "Grand Est", "54": "Grand Est",
    "55": "Grand Est", "57": "Grand Est", "67": "Grand Est", "68": "Grand Est", "88": "Grand Est",
    "44": "Pays de la Loire", "49": "Pays de la Loire", "53": "Pays de la Loire",
    "72": "Pays de la Loire", "85": "Pays de la Loire",
    "22": "Bretagne", "29": "Bretagne", "35": "Bretagne", "56": "Bretagne",
    "16": "Nouvelle-Aquitaine", "17": "Nouvelle-Aquitaine", "19": "Nouvelle-Aquitaine",
    "23": "Nouvelle-Aquitaine", "24": "Nouvelle-Aquitaine", "33": "Nouvelle-Aquitaine",
    "40": "Nouvelle-Aquitaine", "47": "Nouvelle-Aquitaine", "64": "Nouvelle-Aquitaine",
    "79": "Nouvelle-Aquitaine", "86": "Nouvelle-Aquitaine", "87": "Nouvelle-Aquitaine",
    "09": "Occitanie", "11": "Occitanie", "12": "Occitanie", "30": "Occitanie", "31": "Occitanie",
    "32": "Occitanie", "34": "Occitanie", "46": "Occitanie", "48": "Occitanie", "65": "Occitanie",
    "66": "Occitanie", "81": "Occitanie", "82": "Occitanie",
    "01": "Auvergne-Rhône-Alpes", "03": "Auvergne-Rhône-Alpes", "07": "Auvergne-Rhône-Alpes",
    "15": "Auvergne-Rhône-Alpes", "26": "Auvergne-Rhône-Alpes", "38": "Auvergne-Rhône-Alpes",
    "42": "Auvergne-Rhône-Alpes", "43": "Auvergne-Rhône-Alpes", "63": "Auvergne-Rhône-Alpes",
    "69": "Auvergne-Rhône-Alpes", "73": "Auvergne-Rhône-Alpes", "74": "Auvergne-Rhône-Alpes",
    "04": "Provence-Alpes-Côte d'Azur", "05": "Provence-Alpes-Côte d'Azur",
    "06": "Provence-Alpes-Côte d'Azur", "13": "Provence-Alpes-Côte d'Azur",
    "83": "Provence-Alpes-Côte d'Azur", "84": "Provence-Alpes-Côte d'Azur",
    "2A": "Corse", "2B": "Corse",
}

# Département → région « culturelle » historique — utilisé par la carte de la visu 3
DEPT_TO_REGION = {
    "22": "Bretagne", "29": "Bretagne", "35": "Bretagne", "56": "Bretagne",
    "14": "Normandie", "27": "Normandie", "50": "Normandie", "61": "Normandie", "76": "Normandie",
    "59": "Nord & Flandre", "62": "Nord & Flandre",
    "02": "Picardie", "60": "Picardie", "80": "Picardie",
    "08": "Champagne", "10": "Champagne", "51": "Champagne", "52": "Champagne",
    "54": "Lorraine", "55": "Lorraine", "57": "Lorraine", "88": "Lorraine",
    "67": "Alsace", "68": "Alsace",
    "25": "Franche-Comté", "39": "Franche-Comté", "70": "Franche-Comté", "90": "Franche-Comté",
    "21": "Bourgogne", "58": "Bourgogne", "71": "Bourgogne", "89": "Bourgogne",
    "75": "Île-de-France", "77": "Île-de-France", "78": "Île-de-France",
    "91": "Île-de-France", "92": "Île-de-France", "93": "Île-de-France",
    "94": "Île-de-France", "95": "Île-de-France",
    "18": "Centre", "28": "Centre", "36": "Centre", "37": "Centre", "41": "Centre", "45": "Centre",
    "44": "Pays de Loire", "49": "Pays de Loire", "53": "Pays de Loire",
    "72": "Pays de Loire", "85": "Pays de Loire",
    "16": "Poitou-Charentes", "17": "Poitou-Charentes", "79": "Poitou-Charentes", "86": "Poitou-Charentes",
    "19": "Limousin", "23": "Limousin", "87": "Limousin",
    "03": "Auvergne", "15": "Auvergne", "43": "Auvergne", "63": "Auvergne",
    "01": "Lyonnais", "07": "Lyonnais", "42": "Lyonnais", "69": "Lyonnais",
    "26": "Dauphiné", "38": "Dauphiné",
    "73": "Savoie", "74": "Savoie",
    "04": "Provence", "05": "Provence", "06": "Provence", "13": "Provence", "83": "Provence", "84": "Provence",
    "11": "Languedoc", "30": "Languedoc", "34": "Languedoc", "48": "Languedoc",
    "66": "Pays Catalans",
    "09": "Midi-Pyrénées", "12": "Midi-Pyrénées", "31": "Midi-Pyrénées", "32": "Midi-Pyrénées",
    "46": "Midi-Pyrénées", "65": "Midi-Pyrénées", "81": "Midi-Pyrénées", "82": "Midi-Pyrénées",
    "64": "Pays Basque & Béarn",
    "24": "Guyenne", "33": "Guyenne", "40": "Guyenne", "47": "Guyenne",
    "2A": "Corse", "2B": "Corse",
}


# ──────────────────────────────────────────────────────────────────────────────
# Visualisation 1 — Évolution temporelle & lectures multiples
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def prep_visu1(names: pd.DataFrame):
    """Calcule les catégories d'analyse et la table temporelle de la visu 1."""
    MIN_TOTAL = 1000
    TOP_N = 6

    all_names = names.groupby(["annais", "preusuel"], as_index=False)["nombre"].sum()

    trend_scores, growth_scores, decline_scores, stability_scores = [], [], [], []
    for first_name, g in all_names.groupby("preusuel"):
        total = g["nombre"].sum()
        if total < MIN_TOTAL:
            continue
        g = g.sort_values("annais").reset_index(drop=True)
        peak_pos = g["nombre"].idxmax()

        if 5 <= peak_pos <= len(g) - 6:
            peak = g.loc[peak_pos, "nombre"]
            before = g.loc[: peak_pos - 1, "nombre"]
            after = g.loc[peak_pos + 1 :, "nombre"]
            peak_width = (g["nombre"] >= 0.5 * peak).sum()
            trend_scores.append({
                "preusuel": first_name,
                "score": (peak / (before.mean() + 1)) * (peak / (after.mean() + 1)) / peak_width,
            })

        early_period = g[g["annais"].between(1950, 1980)]
        late_period = g[g["annais"] >= 2010]
        if len(early_period) and len(late_period):
            early = early_period["nombre"].mean()
            late = late_period["nombre"].mean()
            growth_scores.append({"preusuel": first_name, "score": late / (early + 1)})
            decline_scores.append({"preusuel": first_name, "score": early / (late + 1)})

        mean_val = g["nombre"].mean()
        if mean_val > 0:
            stability_scores.append(
                {"preusuel": first_name, "score": g["nombre"].std() / mean_val}
            )

    def top(scores, ascending=False):
        return (
            pd.DataFrame(scores)
            .sort_values("score", ascending=ascending)
            .head(TOP_N)["preusuel"]
            .tolist()
        )

    trend_names = top(trend_scores)
    growing_names = top(growth_scores)
    declining_names = top(decline_scores)
    stable_names = top(stability_scores, ascending=True)
    historical_names = names.groupby("preusuel")["nombre"].sum().nlargest(TOP_N).index.tolist()

    event_related = [n for n in ["ZINEDINE", "KYLIAN", "SIMONE", "DIANA", "CHARLES"]
                     if n in set(names["preusuel"].unique())]

    category_sets = {
        "Historical leaders": historical_names,
        "Trend-driven": trend_names,
        "Growing": growing_names,
        "Declining": declining_names,
        "Stable": stable_names,
        "Event-related": event_related,
    }
    displayed_names = sorted(set().union(*category_sets.values()))

    base_time_data = (
        names[names["preusuel"].isin(displayed_names)]
        .groupby(["annais", "preusuel"], as_index=False)["nombre"].sum()
    )
    year_totals = (
        names.groupby("annais", as_index=False)["nombre"].sum()
        .rename(columns={"nombre": "year_total"})
    )
    base_time_data = base_time_data.merge(year_totals, on="annais")
    base_time_data["percentage"] = 100 * base_time_data["nombre"] / base_time_data["year_total"]

    frames = []
    for category, selected in category_sets.items():
        sub = base_time_data[base_time_data["preusuel"].isin(selected)].copy()
        sub["analysis_category"] = category
        frames.append(sub)
    time_data = pd.concat(frames, ignore_index=True)

    periods = pd.DataFrame(
        [(1914, 1918, "WWI"), (1939, 1945, "WWII"), (1946, 1973, "Baby Boom"),
         (1968, 1968, "May 68"), (1998, 1998, "World Cup")],
        columns=["start", "end", "period"],
    )
    events = pd.DataFrame(
        [(1914, "WWI"), (1918, "Armistice"), (1939, "WWII"),
         (1945, "Liberation"), (1968, "May 68"), (1998, "World Cup")],
        columns=["year", "event"],
    )
    return time_data, periods, events, displayed_names, list(category_sets.keys())


def build_visu1(names: pd.DataFrame) -> alt.LayerChart:
    time_data, periods, events, displayed_names, categories = prep_visu1(names)

    analysis_mode = alt.param(
        name="AnalysisMode", value="Historical leaders",
        bind=alt.binding_radio(options=categories, name="Question : "),
    )
    display_mode = alt.param(
        name="DisplayMode", value="Count",
        bind=alt.binding_radio(options=["Count", "Percentage"], name="Affichage : "),
    )
    selected_name = alt.param(
        name="SelectedName", value="All",
        bind=alt.binding_select(options=["All"] + displayed_names, name="Prénom : "),
    )

    def filtered(chart):
        return (
            chart.transform_filter("datum.analysis_category == AnalysisMode")
            .transform_filter("(SelectedName == 'All') || (datum.preusuel == SelectedName)")
            .transform_calculate(
                value="DisplayMode == 'Count' ? datum.nombre : datum.percentage"
            )
        )

    # Échelle X partagée : zero=False est indispensable, sinon les couches sœurs
    # (quantitatives) forcent l'inclusion de 0 et compriment 1900–2020 à droite.
    xscale = alt.Scale(domain=[1900, 2022], zero=False)
    xaxis = alt.Axis(values=list(range(1900, 2021, 20)), labelAngle=0, format="d")

    period_bands = (
        alt.Chart(periods).mark_rect(opacity=0.12)
        .encode(x=alt.X("start:Q", scale=xscale), x2="end:Q",
                color=alt.Color("period:N", legend=None))
    )
    event_lines = (
        alt.Chart(events)
        .mark_rule(color="#8B0000", strokeDash=[6, 4], opacity=0.5)
        .encode(x=alt.X("year:Q", scale=xscale))
    )
    event_labels = (
        alt.Chart(events)
        .mark_text(align="left", baseline="top", dx=4, fontSize=11, color="#8B0000")
        .encode(x=alt.X("year:Q", scale=xscale), y=alt.value(5), text="event:N")
    )

    main_chart = filtered(
        alt.Chart(time_data).mark_line(interpolate="monotone", strokeWidth=3).encode(
            x=alt.X("annais:Q", title="Année", scale=xscale, axis=xaxis),
            y=alt.Y("value:Q", title="Naissances / Part (%)"),
            color=alt.Color("preusuel:N", title="Prénom", scale=alt.Scale(scheme="tableau20")),
            tooltip=[
                alt.Tooltip("preusuel:N", title="Prénom"),
                alt.Tooltip("annais:Q", title="Année"),
                alt.Tooltip("nombre:Q", title="Naissances", format=","),
                alt.Tooltip("percentage:Q", title="Part (%)", format=".3f"),
                alt.Tooltip("analysis_category:N", title="Question"),
            ],
        )
    )
    points = filtered(
        alt.Chart(time_data).mark_circle(size=25, opacity=0.5)
        .encode(x=alt.X("annais:Q", scale=xscale), y="value:Q", color="preusuel:N")
    )

    return (
        alt.layer(period_bands, event_lines, main_chart, points, event_labels)
        .add_params(analysis_mode, display_mode, selected_name)
        .properties(
            width=1100, height=620,
            title=alt.TitleParams(
                "Évolution des prénoms français (1900–2020)",
                subtitle="Leaders historiques, tendances, croissance, déclin, stabilité, événements",
            ),
        )
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#ECECEC", labelFontSize=12, titleFontSize=14)
        .configure_title(fontSize=22, subtitleFontSize=13, anchor="start")
        .interactive()
    )


# ──────────────────────────────────────────────────────────────────────────────
# Visualisation 2 — Écart régional à la moyenne nationale (carte sans flash)
# ──────────────────────────────────────────────────────────────────────────────
NOMS_CARTE = ["ENORA", "ENZO", "CAMILLE", "EMMA", "KEVIN", "JEAN", "MARIE", "LEA"]


@st.cache_data
def prep_visu2(names: pd.DataFrame):
    """Calcule les indices régionaux et départementaux pour la visu 2."""
    df = names.rename(columns={"annais": "annee"}).copy()
    df["region"] = df["dpt"].map(DEPT_TO_REG)

    df_region_totals = (
        df.dropna(subset=["region"])
        .groupby(["annee", "region"], as_index=False)["nombre"].sum()
        .rename(columns={"nombre": "total_region"})
    )
    df_name_region = (
        df.dropna(subset=["region"])
        .pipe(lambda d: d[d["preusuel"].isin(NOMS_CARTE)])
        .groupby(["preusuel", "annee", "region"], as_index=False)["nombre"].sum()
    )
    df_name_national = (
        df[df["preusuel"].isin(NOMS_CARTE)]
        .groupby(["preusuel", "annee"], as_index=False)["nombre"].sum()
        .rename(columns={"nombre": "nombre_national"})
    )
    df_france_totals = (
        df.groupby(["annee"], as_index=False)["nombre"].sum()
        .rename(columns={"nombre": "total_france"})
    )

    # Toutes les régions × tous les prénoms × toutes les années (pour des couleurs stables)
    base_names = pd.DataFrame({"preusuel": NOMS_CARTE})
    df_base = (
        df_region_totals.assign(_k=1)
        .merge(base_names.assign(_k=1), on="_k").drop(columns="_k")
    )
    df_reg = (
        df_base
        .merge(df_name_region, on=["preusuel", "annee", "region"], how="left")
        .merge(df_name_national, on=["preusuel", "annee"], how="left")
        .merge(df_france_totals, on=["annee"], how="left")
    )
    df_reg["nombre"] = df_reg["nombre"].fillna(0)
    df_reg["nombre_national"] = df_reg["nombre_national"].fillna(0)
    df_reg["part_naissances"] = df_reg["nombre"] / df_reg["total_region"]
    df_reg["part_nationale"] = df_reg["nombre_national"] / df_reg["total_france"]
    df_reg["indice_regional"] = df_reg["part_naissances"] / df_reg["part_nationale"]
    df_reg.loc[df_reg["part_nationale"] <= 0, "indice_regional"] = pd.NA
    df_reg["key"] = (
        df_reg["region"] + "_" + df_reg["annee"].astype(str) + "_" + df_reg["preusuel"]
    )

    df_dept_totals = (
        df.dropna(subset=["region"])
        .groupby(["annee", "region", "dpt"], as_index=False)["nombre"].sum()
        .rename(columns={"nombre": "total_dept"})
    )
    df_name_dept = (
        df.dropna(subset=["region"])
        .pipe(lambda d: d[d["preusuel"].isin(NOMS_CARTE)])
        .groupby(["preusuel", "annee", "region", "dpt"], as_index=False)["nombre"].sum()
    )
    df_dept = (
        df_name_dept
        .merge(df_dept_totals, on=["annee", "region", "dpt"], how="left")
        .merge(df_name_national, on=["preusuel", "annee"], how="left")
        .merge(df_france_totals, on=["annee"], how="left")
    )
    df_dept["part_dept"] = df_dept["nombre"] / df_dept["total_dept"]
    df_dept["part_nationale"] = df_dept["nombre_national"] / df_dept["total_france"]
    df_dept["indice_dept"] = df_dept["part_dept"] / df_dept["part_nationale"]
    df_dept.loc[df_dept["part_nationale"] <= 0, "indice_dept"] = pd.NA

    # Allège la taille du spec Vega embarqué : ne garde que les colonnes utiles
    # et arrondit les flottants (sinon ~15 Mo de JSON inliné côté navigateur).
    df_reg = df_reg[["key", "region", "annee", "preusuel", "nombre",
                     "part_naissances", "part_nationale", "indice_regional"]].copy()
    df_dept = df_dept[["preusuel", "annee", "region", "dpt", "nombre",
                       "part_dept", "part_nationale", "indice_dept"]].copy()
    for col in ["part_naissances", "part_nationale"]:
        df_reg[col] = df_reg[col].round(5)
    df_reg["indice_regional"] = df_reg["indice_regional"].round(3)
    for col in ["part_dept", "part_nationale"]:
        df_dept[col] = df_dept[col].round(5)
    df_dept["indice_dept"] = df_dept["indice_dept"].round(3)
    return df_reg, df_dept


def build_visu2(names: pd.DataFrame, geo_reg: dict) -> alt.VConcatChart:
    df_reg, df_dept = prep_visu2(names)

    # Ne garder que la métropole : les régions d'outre-mer (Guyane, Réunion…)
    # élargissent l'emprise de la projection et réduisent la France à un point.
    metro = set(DEPT_TO_REG.values())
    geo_reg = {
        "type": "FeatureCollection",
        "features": [f for f in geo_reg["features"] if f["properties"]["nom"] in metro],
    }

    p_annee = alt.param(
        name="Annee", value=2000,
        bind=alt.binding_range(min=1900, max=2020, step=1, name="Année  "),
    )
    p_prenom = alt.param(
        name="PrenoMCarte", value="ENZO",
        bind=alt.binding_select(
            options=sorted(df_reg["preusuel"].unique().tolist()), name="Prénom  "
        ),
    )
    region_click = alt.selection_point(
        fields=["region"], on="click", clear="dblclick", empty=False
    )

    geo_src = alt.Data(
        values=geo_reg, format=alt.DataFormat(type="json", property="features")
    )

    # Échelle de couleur FIXE (domaine [0, 2], milieu = 1) + couche de fond statique :
    # la silhouette des régions ne disparaît jamais et l'échelle ne se recalcule pas,
    # ce qui supprime le « flash » de re-rendu complet à chaque changement d'année.
    color_scale = alt.Scale(scheme="blueorange", domain=[0, 2], domainMid=1, clamp=True)

    base_map = (
        alt.Chart(geo_src)
        .mark_geoshape(fill="#eef2f7", stroke="white", strokeWidth=0.8)
    )
    choro = (
        alt.Chart(geo_src)
        .transform_calculate(region="datum.properties.nom")
        .transform_calculate(key="datum.region + '_' + toString(Annee) + '_' + PrenoMCarte")
        .transform_lookup(
            lookup="key",
            from_=alt.LookupData(
                df_reg[["key", "nombre", "part_naissances",
                        "part_nationale", "indice_regional"]],
                "key",
                ["nombre", "part_naissances", "part_nationale", "indice_regional"],
            ),
        )
        .mark_geoshape(stroke="white", strokeWidth=0.8)
        .encode(
            color=alt.Color(
                "indice_regional:Q", title="Indice régional / national",
                scale=color_scale, legend=alt.Legend(format=".2f"),
            ),
            opacity=alt.condition(region_click, alt.value(1.0), alt.value(0.85)),
            tooltip=[
                alt.Tooltip("region:N", title="Région"),
                alt.Tooltip("nombre:Q", title="Naissances régionales", format=","),
                alt.Tooltip("part_naissances:Q", title="Part régionale", format=".1%"),
                alt.Tooltip("part_nationale:Q", title="Part nationale", format=".1%"),
                alt.Tooltip("indice_regional:Q", title="Indice", format=".2f"),
            ],
        )
        .add_params(region_click)
    )
    carte = (
        (base_map + choro)
        .project("mercator")
        .properties(width=560, height=460, title="Effet régional du prénom")
    )

    ranking_bars = (
        alt.Chart(df_reg[["region", "annee", "preusuel",
                          "indice_regional", "nombre", "part_naissances"]])
        .transform_filter("datum.preusuel == PrenoMCarte && datum.annee == Annee")
        .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
        .encode(
            y=alt.Y("region:N", sort="-x", title=None),
            x=alt.X("indice_regional:Q", title="Indice régional"),
            color=alt.Color("indice_regional:Q", scale=color_scale, legend=None),
            tooltip=[
                alt.Tooltip("region:N", title="Région"),
                alt.Tooltip("nombre:Q", title="Naissances régionales", format=","),
                alt.Tooltip("part_naissances:Q", title="Part régionale", format=".1%"),
                alt.Tooltip("indice_regional:Q", title="Indice", format=".2f"),
            ],
        )
    )
    neutral_line = (
        alt.Chart(pd.DataFrame({"x": [1]}))
        .mark_rule(color="#333333", strokeDash=[5, 3], strokeWidth=1.2).encode(x="x:Q")
    )
    ranking = (neutral_line + ranking_bars).properties(
        width=560, height=310, title="Classement des régions"
    )

    dept_detail = (
        alt.Chart(df_dept[["preusuel", "annee", "region", "dpt",
                           "nombre", "part_dept", "indice_dept"]])
        .transform_filter("datum.preusuel == PrenoMCarte && datum.annee == Annee")
        .transform_filter(region_click)
        .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
        .encode(
            y=alt.Y("dpt:N", sort="-x", title="Département"),
            x=alt.X("indice_dept:Q", title="Indice départemental"),
            color=alt.Color("indice_dept:Q", scale=color_scale, legend=None),
            tooltip=[
                alt.Tooltip("region:N", title="Région"),
                alt.Tooltip("dpt:N", title="Département"),
                alt.Tooltip("nombre:Q", title="Naissances", format=","),
                alt.Tooltip("part_dept:Q", title="Part départementale", format=".1%"),
                alt.Tooltip("indice_dept:Q", title="Indice", format=".2f"),
            ],
        )
        .properties(width=560, height=260,
                    title="Détail par département (cliquez une région sur la carte)")
    )

    return (
        alt.vconcat(carte, ranking, dept_detail)
        .add_params(p_annee, p_prenom)
        .resolve_scale(color="independent")
        .properties(
            title=alt.TitleParams(
                "Écart à la moyenne nationale des prénoms par région — 1900 à 2020",
                fontSize=15, anchor="start",
            )
        )
    )


# ──────────────────────────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────
# Visualisation 3 — Gender Space × évolution miroir × carte par région
#
# Pilotée par des widgets Streamlit (prénom, plage d'années, équilibre) : les
# données sont filtrées en Python AVANT d'être envoyées à Vega, ce qui garde le
# spec minuscule (le pilotage 100 % Vega inlinait ~1,9 M de lignes → 230 Mo).
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def prep_visu3(names: pd.DataFrame):
    total_yr_sex = (
        names.groupby(["annais", "sexe"])["nombre"].sum().reset_index(name="total_nais")
    )
    scat_yr = (
        names.groupby(["preusuel", "annais", "sexe"])["nombre"].sum().reset_index()
        .merge(total_yr_sex, on=["annais", "sexe"])
    )
    girls_yr = (
        scat_yr[scat_yr.sexe == 2][["preusuel", "annais", "nombre", "total_nais"]]
        .rename(columns={"nombre": "nb_f", "total_nais": "tot_f"})
    )
    boys_yr = (
        scat_yr[scat_yr.sexe == 1][["preusuel", "annais", "nombre", "total_nais"]]
        .rename(columns={"nombre": "nb_m", "total_nais": "tot_m"})
    )
    scat_wide = girls_yr.merge(boys_yr, on=["preusuel", "annais"], how="outer").fillna(0)

    name_totals = scat_wide.groupby("preusuel")[["nb_f", "nb_m"]].sum()
    popular = name_totals[
        (name_totals.nb_f > 0) & (name_totals.nb_m > 0)
        & (name_totals.nb_f + name_totals.nb_m >= 1000)
    ].index
    scat_wide = scat_wide[scat_wide.preusuel.isin(popular)].copy()

    peak = (
        names.groupby(["preusuel", "annais"])["nombre"].sum().reset_index()
        .sort_values("nombre", ascending=False).drop_duplicates("preusuel")
        [["preusuel", "annais"]].rename(columns={"annais": "peak_year"})
    )
    scat_wide = scat_wide.merge(peak, on="preusuel", how="left")

    # Région « culturelle » dominante de chaque prénom (pour le tooltip du scatter)
    dn = names[names.preusuel.isin(popular)].groupby(["preusuel", "dpt"])["nombre"].sum().reset_index()
    dn["region_cult"] = dn["dpt"].map(DEPT_TO_REGION)
    dn = dn.dropna(subset=["region_cult"])
    rg = dn.groupby(["preusuel", "region_cult"])["nombre"].sum().reset_index()
    rg = rg.merge(dn.groupby("preusuel")["nombre"].sum().reset_index(name="_tot"), on="preusuel")
    rg["_share"] = rg["nombre"] / rg["_tot"]
    top_region = (
        rg.sort_values("_share", ascending=False).drop_duplicates("preusuel")
        [["preusuel", "region_cult"]]
    )
    scat_wide = scat_wide.merge(top_region, on="preusuel", how="left")

    # Comptes filles/garçons par prénom × région × année (niveau région : léger)
    region_gender = (
        names[names.preusuel.isin(popular)]
        .assign(region_cult=lambda d: d["dpt"].map(DEPT_TO_REGION))
        .dropna(subset=["region_cult"])
        .pivot_table(index=["preusuel", "region_cult", "annais"], columns="sexe",
                     values="nombre", aggfunc="sum", fill_value=0)
        .rename(columns={1: "nb_m", 2: "nb_f"}).reset_index()
    )
    for col in ("nb_f", "nb_m"):
        if col not in region_gender:
            region_gender[col] = 0

    total_yr = (
        names.groupby(["annais", "sexe"])["nombre"].sum().reset_index(name="total_nais")
    )
    ts = (
        names[names.preusuel.isin(popular)]
        .groupby(["preusuel", "annais", "sexe"])["nombre"].sum().reset_index()
        .merge(total_yr, on=["annais", "sexe"])
    )
    ts["pct"] = ts["nombre"] / ts["total_nais"]
    ts["pct_signed"] = ts.apply(lambda r: -r["pct"] if r["sexe"] == 1 else r["pct"], axis=1)

    dept_lookup = pd.DataFrame(list(DEPT_TO_REGION.items()), columns=["dpt", "region_cult"])
    return scat_wide, ts, region_gender, dept_lookup, sorted(popular)


def build_visu3(prep, focus: str, y0: int, y1: int, balance: float,
                geo_dept: dict) -> alt.HConcatChart:
    scat_wide, ts, region_gender, dept_lookup, _ = prep
    DMIN, DMAX = 3e-5, 0.12

    # ── Scatter (agrégé en Python sur la fenêtre d'années) ───────────────────
    sw = scat_wide[scat_wide.annais.between(y0, y1)]
    g = (
        sw.groupby("preusuel")
        .agg(nb_f=("nb_f", "sum"), nb_m=("nb_m", "sum"),
             tot_f=("tot_f", "sum"), tot_m=("tot_m", "sum"),
             peak_year=("peak_year", "max"), region_cult=("region_cult", "max"))
        .reset_index()
    )
    g["total"] = g.nb_f + g.nb_m
    g = g[(g.nb_f > 0) & (g.nb_m > 0) & (g.total >= 100)]
    g["pct_f"] = (g.nb_f / g.tot_f).round(6)
    g["pct_m"] = (g.nb_m / g.tot_m).round(6)
    g["ratio_f"] = g.nb_f / g.total
    g = g[(g.ratio_f >= balance) & (g.ratio_f <= 1 - balance)].copy()
    g["is_focus"] = g.preusuel == focus

    diag = (
        alt.Chart(pd.DataFrame({"x": [DMIN, DMAX], "y": [DMIN, DMAX]}))
        .mark_line(color="#bbb", strokeDash=[5, 5], size=1.5)
        .encode(x=alt.X("x:Q", scale=alt.Scale(type="log")),
                y=alt.Y("y:Q", scale=alt.Scale(type="log")))
    )
    zone_labels = (
        alt.Chart(pd.DataFrame({
            "x": [0.07, 0.0004, 0.07], "y": [0.07, 0.07, 0.0004],
            "label": ["Mixte", "Plutôt\nféminin", "Plutôt\nmasculin"],
            "color": ["#888", "#e91e8c", "#1565c0"],
        }))
        .mark_text(fontSize=10, fontStyle="italic")
        .encode(x=alt.X("x:Q", scale=alt.Scale(type="log")),
                y=alt.Y("y:Q", scale=alt.Scale(type="log")),
                text="label:N", color=alt.Color("color:N", scale=None))
    )
    xy = dict(
        x=alt.X("pct_m:Q", scale=alt.Scale(type="log", domainMin=DMIN, domainMax=DMAX),
                title="Garçons (%)", axis=alt.Axis(format="%")),
        y=alt.Y("pct_f:Q", scale=alt.Scale(type="log", domainMin=DMIN, domainMax=DMAX),
                title="Filles (%)", axis=alt.Axis(format="%")),
    )
    bubbles = (
        alt.Chart(g).mark_circle().encode(
            **xy,
            size=alt.Size("total:Q", scale=alt.Scale(range=[20, 900]), legend=None),
            color=alt.Color("peak_year:Q", scale=alt.Scale(scheme="plasma", domain=[1900, 2020]),
                            legend=alt.Legend(title="Année du pic", format="d")),
            opacity=alt.condition("datum.is_focus", alt.value(0.95), alt.value(0.45)),
            tooltip=[
                alt.Tooltip("preusuel:N", title="Prénom"),
                alt.Tooltip("region_cult:N", title="Région dominante"),
                alt.Tooltip("pct_f:Q", format=".2%", title="% filles"),
                alt.Tooltip("pct_m:Q", format=".2%", title="% garçons"),
                alt.Tooltip("total:Q", format=",.0f", title="Naissances"),
                alt.Tooltip("peak_year:Q", format="d", title="Année du pic"),
            ],
        )
    )
    focus_ring = (
        alt.Chart(g[g.is_focus]).mark_point(
            size=260, stroke="#111", strokeWidth=2, fill=None)
        .encode(**xy)
    )
    label_src = (
        g.sort_values("total", ascending=False).head(25)
        if not g.empty else g
    )
    label_src = pd.concat([label_src, g[g.is_focus]]).drop_duplicates("preusuel")
    text_labels = (
        alt.Chart(label_src).mark_text(align="left", dx=6, fontSize=9)
        .encode(**xy, text="preusuel:N")
    )
    scatter_sel = alt.selection_point(name="scatter_sel", fields=["preusuel"], empty=True)
    scatter_chart = (
        (diag + zone_labels + bubbles.add_params(scatter_sel) + focus_ring + text_labels)
        .properties(
            width=430, height=380,
            title=alt.TitleParams("Gender Space — Filles vs Garçons",
                                  subtitle="Cliquez une bulle pour sélectionner un prénom"),
        )
    )

    # ── Évolution miroir (prénom sélectionné) ────────────────────────────────
    tsf = ts[(ts.preusuel == focus) & (ts.annais.between(y0, y1))]
    y_axis = alt.Axis(labelExpr="format(abs(datum.value), '.1~%')", title="% des naissances")
    area_f = (
        alt.Chart(tsf[tsf.sexe == 2]).mark_area(
            color="#ffb3c6", opacity=0.8, line={"color": "#e91e8c", "width": 1.5})
        .encode(x=alt.X("annais:Q", title="Année", axis=alt.Axis(format="d")),
                y=alt.Y("pct_signed:Q", axis=y_axis),
                tooltip=[alt.Tooltip("annais:Q", title="Année"),
                         alt.Tooltip("pct:Q", format=".3%", title="Filles")])
    )
    area_m = (
        alt.Chart(tsf[tsf.sexe == 1]).mark_area(
            color="#a8c8f0", opacity=0.8, line={"color": "#1565c0", "width": 1.5})
        .encode(x=alt.X("annais:Q", title="Année", axis=alt.Axis(format="d")),
                y=alt.Y("pct_signed:Q", axis=y_axis),
                tooltip=[alt.Tooltip("annais:Q", title="Année"),
                         alt.Tooltip("pct:Q", format=".3%", title="Garçons")])
    )
    zero_rule = (
        alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color="black", size=0.8).encode(y="y:Q")
    )
    lbl_f = (alt.Chart(pd.DataFrame({"t": ["Filles"]}))
             .mark_text(color="#e91e8c", fontSize=12, fontWeight="bold")
             .encode(x=alt.value(290), y=alt.value(30), text="t:N"))
    lbl_m = (alt.Chart(pd.DataFrame({"t": ["Garçons"]}))
             .mark_text(color="#1565c0", fontSize=12, fontWeight="bold")
             .encode(x=alt.value(290), y=alt.value(268), text="t:N"))
    name_title = (alt.Chart(pd.DataFrame({"t": [focus]}))
                  .mark_text(fontWeight="bold", fontSize=17, align="left", color="#222")
                  .encode(x=alt.value(8), y=alt.value(16), text="t:N"))
    ts_chart = (area_f + area_m + zero_rule + lbl_f + lbl_m + name_title).properties(
        width=310, height=290,
        title=alt.TitleParams("Évolution du prénom par sexe", subtitle="(% des naissances)"),
    )

    # ── Carte par région culturelle (départements colorés) ───────────────────
    rg = region_gender[(region_gender.preusuel == focus) & (region_gender.annais.between(y0, y1))]
    rgg = rg.groupby("region_cult", as_index=False).agg(nb_f=("nb_f", "sum"), nb_m=("nb_m", "sum"))
    rgg["total_r"] = rgg.nb_f + rgg.nb_m
    rgg = rgg[rgg.total_r >= 10].copy()
    rgg["pct_f"] = (rgg.nb_f / rgg.total_r).round(4)
    dept_map = dept_lookup.merge(rgg[["region_cult", "pct_f"]], on="region_cult")

    dept_src = alt.Data(values=geo_dept, format=alt.DataFormat(type="json", property="features"))
    base_map_layer = (
        alt.Chart(dept_src).mark_geoshape(fill="#e0e8f0", stroke="white", strokeWidth=0.4)
    )
    gender_map_layer = (
        alt.Chart(dept_map)
        .transform_lookup(
            lookup="dpt",
            from_=alt.LookupData(data=dept_src, key="properties.code"),
            as_="geo",
        )
        .mark_geoshape(stroke="white", strokeWidth=0.4)
        .encode(
            shape=alt.Shape(field="geo", type="geojson"),
            color=alt.Color("pct_f:Q",
                            scale=alt.Scale(range=["#1565c0", "#ffffff", "#e91e8c"], domain=[0, 0.5, 1]),
                            legend=alt.Legend(title="% filles", format=".0%")),
            tooltip=[alt.Tooltip("region_cult:N", title="Région"),
                     alt.Tooltip("pct_f:Q", format=".0%", title="% filles")],
        )
    )
    map_chart = (
        (base_map_layer + gender_map_layer)
        .project(type="mercator")
        .properties(width=230, height=300,
                    title=alt.TitleParams("Genre par région",
                                          subtitle="rose = filles · bleu = garçons"))
    )

    return (map_chart | ts_chart | scatter_chart).resolve_scale(
        color="independent", size="independent"
    )


# ──────────────────────────────────────────────────────────────────────────────
# Interface Streamlit
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Prénoms en France (1900–2020)", layout="wide")

st.title("Prénoms en France — 1900 à 2020")
st.caption("Mini-projet IGR204 · Télécom Paris · Données INSEE")

names = load_names()

tab1, tab2, tab3 = st.tabs([
    "1 · Évolution temporelle",
    "2 · Distribution géographique",
    "3 · Effets de genre",
])

with tab1:
    st.subheader("Évolution temporelle & lectures multiples")
    st.markdown(
        "Choisissez une **question** (leaders historiques, tendances éphémères, "
        "prénoms en croissance/déclin, stables, ou liés à un événement) ; les bandes "
        "colorées et les lignes pointillées repèrent les grandes périodes et événements."
    )
    st.altair_chart(build_visu1(names), width="stretch")

with tab2:
    st.subheader("Écart régional à la moyenne nationale")
    st.markdown(
        "Indice régional = part du prénom dans la région ÷ part nationale "
        "(**> 1** = sur-représenté, **< 1** = sous-représenté). Faites glisser l'**année** "
        "et changez de **prénom** : la carte se met à jour **sans clignoter**. "
        "Cliquez une région pour afficher le détail par département."
    )
    geo_reg = load_geojson(str(GEO_REG_PATH), REG_GEOJSON_URL)
    st.altair_chart(build_visu2(names, geo_reg), width="content")

with tab3:
    st.subheader("Gender Space × évolution miroir")
    st.markdown(
        "Chaque bulle est un prénom positionné selon sa part chez les filles et les garçons. "
        "**Cliquez une bulle** pour sélectionner un prénom — le miroir et la carte se mettent à jour. "
        "Utilisez les sliders pour filtrer la **plage d'années** et l'**équilibre**."
    )
    prep3 = prep_visu3(names)
    noms3 = prep3[4]

    # Si un clic sur une bulle a été enregistré au rerun précédent,
    # l'appliquer ICI avant que le widget soit instancié (règle Streamlit).
    if "visu3_pending" in st.session_state:
        st.session_state["visu3_focus"] = st.session_state.pop("visu3_pending")

    if "visu3_focus" not in st.session_state:
        st.session_state["visu3_focus"] = "CAMILLE" if "CAMILLE" in noms3 else noms3[0]

    c1, c2, c3 = st.columns([2, 3, 2])
    with c1:
        st.selectbox("Prénom", options=noms3, key="visu3_focus")
    focus = st.session_state["visu3_focus"]
    with c2:
        yr = st.slider("Plage d'années", 1900, 2019, (1990, 2019))
    with c3:
        bal = st.slider("Équilibre min.", 0.0, 0.5, 0.05, 0.01,
                        help="Part minimale du sexe minoritaire (0.5 = uniquement 50/50)")

    geo_dept = load_geojson(str(GEO_DEPT_PATH))
    chart3 = build_visu3(prep3, focus, yr[0], yr[1], bal, geo_dept)

    event3 = st.altair_chart(chart3, on_select="rerun", use_container_width=False)

    # Stocker le clic dans une clé SÉPARÉE (pas la clé du widget)
    # → sera appliqué au début du prochain rerun, avant l'instanciation du widget
    sel_pts = (event3.selection or {}).get("scatter_sel", [])
    if sel_pts:
        clicked = sel_pts[0].get("preusuel", "")
        if clicked and clicked in noms3 and clicked != focus:
            st.session_state["visu3_pending"] = clicked
            st.rerun()
