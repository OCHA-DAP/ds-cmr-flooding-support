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

# Impact data

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from src.datasources import impact, codab, floodscan
from src.utils import thousands_space
```

```python
impact.process_impact_2022()
```

```python
df = impact.load_processed_impact_2022()
```

```python
df_agg = df.groupby("ADM3_PCODE").sum(numeric_only=True).reset_index()
```

```python
adm3 = codab.load_codab(admin_level=3)
adm3_aoi = adm3[adm3["ADM1_PCODE"] == "CM004"]
adm2 = codab.load_codab(admin_level=2)
adm2_aoi = adm2[adm2["ADM1_PCODE"] == "CM004"]
```

```python
df_plot = adm3_aoi.merge(df_agg, on="ADM3_PCODE")
```

```python
df_plot["ADM2_PCODE"].unique()
```

```python
filename = "cmr_adm3_average_flood_exposed.csv"
exposure = pd.read_csv(floodscan.PROC_FS_DIR / filename)
exposure
```

```python
fig, ax = plt.subplots(figsize=(8, 8))
df_plot.plot(column="Total personne affecté", legend=True, ax=ax, cmap="Reds")
adm3[adm3["ADM1_PCODE"] == "CM004"].boundary.plot(
    ax=ax, linewidth=0.5, color="k"
)
ax.axis("off")
ax.set_title(
    "Personnes affectés par inondations 2022\nRégion: Extrême-Nord, par Commune"
)
```

```python
df_plot2 = adm3_aoi.merge(
    df.groupby("ADM2_PCODE").sum(numeric_only=True).reset_index(),
    on="ADM2_PCODE",
)

fig, ax = plt.subplots(figsize=(8, 8))
df_plot2.plot(column="Total personne affecté", legend=True, ax=ax, cmap="Reds")
adm2_aoi.boundary.plot(ax=ax, linewidth=0.5, color="k")
ax.axis("off")
ax.set_title(
    "Personnes affectés par inondations 2022\nDépartement: Extrême-Nord, par Commune"
)
```

```python
compare = df_plot.merge(exposure, on="ADM3_PCODE")
# compare = compare.fillna(0)
```

```python
compare
```

```python
fig, ax = plt.subplots()
compare.plot(
    y="Total personne affecté", x="total_exposed", ax=ax, kind="scatter"
)
for _, row in compare.iterrows():
    ax.annotate(
        f'  {row["ADM3_FR"]}',
        xy=(row["total_exposed"], row["Total personne affecté"]),
        ha="left",
        va="center",
        fontsize=8,
    )

ax.set_ylabel("Nombre de personnes affectées (mesuré)")
ax.set_xlabel("Nombre de personnes exposées (estimé)")
ax.set_title(
    "Comparaison de personnes affectées et exposées\n"
    "Inondations 2022, par Commune"
)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_xlim(left=0)
ax.set_ylim(bottom=0)
ax.xaxis.set_major_formatter(FuncFormatter(thousands_space))
ax.yaxis.set_major_formatter(FuncFormatter(thousands_space))
```

```python
fig, ax = plt.subplots()

compare_adm2 = (
    compare.groupby(["ADM2_PCODE", "ADM2_FR"])
    .sum(numeric_only=True)
    .reset_index()
)

x, y = compare_adm2[["total_exposed", "Total personne affecté"]].values.T
slope, intercept = np.polyfit(x, y, 1)
y_trend = slope * x + intercept
plt.annotate(
    f"y = {slope:.2f}x + {intercept:.2f}", xy=(150000, 150000), color="grey"
)

ax.plot(x, y_trend, color="grey", label="Trendline", linewidth=0.5)

compare_adm2.plot(
    y="Total personne affecté", x="total_exposed", ax=ax, kind="scatter"
)
for _, row in compare_adm2.iterrows():
    ax.annotate(
        f'  {row["ADM2_FR"]}',
        xy=(row["total_exposed"], row["Total personne affecté"]),
        ha="left",
        va="center",
        fontsize=8,
    )

ax.set_ylabel("Nombre de personnes affectées (mesuré)")
ax.set_xlabel("Nombre de personnes exposées (estimé)")
ax.set_title(
    "Comparaison de personnes affectées et exposées\n"
    "Inondations 2022, par Département"
)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_xlim(left=0, right=250000)
ax.set_ylim(bottom=0)
ax.xaxis.set_major_formatter(FuncFormatter(thousands_space))
ax.yaxis.set_major_formatter(FuncFormatter(thousands_space))
```

```python
filename = "cmr_adm2_impact_exposed.csv"
compare_adm2.to_csv(impact.IMPACT_PROC_DIR / filename, index=False)
```
