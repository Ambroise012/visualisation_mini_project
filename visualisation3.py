import pandas as pd
import altair as alt

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

name_sel = alt.selection_point(name="name_sel", fields=["preusuel"], empty=False)

year_start_param = alt.param(
    name="year_start",
    value=1990,
    bind=alt.binding_range(min=1900, max=2019, step=1, name="Année début :  "),
)
year_end_param = alt.param(
    name="year_end",
    value=2019,
    bind=alt.binding_range(min=1900, max=2019, step=1, name="Année fin :  "),
)

balance_param = alt.param(
    name="balance",
    value=0.05,
    bind=alt.binding_range(min=0.0, max=0.5, step=0.01, name="Équilibre min :  "),
)

search_param = alt.param(
    name="name_filter",
    value="",
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

zone_labels = alt.Chart(
    pd.DataFrame({
        "x": [0.07, 0.0004, 0.07],
        "y": [0.07, 0.07, 0.0004],
        "label": ["Mixte", "Plutôt\nféminin", "Plutôt\nmasculin"],
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
        nb_f="sum(nb_f)",
        nb_m="sum(nb_m)",
        tot_f="sum(tot_f)",
        tot_m="sum(tot_m)",
        peak_year="max(peak_year)",
        groupby=["preusuel"],
    )
    .transform_calculate(total="datum.nb_f + datum.nb_m")
    .transform_calculate(pct_f="datum.nb_f / datum.tot_f")
    .transform_calculate(pct_m="datum.nb_m / datum.tot_m")
    .transform_calculate(ratio_f="datum.nb_f / datum.total")
    .transform_filter("datum.nb_f > 0 && datum.nb_m > 0 && datum.total >= 100")
    .transform_filter(
        "datum.ratio_f >= balance && datum.ratio_f <= (1 - balance)"
    )
)

bubbles = (
    scat_base
    .mark_circle()
    .encode(
        x=alt.X(
            "pct_m:Q",
            scale=alt.Scale(type="log", domainMin=DMIN, domainMax=DMAX),
            title="Garçons (%)",
            axis=alt.Axis(format="%"),
        ),
        y=alt.Y(
            "pct_f:Q",
            scale=alt.Scale(type="log", domainMin=DMIN, domainMax=DMAX),
            title="Filles (%)",
            axis=alt.Axis(format="%"),
        ),
        size=alt.Size("total:Q", scale=alt.Scale(range=[20, 900]), legend=None),
        color=alt.Color(
            "peak_year:Q",
            scale=alt.Scale(scheme="plasma", domain=[1900, 2020]),
            legend=alt.Legend(title="Année du pic", format="d"),
        ),
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
        width=500,
        height=450,
        title=alt.TitleParams(
            "Gender Space — Girls vs Boys",
            subtitle="Quels prénoms sont mixtes, féminins ou masculins ?",
        ),
    )
)

base = alt.Chart(ts)

y_axis = alt.Axis(
    labelExpr="format(abs(datum.value), '.1~%')",
    title="% des naissances",
)

area_f = (
    base.mark_area(color="#ffb3c6", opacity=0.8, line={"color": "#e91e8c", "width": 1.5})
    .encode(
        x=alt.X("annais:Q", title="Année", axis=alt.Axis(format="d")),
        y=alt.Y("pct_signed:Q", axis=y_axis),
        tooltip=[
            alt.Tooltip("annais:Q", title="Année"),
            alt.Tooltip("pct:Q", format=".3%", title="Filles"),
        ],
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
        tooltip=[
            alt.Tooltip("annais:Q", title="Année"),
            alt.Tooltip("pct:Q", format=".3%", title="Garçons"),
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
    width=380,
    height=300,
    title=alt.TitleParams(
        "Évolution du prénom par sexe",
        subtitle="(% des naissances)  ·  cliquez sur un prénom →",
    ),
)

_H = 112

_bg = (
    alt.Chart(pd.DataFrame({"_": [0]}))
    .mark_rect(color="#f5f7fa", stroke="#c8d0da", strokeWidth=1)
    .encode(x=alt.value(0), x2=alt.value(950), y=alt.value(0), y2=alt.value(_H))
)

_info_rows = pd.DataFrame({
    "text": [
        "Guide d'utilisation",
        "● Scatter (droite) : chaque bulle = un prénom  ·  axes log = % filles vs % garçons  ·  couleur = année du pic  ·  taille = naissances",
        "● Sliders Année début / fin : définissent la plage temporelle — scatter et graphique miroir s'adaptent simultanément",
        "● Équilibre min : part minimale du sexe minoritaire  (0 = tous  ·  0.05 = au moins 5 %  ·  0.5 = uniquement 50/50)",
        "● Prénom : tapez les premières lettres pour mettre en évidence les prénoms — puis cliquez pour voir l'évolution miroir",
    ],
    "y": [20, 42, 60, 78, 96],
    "bold": [True, False, False, False, False],
})

_title_mark = (
    alt.Chart(_info_rows[_info_rows.bold])
    .mark_text(align="left", dx=14, fontSize=12, fontWeight="bold", color="#333")
    .encode(
        x=alt.value(0),
        y=alt.Y("y:Q", axis=None, scale=alt.Scale(domain=[_H, 0])),
        text="text:N",
    )
)

_body_mark = (
    alt.Chart(_info_rows[~_info_rows.bold].reset_index(drop=True))
    .mark_text(align="left", dx=14, fontSize=10.5, color="#555")
    .encode(
        x=alt.value(0),
        y=alt.Y("y:Q", axis=None, scale=alt.Scale(domain=[_H, 0])),
        text="text:N",
    )
)

info_box = (_bg + _title_mark + _body_mark).properties(width=950, height=_H)

final = alt.vconcat(
    (ts_chart | scatter_chart).resolve_scale(
        color="independent",
        size="independent",
    ),
    info_box,
    spacing=16,
)

final.save("visualisation3.html")
print("Saved → visualisation3.html")
