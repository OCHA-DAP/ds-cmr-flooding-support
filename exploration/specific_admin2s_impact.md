---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.1
  kernelspec:
    display_name: ds-cmr-flooding-support
    language: python
    name: ds-cmr-flooding-support
---

# Specific departments - impact estimate from EMDAT

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from src.datasources import impact, floodscan, ecmwf, worldpop, codab
from src.constants import *
```

```python
DATE_LT_STR = "m7-l123"
PUB_MONTH_STR = "juillet"
VALID_MONTHS_STR = "juillet-août-septembre"
MIN_YEAR = 2000
```

```python
years = range(MIN_YEAR, 2024)
```

```python
df_fs = floodscan.load_adm_flood_exposures()
df_compare = df_fs.copy()
df_compare = df_compare[df_compare["year"].isin(years)]
df_compare["impact"] = 0
```

```python
col = "Total personne affecté"
df_impact = impact.load_processed_impact_2022()
df_impact_adm2 = df_impact.groupby("ADM2_PCODE")[col].sum()
```

```python
# Logone-et-Chari

# HDX
df_compare.loc[
    (df_compare["year"] == 2022) & (df_compare["ADM2_PCODE"] == LOGONE_CHARI),
    "impact",
] = df_impact_adm2.loc[LOGONE_CHARI]
```

```python
# Mayo-Danay

# HDX
df_compare.loc[
    (df_compare["year"] == 2022) & (df_compare["ADM2_PCODE"] == MAYO_DANAY),
    "impact",
] = df_impact_adm2.loc[MAYO_DANAY]

# https://reliefweb.int/report/cameroon/cameroon-floods-far-north-region-final-report-dref-operation-no-mdrcm029
df_compare.loc[
    (df_compare["year"] == 2020) & (df_compare["ADM2_PCODE"] == MAYO_DANAY),
    "impact",
] = 19218

# EMDAT
df_compare.loc[
    (df_compare["year"] == 2010) & (df_compare["ADM2_PCODE"] == MAYO_DANAY),
    "impact",
] = 3095
df_compare.loc[
    (df_compare["year"] == 2013) & (df_compare["ADM2_PCODE"] == MAYO_DANAY),
    "impact",
] = 805
```

```python
df_compare
```

```python

```

```python
# 2012 estimated distribution
31980
```

```python
df_pop = worldpop.load_adm_worldpop()
```

```python
adm2 = codab.load_codab(admin_level=2)
```

```python
impact_2012_adm2s = [
    "CM003002",
    "CM004001",
    "CM004002",
    "CM004003",
    "CM004004",
    "CM006001",
    "CM006002",
    "CM006003",
    "CM006004",
    "CM007007",
]
```

```python
total_impact_pop = df_pop[df_pop["ADM2_PCODE"].isin(impact_2012_adm2s)][
    "total_pop"
].sum()
total_impact_pop
```

```python
df_pop.set_index("ADM2_PCODE").loc[LOGONE_CHARI]
```

```python
for pcode in [LOGONE_CHARI, MAYO_DANAY]:
    df_compare.loc[
        (df_compare["year"] == 2012) & (df_compare["ADM2_PCODE"] == pcode),
        "impact",
    ] = (
        31980
        * df_pop.set_index("ADM2_PCODE").loc[pcode].values
        / total_impact_pop
    )
```

```python
df_compare.set_index("ADM2_PCODE").loc[LOGONE_CHARI]
```

```python
for pcode in [LOGONE_CHARI, MAYO_DANAY]:
    dff = df_compare[df_compare["ADM2_PCODE"] == pcode]
    dff.plot.scatter(x="total_exposed", y="impact")
```

```python
filename = f"cmr_ecmwf_{DATE_LT_STR}_logone-chari_ranks.csv"
ec = pd.read_csv(ecmwf.ECMWF_PROC_DIR / filename)
ec = ec[(ec["year"].isin(years)) | (ec["year"] == 2024)]
ec["percentile_2000"] = ec["tprate"].rank(pct=True)
```

```python
ec
```

```python
q_range = 0.25
q = ec.set_index("year").loc[2024]["percentile_2000"]
high_q, low_q = min(q + q_range, 1), max(q - q_range, 0)
print([low_q, q, high_q])
```

```python
for pcode in [LOGONE_CHARI, MAYO_DANAY]:
    print(
        df_compare.set_index("ADM2_PCODE")
        .loc[pcode]["impact"]
        .quantile([low_q, q, high_q])
    )
```

```python
df_compare.set_index("ADM2_PCODE").loc[MAYO_DANAY]
```

```python
percentile = ec.set_index("year").loc[2024]["percentile"] * 100
```

```python
percentile
```

```python
# add exposure estimates

exp_2024 = (
    df_compare.groupby("ADM2_PCODE")["total_exposed"]
    .apply(lambda x: np.percentile(x, percentile))
    .astype(int)
    .to_frame()
    .reset_index()
)
exp_2024["year"] = 2024
df_exp = pd.concat([df_compare, exp_2024])
```

```python
df_compare
```

```python
df_exp
```

```python
df_impact = (
    df_compare[df_compare["ADM2_PCODE"].isin([LOGONE_CHARI, MAYO_DANAY])]
    .pivot(index="year", columns="ADM2_PCODE", values="impact")
    .reset_index()
)
df_exp = (
    df_exp[df_exp["ADM2_PCODE"].isin([LOGONE_CHARI, MAYO_DANAY])]
    .pivot(index="year", columns="ADM2_PCODE", values="total_exposed")
    .reset_index()
)
```

```python
fig, (ax1, ax2, ax3) = plt.subplots(
    3, 1, sharex=True, figsize=(10, 10), dpi=300
)

# impact
barcolor = "crimson"
ax1.bar(
    df_impact["year"],
    df_impact[LOGONE_CHARI],
    label="Logone-et-Chari",
    color=barcolor,
    alpha=1,
)
ax1.bar(
    df_impact["year"],
    df_impact[MAYO_DANAY],
    bottom=df_impact[LOGONE_CHARI],
    label="Mayo-Danay",
    color=barcolor,
    alpha=0.5,
)

ax1.yaxis.set_major_formatter(
    ticker.FuncFormatter(lambda x, pos: "{:,.0f}".format(x).replace(",", " "))
)
ax1.set_ylabel("Population affectée")
ax1.set_title(
    "Comparaison d'impact, exposition aux inondations, et prévisions de précipitations"
)
ax1.legend(title="Département")

# exposure
barcolor = "darkslateblue"
ax2.bar(
    df_exp["year"],
    df_exp[LOGONE_CHARI],
    label="Logone-et-Chari",
    color=barcolor,
    alpha=0.5,
)
ax2.bar(
    df_exp["year"],
    df_exp[MAYO_DANAY],
    bottom=df_exp[LOGONE_CHARI],
    label="Mayo-Danay",
    color=barcolor,
    alpha=0.2,
)

ax2.yaxis.set_major_formatter(
    ticker.FuncFormatter(lambda x, pos: "{:,.0f}".format(x).replace(",", " "))
)


ax2.set_ylabel("Population exposée")
ax2.legend(title="Département", loc="upper left")

ax3.plot(
    ec["year"],
    ec["tprate"],
    marker="o",
    linestyle="-",
    color="dodgerblue",
)

ax3.set_xlabel("Année")
ax3.set_ylabel(
    f"Prévision de précipitations JAS totales\nsur basin Logone-Chari (mm)"
)

# ax2.set_xticks(df_plot["year"])
# ax1.set_xticks(df_plot["year"])
# ax1.xaxis.set_tick_params(labelbottom=True)


for ax in [ax1, ax2, ax3]:
    ax.grid(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xticks(ec["year"])
    ax.set_xticks(ec["year"])
    ax.xaxis.set_tick_params(labelbottom=True, rotation=90)

plt.tight_layout()
plt.show()
```

```python

```
