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

# Specific admin2s

Just looking at Logone-et-Chari and Mayo-Danay

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

from src.datasources import ecmwf, impact, floodscan, codab, watersheds
from src.constants import *
```

```python
DATE_LT_STR = "m7-l123"
PUB_MONTH_STR = "juillet"
VALID_MONTHS_STR = "juillet-août-septembre"
```

```python
filename = "cmr_adm2_impact_exposed.csv"
impact_exposure = pd.read_csv(impact.IMPACT_PROC_DIR / filename)
```

```python
impact_exposure
```

```python
fs = floodscan.load_adm_flood_exposures(admin_level=2)
```

```python
filename = f"cmr_ecmwf_{DATE_LT_STR}_logone-chari_ranks.csv"
ec = pd.read_csv(ecmwf.ECMWF_PROC_DIR / filename)
```

```python
df_plot = (
    fs[fs["ADM2_PCODE"].isin([LOGONE_CHARI, MAYO_DANAY])]
    .pivot(index="year", columns="ADM2_PCODE", values="total_exposed")
    .reset_index()
)
df_plot = df_plot.merge(ec[["year", "tprate"]], how="outer")
df_plot = df_plot[df_plot["year"] >= 2010]
```

```python
df_plot
```

```python
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(8, 8), dpi=100)
# fig, ax1 = plt.subplots(figsize=(8, 4), dpi=100)
# fig2, ax2 = plt.subplots(figsize=(8, 4), dpi=100)

barcolor = "darkslateblue"
ax1.bar(
    df_plot["year"],
    df_plot[LOGONE_CHARI],
    label="Logone-et-Chari",
    color=barcolor,
    alpha=0.5,
)
ax1.bar(
    df_plot["year"],
    df_plot[MAYO_DANAY],
    bottom=df_plot[LOGONE_CHARI],
    label="Mayo-Danay",
    color=barcolor,
    alpha=0.2,
)

ax1.yaxis.set_major_formatter(
    ticker.FuncFormatter(lambda x, pos: "{:,.0f}".format(x))
)


ax1.set_ylabel("Population exposée")
ax1.set_title(
    "Comparaison d'exposition aux inondations et prévisions de précipitations"
)
ax1.legend(title="Département")

ax2.plot(
    df_plot["year"],
    df_plot["tprate"],
    marker="o",
    linestyle="-",
    color="dodgerblue",
)

logone_impact = impact_exposure.set_index("ADM2_PCODE").loc[
    LOGONE_CHARI, "Total personne affecté"
]
mayo_impact = impact_exposure.set_index("ADM2_PCODE").loc[
    MAYO_DANAY, "Total personne affecté"
]
ax1.plot(
    [2022, 2022],
    [logone_impact, 0],
    linestyle="-",
    color="crimson",
    linewidth=10,
)
ax1.plot(
    [2022, 2022],
    [mayo_impact + logone_impact, logone_impact],
    linestyle="-",
    color="salmon",
    linewidth=10,
)
ax1.annotate(
    "Impact\nréel",
    xy=(2022, 250000),
    xytext=(2020, 350000),
    arrowprops=dict(
        color="crimson",
        arrowstyle="-",
    ),
    fontsize=12,
    ha="center",
    color="crimson",
)

ax2.set_xlabel("Année")
ax2.set_ylabel(
    f"Prévision de précipitations JAS totales\nsur basin Logone-Chari (mm)"
)

ax2.set_xticks(df_plot["year"])
ax1.set_xticks(df_plot["year"])
ax1.xaxis.set_tick_params(labelbottom=True)


for ax in [ax1, ax2]:
    ax.grid(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.show()
```

```python
df_plot["tprate"].rank(pct=True)
```

```python

```

```python

```

```python

```
