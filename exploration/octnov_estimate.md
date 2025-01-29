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

# Oct-Nov estimate

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from src.datasources import floodscan, worldpop, codab, ecmwf
from src.constants import *
```

```python
DATE_LT_STR = "m10-l01"
PUB_MONTH_STR = "octobtre"
VALID_MONTHS_STR = "octobre-novembre"

issue_months = [10]
valid_months = [10, 11]
```

```python
adm2 = codab.load_codab(admin_level=2)
```

```python
filter_months = [10, 11]
```

```python
floodscan.calculate_exposure_raster(filter_months=filter_months)
```

```python
floodscan.calculate_adm_exposures(filter_months=filter_months)
```

```python
fs = floodscan.load_adm_flood_exposures(
    admin_level=2, filter_months=filter_months
)
```

```python
fs[fs["ADM2_PCODE"] == LOGONE_CHARI].plot(x="year", y="total_exposed")
```

```python
fs[fs["ADM2_PCODE"] == LOGONE_CHARI]
```

```python
filename = f"cmr_ecmwf_i{issue_months}_v{valid_months}_logone-chari_ranks.csv"
ec = pd.read_csv(ecmwf.ECMWF_PROC_DIR / filename)
```

```python
percentile = ec.set_index("year").loc[2024]["percentile"] * 100
high_percentile, low_percentile = min(percentile + 20, 100), percentile - 20
print(high_percentile, low_percentile)
```

```python
fs_2024 = fs.groupby("ADM2_PCODE").first()

for per, per_label in zip(
    [low_percentile, percentile, high_percentile], ["low", "mid", "high"]
):
    fs_2024[f"{per_label}_exp"] = (
        fs.groupby("ADM2_PCODE")["total_exposed"]
        .apply(lambda x: np.percentile(x, per))
        .astype(int)
    )
    # fs_2024[f"{per_label}_imp"] = fs_2024[f"{per_label}_exp"].apply(
    #     exposed_to_impact
    # )

fs_2024 = fs_2024.drop(columns=["total_exposed", "year"]).reset_index()
```

```python
fs_2024_plot = adm2.merge(fs_2024, on="ADM2_PCODE")
```

```python
# plotting exposure
fig, ax = plt.subplots(figsize=(8, 8), dpi=300)

fs_2024_plot[fs_2024_plot["mid_exp"] > 0].plot(
    column="mid_exp", cmap="Purples", legend=True, ax=ax
)
adm2.boundary.plot(ax=ax, linewidth=0.5, color="k")
ax.set_title(
    "Prévision moyenne de population exposée aux inondations en 2024,\n"
    f"basée sur prévisions ECMWF de {PUB_MONTH_STR} pour {VALID_MONTHS_STR}"
)
cbar = ax.get_figure().get_axes()[1]


def thousands_formatter(x, pos):
    return "{:,.0f}".format(x).replace(",", " ")


cbar.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

ax.axis("off")
```

```python
# table impact
cols = [
    # "ADM1_PCODE",
    "ADM1_FR",
    # "ADM2_PCODE",
    "ADM2_FR",
    # "total_pop",
    "low_exp",
    "mid_exp",
    "high_exp",
    # "geometry",
]
low_label = "Est. exposée bas"
mid_label = "Est. exposée moyen"
high_label = "Est. exposée haut"
fs_2024_plot.sort_values("mid_exp", ascending=False)[cols].iloc[:].rename(
    columns={
        "low_exp": low_label,
        "mid_exp": mid_label,
        "high_exp": high_label,
        "ADM1_FR": "Région",
        "ADM2_FR": "Département",
    }
).style.background_gradient(
    cmap="Purples", vmin=0, vmax=fs_2024_plot["high_exp"].max()
).format(
    "{:,.0f}", subset=[low_label, mid_label, high_label]
)
```

```python

```
