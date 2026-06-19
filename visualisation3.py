import json as _json
import pandas as pd
import altair as alt
import geopandas as gpd

alt.data_transformers.enable("json")

names = pd.read_csv("Names_hints/dpt2020.csv", sep=";")
names = names[names.preusuel != "_PRENOMS_RARES"]
names = names[names.dpt != "XX"]
names["annais"] = pd.to_numeric(names["annais"], errors="coerce")
names = names.dropna(subset=["annais"])
names["annais"] = names["annais"].astype(int)

total_yr_sex = (
    names.groupby(["annais", "sexe"])["nombre"]
    .sum().reset_index(name="total_nais")
)

scat_yr = (
    names.groupby(["preusuel", "annais", "sexe"])["nombre"]
    .sum().reset_index()
    .merge(total_yr_sex, on=["annais", "sexe"])
)

girls_yr = (scat_yr[scat_yr.sexe == 2]
            [["preusuel", "annais", "nombre", "total_nais"]]
            .rename(columns={"nombre": "nb_f", "total_nais": "tot_f"}))
boys_yr  = (scat_yr[scat_yr.sexe == 1]
            [["preusuel", "annais", "nombre", "total_nais"]]
            .rename(columns={"nombre": "nb_m", "total_nais": "tot_m"}))

scat_wide = (girls_yr.merge(boys_yr, on=["preusuel", "annais"], how="outer")
             .fillna(0))

name_totals = scat_wide.groupby("preusuel")[["nb_f", "nb_m"]].sum()
popular = name_totals[
    (name_totals.nb_f > 0) &
    (name_totals.nb_m > 0) &
    (name_totals.nb_f + name_totals.nb_m >= 1000)
].index
scat_wide = scat_wide[scat_wide.preusuel.isin(popular)].copy()

peak = (
    names.groupby(["preusuel", "annais"])["nombre"]
    .sum().reset_index()
    .sort_values("nombre", ascending=False)
    .drop_duplicates("preusuel")[["preusuel", "annais"]]
    .rename(columns={"annais": "peak_year"})
)
scat_wide = scat_wide.merge(peak, on="preusuel", how="left")

total_yr = (
    names.groupby(["annais", "sexe"])["nombre"]
    .sum().reset_index(name="total_nais")
)

ts = (
    names[names.preusuel.isin(popular)]
    .groupby(["preusuel", "annais", "sexe"])["nombre"]
    .sum().reset_index()
    .merge(total_yr, on=["annais", "sexe"])
)
ts["pct"] = ts["nombre"] / ts["total_nais"]
ts["pct_signed"] = ts.apply(
    lambda r: -r["pct"] if r["sexe"] == 1 else r["pct"], axis=1
)

DEPT_TO_REGION = {
    "22": "Bretagne",          "29": "Bretagne",          "35": "Bretagne",         "56": "Bretagne",
    "14": "Normandie",         "27": "Normandie",         "50": "Normandie",        "61": "Normandie",        "76": "Normandie",
    "59": "Nord & Flandre",    "62": "Nord & Flandre",
    "02": "Picardie",          "60": "Picardie",          "80": "Picardie",
    "08": "Champagne",         "10": "Champagne",         "51": "Champagne",        "52": "Champagne",
    "54": "Lorraine",          "55": "Lorraine",          "57": "Lorraine",         "88": "Lorraine",
    "67": "Alsace",            "68": "Alsace",
    "25": "Franche-Comté",     "39": "Franche-Comté",     "70": "Franche-Comté",    "90": "Franche-Comté",
    "21": "Bourgogne",         "58": "Bourgogne",         "71": "Bourgogne",        "89": "Bourgogne",
    "75": "Île-de-France",     "77": "Île-de-France",     "78": "Île-de-France",
    "91": "Île-de-France",     "92": "Île-de-France",     "93": "Île-de-France",    "94": "Île-de-France",   "95": "Île-de-France",
    "18": "Centre",            "28": "Centre",            "36": "Centre",           "37": "Centre",           "41": "Centre",          "45": "Centre",
    "44": "Pays de Loire",     "49": "Pays de Loire",     "53": "Pays de Loire",    "72": "Pays de Loire",    "85": "Pays de Loire",
    "16": "Poitou-Charentes",  "17": "Poitou-Charentes",  "79": "Poitou-Charentes", "86": "Poitou-Charentes",
    "19": "Limousin",          "23": "Limousin",          "87": "Limousin",
    "03": "Auvergne",          "15": "Auvergne",          "43": "Auvergne",         "63": "Auvergne",
    "01": "Lyonnais",          "07": "Lyonnais",          "42": "Lyonnais",         "69": "Lyonnais",
    "26": "Dauphiné",          "38": "Dauphiné",
    "73": "Savoie",            "74": "Savoie",
    "04": "Provence",          "05": "Provence",          "06": "Provence",         "13": "Provence",         "83": "Provence",        "84": "Provence",
    "11": "Languedoc",         "30": "Languedoc",         "34": "Languedoc",        "48": "Languedoc",
    "66": "Pays Catalans",
    "09": "Midi-Pyrénées",     "12": "Midi-Pyrénées",     "31": "Midi-Pyrénées",    "32": "Midi-Pyrénées",
    "46": "Midi-Pyrénées",     "65": "Midi-Pyrénées",     "81": "Midi-Pyrénées",    "82": "Midi-Pyrénées",
    "64": "Pays Basque & Béarn",
    "24": "Guyenne",           "33": "Guyenne",           "40": "Guyenne",          "47": "Guyenne",
    "2A": "Corse",             "2B": "Corse",
}

dept_gdf = gpd.read_file("Names_hints/departements-version-simplifiee.geojson")
dept_gdf = dept_gdf[~dept_gdf["code"].str.startswith("97")]
dept_gdf["region_cult"] = dept_gdf["code"].map(DEPT_TO_REGION)
regions_gdf = (
    dept_gdf.dropna(subset=["region_cult"])
    .dissolve(by="region_cult")
    .reset_index()[["region_cult", "geometry"]]
)

_dn = (
    names[names.preusuel.isin(popular)]
    .groupby(["preusuel", "dpt"])["nombre"].sum().reset_index()
)
_dn["region_cult"] = _dn["dpt"].map(DEPT_TO_REGION)
_dn = _dn.dropna(subset=["region_cult"])
_rg = _dn.groupby(["preusuel", "region_cult"])["nombre"].sum().reset_index()
_rg_tot = _dn.groupby("preusuel")["nombre"].sum().reset_index(name="_tot")
_rg = _rg.merge(_rg_tot, on="preusuel")
_rg["_share"] = _rg["nombre"] / _rg["_tot"]
top_region = (
    _rg.sort_values("_share", ascending=False)
    .drop_duplicates("preusuel")[["preusuel", "region_cult"]]
)
scat_wide = scat_wide.merge(top_region, on="preusuel", how="left")

_reg_yr = (
    names[names.preusuel.isin(popular)]
    .assign(region_cult=lambda df: df["dpt"].map(DEPT_TO_REGION))
    .dropna(subset=["region_cult"])
    .groupby(["preusuel", "region_cult", "annais", "sexe"])["nombre"].sum()
    .reset_index()
)
_f_yr = (_reg_yr[_reg_yr.sexe == 2][["preusuel", "region_cult", "annais", "nombre"]]
         .rename(columns={"nombre": "nb_f"}))
_m_yr = (_reg_yr[_reg_yr.sexe == 1][["preusuel", "region_cult", "annais", "nombre"]]
         .rename(columns={"nombre": "nb_m"}))
map_yr_data = (_f_yr.merge(_m_yr, on=["preusuel", "region_cult", "annais"], how="outer")
               .fillna(0))
map_yr_data = map_yr_data[map_yr_data["nb_f"] + map_yr_data["nb_m"] >= 5].reset_index(drop=True)

_regions_features = _json.loads(regions_gdf.to_json())["features"]

name_sel = alt.selection_point(name="name_sel", fields=["preusuel"], empty=False)

year_start_param = alt.param(
    name="year_start", value=1990,
    bind=alt.binding_range(min=1900, max=2019, step=1, name="Start year :  "),
)
year_end_param = alt.param(
    name="year_end", value=2019,
    bind=alt.binding_range(min=1900, max=2019, step=1, name="End year :  "),
)
balance_param = alt.param(
    name="balance", value=0.05,
    bind=alt.binding_range(min=0.0, max=0.5, step=0.01, name="Min. balance :  "),
)
search_param = alt.param(
    name="name_filter", value="",
    bind=alt.binding(input="text", placeholder="e.g. CAMILLE, ALEX…", name="Name :  "),
)

base_map_layer = (
    alt.Chart(regions_gdf)
    .mark_geoshape(fill="#e0e8f0", stroke="white", strokeWidth=0.7)
    .project(type="mercator")
)

gender_map_layer = (
    alt.Chart(map_yr_data)
    .transform_filter(name_sel)
    .transform_filter("datum.annais >= year_start && datum.annais <= year_end")
    .transform_aggregate(
        nb_f="sum(nb_f)", nb_m="sum(nb_m)",
        groupby=["region_cult"],
    )
    .transform_calculate(total_r="datum.nb_f + datum.nb_m")
    .transform_filter("datum.total_r >= 10")
    .transform_calculate(pct_f="datum.nb_f / datum.total_r")
    .transform_lookup(
        lookup="region_cult",
        from_=alt.LookupData(
            data=alt.InlineData(values=_regions_features),
            key="properties.region_cult",
        ),
        as_="geo",
    )
    .mark_geoshape(stroke="white", strokeWidth=0.7)
    .encode(
        shape=alt.Shape(field="geo", type="geojson"),
        color=alt.Color(
            "pct_f:Q",
            scale=alt.Scale(
                range=["#1565c0", "#ffffff", "#e91e8c"],
                domain=[0, 0.5, 1],
            ),
            legend=alt.Legend(title="% girls", format=".0%"),
        ),
        tooltip=[
            alt.Tooltip("region_cult:N", title="Cultural region"),
            alt.Tooltip("pct_f:Q", format=".0%", title="% girls"),
        ],
    )
    .project(type="mercator")
)

map_chart = (
    (base_map_layer + gender_map_layer)
    .properties(
        width=210, height=290,
        title=alt.TitleParams(
            "Gender by cultural region",
            subtitle="pink=girls · blue=boys · click a name →",
        ),
    )
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

zone_labels = alt.Chart(
    pd.DataFrame({
        "x": [0.07, 0.0004, 0.07],
        "y": [0.07, 0.07, 0.0004],
        "label": ["Mixed", "Mostly\nfemale", "Mostly\nmale"],
        "color": ["#888", "#e91e8c", "#1565c0"],
    })
).mark_text(fontSize=10, fontStyle="italic").encode(
    x=alt.X("x:Q", scale=alt.Scale(type="log")),
    y=alt.Y("y:Q", scale=alt.Scale(type="log")),
    text="label:N",
    color=alt.Color("color:N", scale=None),
)

scat_base = (
    alt.Chart(scat_wide)
    .transform_filter("datum.annais >= year_start && datum.annais <= year_end")
    .transform_aggregate(
        nb_f="sum(nb_f)", nb_m="sum(nb_m)",
        tot_f="sum(tot_f)", tot_m="sum(tot_m)",
        peak_year="max(peak_year)",
        region_cult="max(region_cult)",
        groupby=["preusuel"],
    )
    .transform_calculate(total="datum.nb_f + datum.nb_m")
    .transform_calculate(pct_f="datum.nb_f / datum.tot_f")
    .transform_calculate(pct_m="datum.nb_m / datum.tot_m")
    .transform_calculate(ratio_f="datum.nb_f / datum.total")
    .transform_filter("datum.nb_f > 0 && datum.nb_m > 0 && datum.total >= 100")
    .transform_filter("datum.ratio_f >= balance && datum.ratio_f <= (1 - balance)")
)

bubbles = (
    scat_base
    .mark_circle()
    .encode(
        x=alt.X(
            "pct_m:Q",
            scale=alt.Scale(type="log", domainMin=DMIN, domainMax=DMAX),
            title="Boys (%)",
            axis=alt.Axis(format="%"),
        ),
        y=alt.Y(
            "pct_f:Q",
            scale=alt.Scale(type="log", domainMin=DMIN, domainMax=DMAX),
            title="Girls (%)",
            axis=alt.Axis(format="%"),
        ),
        size=alt.Size("total:Q", scale=alt.Scale(range=[20, 900]), legend=None),
        color=alt.Color(
            "peak_year:Q",
            scale=alt.Scale(scheme="plasma", domain=[1900, 2020]),
            legend=alt.Legend(title="Peak year", format="d"),
        ),
        opacity={
            "condition": [
                {"param": "name_sel", "value": 0.95},
                {"test": "name_filter == '' || indexof(upper(datum.preusuel), upper(name_filter)) === 0", "value": 0.55},
            ],
            "value": 0.04,
        },
        tooltip=[
            alt.Tooltip("preusuel:N", title="Name"),
            alt.Tooltip("region_cult:N", title="Top region"),
            alt.Tooltip("pct_f:Q", format=".2%", title="% girls"),
            alt.Tooltip("pct_m:Q", format=".2%", title="% boys"),
            alt.Tooltip("total:Q", format=",.0f", title="Births"),
            alt.Tooltip("peak_year:Q", format="d", title="Peak year"),
        ],
    )
)

text_labels = (
    scat_base
    .mark_text(align="left", dx=5, fontSize=9)
    .encode(
        x=alt.X("pct_m:Q", scale=alt.Scale(type="log")),
        y=alt.Y("pct_f:Q", scale=alt.Scale(type="log")),
        text="preusuel:N",
    )
    .transform_filter(
        "name_filter == '' || indexof(upper(datum.preusuel), upper(name_filter)) === 0"
    )
    .transform_window(
        rank="rank(total)", sort=[alt.SortField("total", order="descending")]
    )
    .transform_filter(alt.datum.rank <= 25)
)

scatter_chart = (
    (diag + zone_labels + bubbles + text_labels)
    .add_params(year_start_param, year_end_param, balance_param, search_param)
    .properties(
        width=430, height=380,
        title=alt.TitleParams(
            "Gender Space — Girls vs Boys",
            subtitle="Which names are gender-neutral, female, or male?",
        ),
    )
)

base = alt.Chart(ts)

y_axis = alt.Axis(
    labelExpr="format(abs(datum.value), '.1~%')",
    title="% of births",
)

area_f = (
    base.mark_area(color="#ffb3c6", opacity=0.8, line={"color": "#e91e8c", "width": 1.5})
    .encode(
        x=alt.X("annais:Q", title="Year", axis=alt.Axis(format="d")),
        y=alt.Y("pct_signed:Q", axis=y_axis),
        tooltip=[
            alt.Tooltip("annais:Q", title="Year"),
            alt.Tooltip("pct:Q", format=".3%", title="Girls"),
        ],
    )
    .transform_filter("datum.annais >= year_start && datum.annais <= year_end")
    .transform_filter(alt.datum.sexe == 2)
    .transform_filter(name_sel)
)

area_m = (
    base.mark_area(color="#a8c8f0", opacity=0.8, line={"color": "#1565c0", "width": 1.5})
    .encode(
        x=alt.X("annais:Q", title="Year", axis=alt.Axis(format="d")),
        y=alt.Y("pct_signed:Q", axis=y_axis),
        tooltip=[
            alt.Tooltip("annais:Q", title="Year"),
            alt.Tooltip("pct:Q", format=".3%", title="Boys"),
        ],
    )
    .transform_filter("datum.annais >= year_start && datum.annais <= year_end")
    .transform_filter(alt.datum.sexe == 1)
    .transform_filter(name_sel)
)

zero_rule = (
    alt.Chart(pd.DataFrame({"y": [0]}))
    .mark_rule(color="black", size=0.8)
    .encode(y="y:Q")
)

lbl_f = (
    alt.Chart(pd.DataFrame({"t": ["Girls"]}))
    .mark_text(color="#e91e8c", fontSize=12, fontWeight="bold")
    .encode(x=alt.value(290), y=alt.value(30), text="t:N")
)
lbl_m = (
    alt.Chart(pd.DataFrame({"t": ["Boys"]}))
    .mark_text(color="#1565c0", fontSize=12, fontWeight="bold")
    .encode(x=alt.value(290), y=alt.value(268), text="t:N")
)

name_title = (
    alt.Chart(ts)
    .transform_filter(name_sel)
    .transform_aggregate(preusuel="max(preusuel)", groupby=[])
    .mark_text(fontWeight="bold", fontSize=17, align="left", color="#222")
    .encode(x=alt.value(8), y=alt.value(16), text="preusuel:N")
)

ts_chart = (area_f + area_m + zero_rule + lbl_f + lbl_m + name_title).properties(
    width=310, height=290,
    title=alt.TitleParams(
        "Name evolution by sex",
        subtitle="(% of births)  ·  click a name →",
    ),
)

_help = pd.DataFrame({
    "label": ["Map ?", "Scatter ?", "Year range ?", "Min. balance ?", "Name ?"],
    "How to use": [
        "Click a name in the scatter → the map colours each region by % girls (pink) vs % boys (blue)  ·  respects the year sliders",
        "Each bubble = one name  ·  log axes = % girls vs % boys  ·  colour = peak year  ·  size = total births",
        "Start / End year sliders set the time window — scatter and mirror chart update simultaneously",
        "Minimum share of the minority sex: 0 = all  ·  0.05 = at least 5 %  ·  0.5 = 50/50 only",
        "Type first letters to highlight names in the scatter — click a bubble to see its mirror evolution",
    ],
    "x": [90, 280, 490, 700, 910],
})

help_row = (
    alt.Chart(_help)
    .mark_text(fontSize=11, color="#888", fontStyle="italic", cursor="help")
    .encode(
        x=alt.X("x:Q", axis=None, scale=alt.Scale(domain=[0, 1000])),
        y=alt.value(16),
        text="label:N",
        tooltip=alt.Tooltip("How to use:N"),
    )
    .properties(width=1000, height=32)
)

final = alt.vconcat(
    (map_chart | ts_chart | scatter_chart)
    .resolve_scale(color="independent", size="independent")
    .add_params(name_sel),
    help_row,
    spacing=12,
).properties(
    title=alt.TitleParams(
        "Are there gender effects in the data? Does popularity of names given to both sexes evolve consistently?",
        subtitle=[
            "Note: this data set treats sex as binary — a simplification that does not generally hold.",
            "Try clicking: YAEL · DOMINIQUE · CLAUDE",
        ],
        anchor="start",
        fontSize=15,
        fontWeight="normal",
        subtitleFontSize=11,
        subtitleColor="#666",
        subtitleFontStyle="italic",
    )
)

final.save("visualisation3.html")
print("Saved → visualisation3.html")
