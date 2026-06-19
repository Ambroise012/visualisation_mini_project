"""
Mini Project — Baby Names in France (1900–2020)
Application Streamlit regroupant les 3 visualisations du projet.

    streamlit run streamlit_app.py
"""

import json
from pathlib import Path
from urllib.request import urlopen

import altair as alt
import pandas as pd
import streamlit as st

alt.data_transformers.disable_max_rows()

BASE_DIR = Path(__file__).parent
CSV_PATH = BASE_DIR / "Names_hints" / "dpt2020.csv"
GEO_REG_PATH = BASE_DIR / "Names_hints" / "regions_fr.geojson"


# ──────────────────────────────────────────────────────────────────────────────
# Chargement des données (mis en cache)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_names() -> pd.DataFrame:
    """Charge et nettoie le fichier des prénoms par département."""
    names = pd.read_csv(CSV_PATH, sep=";")
    names = names[names.preusuel != "_PRENOMS_RARES"]
    names = names[names.dpt != "XX"]
    names["annais"] = pd.to_numeric(names["annais"], errors="coerce")
    names = names.dropna(subset=["annais"])
    names["annais"] = names["annais"].astype(int)
    names = names[names["annais"].between(1900, 2020)]
    return names


@st.cache_data
def load_regions_geojson() -> dict:
    """Charge le GeoJSON des régions (téléchargé et mis en cache si absent)."""
    if GEO_REG_PATH.exists() and GEO_REG_PATH.stat().st_size > 200:
        with GEO_REG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    url = "https://france-geojson.gregoiredavid.fr/repo/regions.geojson"
    with urlopen(url) as r:
        geo = json.loads(r.read().decode("utf-8"))
    with GEO_REG_PATH.open("w", encoding="utf-8") as f:
        json.dump(geo, f, ensure_ascii=False)
    return geo


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


# ──────────────────────────────────────────────────────────────────────────────
# Visualisation 1 — Évolution temporelle & effets de tendance
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def build_visu1(names: pd.DataFrame) -> alt.Chart:
    all_names = names.groupby(["annais", "preusuel"], as_index=False)["nombre"].sum()

    scores = []
    MIN_TOTAL = 3000
    for first_name, g in all_names.groupby("preusuel"):
        total = g["nombre"].sum()
        if total < MIN_TOTAL:
            continue
        g = g.sort_values("annais").reset_index(drop=True)
        peak_pos = g["nombre"].idxmax()
        peak = g.loc[peak_pos, "nombre"]
        before = g.loc[: peak_pos - 1, "nombre"]
        after = g.loc[peak_pos + 1 :, "nombre"]
        if len(before) < 5 or len(after) < 5:
            continue
        peak_width = (g["nombre"] >= 0.5 * peak).sum()
        trend_score = (
            (peak / (before.mean() + 1)) * (peak / (after.mean() + 1)) / peak_width
        )
        scores.append({"preusuel": first_name, "trend_score": trend_score})

    trend_scores = (
        pd.DataFrame(scores).sort_values("trend_score", ascending=False).reset_index(drop=True)
    )
    trend_names = trend_scores.head(10)["preusuel"].tolist()

    top_names = names.groupby("preusuel")["nombre"].sum().nlargest(10).index.tolist()
    displayed_names = sorted(set(top_names) | set(trend_names))

    time_data = (
        names[names["preusuel"].isin(displayed_names)]
        .groupby(["annais", "preusuel"], as_index=False)["nombre"]
        .sum()
    )
    yearly_totals = (
        time_data.groupby("annais", as_index=False)["nombre"]
        .sum()
        .rename(columns={"nombre": "yearly_total"})
    )
    time_data = time_data.merge(yearly_totals, on="annais")
    time_data["percentage"] = 100 * time_data["nombre"] / time_data["yearly_total"]
    time_data["trend_effect"] = time_data["preusuel"].isin(trend_names)

    display_mode = alt.param(
        name="DisplayMode", value="Count",
        bind=alt.binding_radio(options=["Count", "Percentage"], name="Affichage : "),
    )
    trend_filter = alt.param(
        name="TrendFilter", value="All",
        bind=alt.binding_radio(options=["All", "Trend-driven"], name="Type : "),
    )
    first_name_p = alt.param(
        name="FirstName", value="All",
        bind=alt.binding_select(options=["All"] + displayed_names, name="Prénom : "),
    )

    return (
        alt.Chart(time_data)
        .add_params(display_mode, trend_filter, first_name_p)
        .transform_filter("(FirstName == 'All') || (datum.preusuel == FirstName)")
        .transform_filter("(TrendFilter == 'All') || datum.trend_effect")
        .transform_calculate(
            value="DisplayMode == 'Count' ? datum.nombre : datum.percentage"
        )
        .mark_line(point=True)
        .encode(
            x=alt.X("annais:O", title="Année"),
            y=alt.Y("value:Q", title="Naissances / Pourcentage"),
            color=alt.Color("preusuel:N", title="Prénom"),
            tooltip=[
                alt.Tooltip("annais:O", title="Année"),
                alt.Tooltip("preusuel:N", title="Prénom"),
                alt.Tooltip("nombre:Q", title="Naissances"),
                alt.Tooltip("percentage:Q", title="Pourcentage", format=".2f"),
            ],
        )
        .properties(height=560, title="Évolution des prénoms")
        .interactive()
    )


# ──────────────────────────────────────────────────────────────────────────────
# Visualisation 2 — Distribution géographique par région
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def build_visu2(names: pd.DataFrame, geo_reg: dict) -> alt.VConcatChart:
    noms_carte = ["ENORA", "ENZO", "CAMILLE", "EMMA", "KEVIN", "JEAN", "MARIE", "LEA"]

    df = names.rename(columns={"annais": "annee"}).copy()
    df["region"] = df["dpt"].map(DEPT_TO_REG)
    df_reg = (
        df.dropna(subset=["region"])
        .pipe(lambda d: d[d["preusuel"].isin(noms_carte)])
        .groupby(["preusuel", "annee", "region"], as_index=False)["nombre"]
        .sum()
    )
    df_reg["key"] = (
        df_reg["region"] + "_" + df_reg["annee"].astype(str) + "_" + df_reg["preusuel"]
    )

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

    geo_src = alt.Data(
        values=geo_reg, format=alt.DataFormat(type="json", property="features")
    )

    carte = (
        alt.Chart(geo_src)
        .transform_calculate(
            key="datum.properties.nom + '_' + toString(Annee) + '_' + PrenoMCarte"
        )
        .transform_lookup(
            lookup="key", from_=alt.LookupData(df_reg, "key", ["nombre"])
        )
        .mark_geoshape(stroke="white", strokeWidth=0.8, invalid="filter")
        .encode(
            color=alt.Color(
                "nombre:Q", title="Naissances",
                scale=alt.Scale(scheme="blues", domainMin=0),
            ),
            tooltip=[
                alt.Tooltip("properties.nom:N", title="Région"),
                alt.Tooltip("nombre:Q", title="Naissances", format=","),
            ],
        )
        .add_params(p_annee, p_prenom)
        .project("mercator")
        .properties(width=560, height=440, title="Naissances par région")
    )

    ranking = (
        alt.Chart(df_reg)
        .transform_filter("datum.preusuel == PrenoMCarte && datum.annee == Annee")
        .transform_window(rank="rank()", sort=[alt.SortField("nombre", order="descending")])
        .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
        .encode(
            y=alt.Y("region:N", sort="-x", title=None),
            x=alt.X("nombre:Q", title="Naissances"),
            color=alt.Color(
                "nombre:Q", scale=alt.Scale(scheme="blues", domainMin=0), legend=None
            ),
            tooltip=[
                alt.Tooltip("region:N", title="Région"),
                alt.Tooltip("nombre:Q", title="Naissances", format=","),
            ],
        )
        .add_params(p_annee, p_prenom)
        .properties(width=560, height=310, title="Classement des régions")
    )

    return (
        alt.vconcat(carte, ranking)
        .resolve_scale(color="independent")
        .properties(
            title=alt.TitleParams(
                "Évolution des naissances par région — 1900 à 2020",
                fontSize=15, anchor="start",
            )
        )
    )


# ──────────────────────────────────────────────────────────────────────────────
# Visualisation 3 — Gender Space × évolution miroir
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def build_visu3(names: pd.DataFrame) -> alt.VConcatChart:
    total_yr_sex = (
        names.groupby(["annais", "sexe"])["nombre"].sum().reset_index(name="total_nais")
    )
    scat_yr = (
        names.groupby(["preusuel", "annais", "sexe"])["nombre"]
        .sum().reset_index()
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
        (name_totals.nb_f > 0)
        & (name_totals.nb_m > 0)
        & (name_totals.nb_f + name_totals.nb_m >= 1000)
    ].index
    scat_wide = scat_wide[scat_wide.preusuel.isin(popular)].copy()

    peak = (
        names.groupby(["preusuel", "annais"])["nombre"].sum().reset_index()
        .sort_values("nombre", ascending=False)
        .drop_duplicates("preusuel")[["preusuel", "annais"]]
        .rename(columns={"annais": "peak_year"})
    )
    scat_wide = scat_wide.merge(peak, on="preusuel", how="left")

    total_yr = (
        names.groupby(["annais", "sexe"])["nombre"].sum().reset_index(name="total_nais")
    )
    ts = (
        names[names.preusuel.isin(popular)]
        .groupby(["preusuel", "annais", "sexe"])["nombre"].sum().reset_index()
        .merge(total_yr, on=["annais", "sexe"])
    )
    ts["pct"] = ts["nombre"] / ts["total_nais"]
    ts["pct_signed"] = ts.apply(
        lambda r: -r["pct"] if r["sexe"] == 1 else r["pct"], axis=1
    )

    name_sel = alt.selection_point(name="name_sel", fields=["preusuel"], empty=False)
    year_start_param = alt.param(
        name="year_start", value=1990,
        bind=alt.binding_range(min=1900, max=2019, step=1, name="Année début :  "),
    )
    year_end_param = alt.param(
        name="year_end", value=2019,
        bind=alt.binding_range(min=1900, max=2019, step=1, name="Année fin :  "),
    )
    balance_param = alt.param(
        name="balance", value=0.05,
        bind=alt.binding_range(min=0.0, max=0.5, step=0.01, name="Équilibre min :  "),
    )
    search_param = alt.param(
        name="name_filter", value="",
        bind=alt.binding(input="text", placeholder="Ex : CAMILLE, ALEX…", name="Prénom :  "),
    )

    DMIN, DMAX = 3e-5, 0.12

    diag = (
        alt.Chart(pd.DataFrame({"x": [DMIN, DMAX], "y": [DMIN, DMAX]}))
        .mark_line(color="#bbb", strokeDash=[5, 5], size=1.5)
        .encode(
            x=alt.X("x:Q", scale=alt.Scale(type="log")),
            y=alt.Y("y:Q", scale=alt.Scale(type="log")),
        )
    )
    zone_labels = (
        alt.Chart(
            pd.DataFrame({
                "x": [0.07, 0.0004, 0.07],
                "y": [0.07, 0.07, 0.0004],
                "label": ["Mixte", "Plutôt\nféminin", "Plutôt\nmasculin"],
                "color": ["#888", "#e91e8c", "#1565c0"],
            })
        )
        .mark_text(fontSize=10, fontStyle="italic")
        .encode(
            x=alt.X("x:Q", scale=alt.Scale(type="log")),
            y=alt.Y("y:Q", scale=alt.Scale(type="log")),
            text="label:N",
            color=alt.Color("color:N", scale=None),
        )
    )

    scat_base = (
        alt.Chart(scat_wide)
        .transform_filter("datum.annais >= year_start && datum.annais <= year_end")
        .transform_aggregate(
            nb_f="sum(nb_f)", nb_m="sum(nb_m)", tot_f="sum(tot_f)", tot_m="sum(tot_m)",
            peak_year="max(peak_year)", groupby=["preusuel"],
        )
        .transform_calculate(total="datum.nb_f + datum.nb_m")
        .transform_calculate(pct_f="datum.nb_f / datum.tot_f")
        .transform_calculate(pct_m="datum.nb_m / datum.tot_m")
        .transform_calculate(ratio_f="datum.nb_f / datum.total")
        .transform_filter("datum.nb_f > 0 && datum.nb_m > 0 && datum.total >= 100")
        .transform_filter("datum.ratio_f >= balance && datum.ratio_f <= (1 - balance)")
    )

    bubbles = (
        scat_base.mark_circle()
        .encode(
            x=alt.X("pct_m:Q", scale=alt.Scale(type="log", domainMin=DMIN, domainMax=DMAX),
                    title="Garçons (%)", axis=alt.Axis(format="%")),
            y=alt.Y("pct_f:Q", scale=alt.Scale(type="log", domainMin=DMIN, domainMax=DMAX),
                    title="Filles (%)", axis=alt.Axis(format="%")),
            size=alt.Size("total:Q", scale=alt.Scale(range=[20, 900]), legend=None),
            color=alt.Color("peak_year:Q",
                            scale=alt.Scale(scheme="plasma", domain=[1900, 2020]),
                            legend=alt.Legend(title="Année du pic", format="d")),
            opacity={
                "condition": [
                    {"param": "name_sel", "value": 0.95},
                    {"test": "name_filter == '' || indexof(upper(datum.preusuel), upper(name_filter)) === 0", "value": 0.55},
                ],
                "value": 0.04,
            },
            tooltip=[
                alt.Tooltip("preusuel:N", title="Prénom"),
                alt.Tooltip("pct_f:Q", format=".2%", title="% filles"),
                alt.Tooltip("pct_m:Q", format=".2%", title="% garçons"),
                alt.Tooltip("total:Q", format=",.0f", title="Naissances"),
                alt.Tooltip("peak_year:Q", format="d", title="Année du pic"),
            ],
        )
        .add_params(name_sel)
    )

    text_labels = (
        scat_base.mark_text(align="left", dx=5, fontSize=9)
        .encode(
            x=alt.X("pct_m:Q", scale=alt.Scale(type="log")),
            y=alt.Y("pct_f:Q", scale=alt.Scale(type="log")),
            text="preusuel:N",
        )
        .transform_filter(
            "name_filter == '' || indexof(upper(datum.preusuel), upper(name_filter)) === 0"
        )
        .transform_window(rank="rank(total)", sort=[alt.SortField("total", order="descending")])
        .transform_filter(alt.datum.rank <= 25)
    )

    scatter_chart = (
        (diag + zone_labels + bubbles + text_labels)
        .add_params(year_start_param, year_end_param, balance_param, search_param)
        .properties(
            width=500, height=450,
            title=alt.TitleParams(
                "Gender Space — Girls vs Boys",
                subtitle="Quels prénoms sont mixtes, féminins ou masculins ?",
            ),
        )
    )

    base = alt.Chart(ts)
    y_axis = alt.Axis(labelExpr="format(abs(datum.value), '.1~%')", title="% des naissances")

    area_f = (
        base.mark_area(color="#ffb3c6", opacity=0.8, line={"color": "#e91e8c", "width": 1.5})
        .encode(
            x=alt.X("annais:Q", title="Année", axis=alt.Axis(format="d")),
            y=alt.Y("pct_signed:Q", axis=y_axis),
            tooltip=[alt.Tooltip("annais:Q", title="Année"), alt.Tooltip("pct:Q", format=".3%", title="Filles")],
        )
        .transform_filter("datum.annais >= year_start && datum.annais <= year_end")
        .transform_filter(alt.datum.sexe == 2)
        .transform_filter(name_sel)
    )
    area_m = (
        base.mark_area(color="#a8c8f0", opacity=0.8, line={"color": "#1565c0", "width": 1.5})
        .encode(
            x=alt.X("annais:Q", title="Année", axis=alt.Axis(format="d")),
            y=alt.Y("pct_signed:Q", axis=y_axis),
            tooltip=[alt.Tooltip("annais:Q", title="Année"), alt.Tooltip("pct:Q", format=".3%", title="Garçons")],
        )
        .transform_filter("datum.annais >= year_start && datum.annais <= year_end")
        .transform_filter(alt.datum.sexe == 1)
        .transform_filter(name_sel)
    )
    zero_rule = (
        alt.Chart(pd.DataFrame({"y": [0]}))
        .mark_rule(color="black", size=0.8).encode(y="y:Q")
    )
    lbl_f = (
        alt.Chart(pd.DataFrame({"t": ["Filles"]}))
        .mark_text(color="#e91e8c", fontSize=12, fontWeight="bold")
        .encode(x=alt.value(340), y=alt.value(30), text="t:N")
    )
    lbl_m = (
        alt.Chart(pd.DataFrame({"t": ["Garçons"]}))
        .mark_text(color="#1565c0", fontSize=12, fontWeight="bold")
        .encode(x=alt.value(340), y=alt.value(268), text="t:N")
    )
    name_title = (
        alt.Chart(ts)
        .transform_filter(name_sel)
        .transform_aggregate(preusuel="max(preusuel)", groupby=[])
        .mark_text(fontWeight="bold", fontSize=17, align="left", color="#222")
        .encode(x=alt.value(8), y=alt.value(16), text="preusuel:N")
    )

    ts_chart = (area_f + area_m + zero_rule + lbl_f + lbl_m + name_title).properties(
        width=380, height=300,
        title=alt.TitleParams(
            "Évolution du prénom par sexe",
            subtitle="(% des naissances)  ·  cliquez sur un prénom →",
        ),
    )

    return (ts_chart | scatter_chart).resolve_scale(
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
    st.subheader("Évolution temporelle & effets de tendance")
    st.markdown(
        "Évolution des 10 prénoms les plus populaires et des prénoms identifiés comme "
        "**tendances éphémères** (pic suivi d'un déclin rapide)."
    )
    st.altair_chart(build_visu1(names), width="stretch")

with tab2:
    st.subheader("Distribution géographique par région")
    st.markdown(
        "Carte choroplèthe de la France couplée au classement des régions, "
        "mis à jour en temps réel selon l'**année** et le **prénom**."
    )
    geo_reg = load_regions_geojson()
    st.altair_chart(build_visu2(names, geo_reg), width="content")

with tab3:
    st.subheader("Gender Space × évolution miroir")
    st.markdown(
        "Chaque bulle est un prénom positionné selon sa part chez les filles et les garçons. "
        "**Cliquez** sur une bulle pour afficher l'évolution miroir à gauche."
    )
    st.altair_chart(build_visu3(names), width="content")
