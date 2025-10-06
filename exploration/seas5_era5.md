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

# SEAS5-ERA5

Plot SEAS5 and ERA5 together to check skill

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import calendar

import ocha_stratus as stratus
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

from src.constants import *
from src.datasources import seas5, era5, emdat
from src.utils import detrend_column
```

```python
pcode = EXTREMENORD
```

```python
query = f"SELECT * FROM public.polygon WHERE pcode = '{pcode}'"
df_adm = pd.read_sql(query, stratus.get_engine(stage="prod"))
adm_name = df_adm.iloc[0]["name"]
```

```python
adm_name
```

## Load data

### Exposure

```python
query = f"SELECT * FROM app.floodscan_exposure WHERE pcode = '{pcode}'"
```

```python
df_exp_daily = pd.read_sql(
    query, stratus.get_engine(stage="prod"), parse_dates=["valid_date"]
)
```

```python
df_exp_yearly = (
    df_exp_daily.groupby(df_exp_daily["valid_date"].dt.year)["sum"]
    .agg(["mean", "max", "min"])
    .reset_index()
)
df_exp_yearly["max_diff"] = df_exp_yearly["max"] - df_exp_yearly["min"]
df_exp_yearly["mean_diff"] = df_exp_yearly["mean"] - df_exp_yearly["min"]
```

```python
df_exp_yearly["max_prev"] = df_exp_yearly["max"].shift()
df_exp_yearly["mean_prev"] = df_exp_yearly["mean"].shift()
```

```python
window = 3
df_exp_yearly[f"mean_roll{window}"] = (
    df_exp_yearly["mean"].rolling(window).mean()
)
df_exp_yearly[f"max_diff_mean_roll{window}"] = (
    df_exp_yearly["max"] / df_exp_yearly[f"mean_roll{window}"]
)
```

```python
df_exp_yearly.set_index("valid_date").plot()
```

```python
df_exp_yearly = df_exp_yearly.rename(
    columns={
        x: f"{x}_exp"
        for x in df_exp_yearly.columns
        if x != "valid_date" and "exp" not in x
    }
)
```

```python
df_exp_yearly = df_exp_yearly[df_exp_yearly["valid_date"] < 2025]
```

### SEAS5

Load and filter SEAS5 data to specific `issued_month`.

```python
df_seas5_all = seas5.load_seas5(pcode=pcode)
```

```python
issued_month = 6
issued_mo_str = calendar.month_abbr[issued_month]
df_seas5_imo = df_seas5_all[
    df_seas5_all["issued_date"].dt.month == issued_month
]
```

```python
valid_months_override = [7, 8, 9]
df_seas5_imo = df_seas5_imo[
    df_seas5_imo["valid_date"].dt.month.isin(valid_months_override)
]
```

```python
valid_months = sorted(df_seas5_imo["valid_date"].dt.month.unique())
valid_mo_str = "".join([calendar.month_abbr[x][0] for x in valid_months])
valid_mo_str
```

```python
df_seas5_yearly = (
    df_seas5_imo.groupby(df_seas5_imo["valid_date"].dt.year)["mean"]
    .mean()
    .reset_index()
)
```

```python
df_seas5_yearly = detrend_column(df_seas5_yearly, col="mean", max_index=2024)
# df_seas5_yearly = detrend_column(
#     df_seas5_yearly, col="mean", min_index=2000, max_index=2024
# )
```

```python
ax = df_seas5_yearly.set_index("valid_date").plot()
ax.set_title("seas5")
```

```python
df_seas5_yearly
```

```python
df_seas5_monthwise = df_seas5_imo.copy()
df_seas5_monthwise["valid_month"] = df_seas5_monthwise["valid_date"].dt.month
df_seas5_monthwise["valid_year"] = df_seas5_monthwise["valid_date"].dt.year
df_seas5_monthwise = df_seas5_monthwise.pivot(
    index="valid_year", columns="valid_month", values="mean"
)
df_seas5_monthwise = df_seas5_monthwise.rename(
    columns={x: f"mean_seas5_mo{x}" for x in df_seas5_monthwise.columns}
).reset_index()
df_seas5_monthwise
```

### ERA5

Load and filter ERA5 data to same `valid_months` as SEAS5.

```python
df_era5 = era5.load_era5(pcode=pcode)
```

```python
df_era5_yearly = (
    df_era5[df_era5["valid_date"].dt.month.isin(valid_months)]
    .groupby(df_era5["valid_date"].dt.year)["mean"]
    .mean()
    .reset_index()
)
df_era5_yearly = df_era5_yearly[df_era5_yearly["valid_date"] < 2025]
```

```python
df_era5_yearly = detrend_column(df_era5_yearly, "mean")
# df_era5_yearly = detrend_column(df_era5_yearly, "mean", min_index=2000)
```

```python
ax = df_era5_yearly.set_index("valid_date").plot()
ax.set_title("era5")
```

```python
df_era5_yearly
```

#### Month-wise

```python
df_era5
```

```python
df_era5_monthwise = df_era5[df_era5["valid_date"].dt.year < 2025].copy()
df_era5_monthwise["valid_month"] = df_era5_monthwise["valid_date"].dt.month
df_era5_monthwise["valid_year"] = df_era5_monthwise["valid_date"].dt.year
df_era5_monthwise = df_era5_monthwise.pivot(
    index="valid_year", columns="valid_month", values="mean"
)
df_era5_monthwise = df_era5_monthwise.rename(
    columns={x: f"mean_era5_mo{x}" for x in df_era5_monthwise.columns}
).reset_index()
for col in df_era5_monthwise:
    if col == "valid_year":
        continue
    df_era5_monthwise = detrend_column(
        df_era5_monthwise, col, index_col="valid_year"
    )
```

### EM-DAT

```python
df_emdat_events = emdat.load_emdat_from_global()
```

```python
df_emdat_events
```

```python
df_emdat_yearly = (
    df_emdat_events.groupby("Start Year")["Total Affected"].sum().reset_index()
)
```

```python
# Ensure Start Year is the index
df_emdat_yearly = df_emdat_yearly.set_index("Start Year")

# Reindex to fill in all years 2000–2024
df_emdat_yearly = df_emdat_yearly.reindex(range(2000, 2025), fill_value=0)

# Reset index if you want to plot with "Start Year" as a column
df_emdat_yearly = df_emdat_yearly.reset_index().rename(
    columns={"index": "Start Year"}
)
df_emdat_yearly["Total Affected"] = df_emdat_yearly["Total Affected"].astype(
    int
)
```

```python
df_emdat_yearly
```

```python
df_emdat_yearly.plot(x="Start Year", y="Total Affected", kind="bar")
```

## Combine

```python
df_compare_full = (
    df_exp_yearly.merge(
        df_era5_yearly.rename(
            columns={
                "mean": "mean_era5",
                "mean_detrended": "mean_era5_detrended",
            }
        ),
        how="outer",
    )
    .merge(
        df_seas5_yearly,
        how="outer",
    )
    .rename(
        columns={
            "mean": "mean_seas5",
            "mean_detrended": "mean_seas5_detrended",
        }
    )
    .merge(
        df_emdat_yearly.rename(
            columns={
                "Start Year": "valid_date",
                "Total Affected": "total_affected",
            }
        ),
        how="outer",
    )
).rename(columns={"valid_date": "year"})
df_compare_full["cerf"] = df_compare_full["year"].isin(CERF_YEARS)
df_compare = df_compare_full[
    (df_compare_full["year"] < 2025) & (df_compare_full["year"] >= 2000)
].copy()
df_compare
```

```python

```

## Analysis

### Correlations

```python
df_compare_full.set_index("year").corr()[
    [x for x in df_compare_full.columns if "5" in x]
]
```

```python
def plot_comparison(df, xcol, ycol, sizecol=None, labels=None, rotation=0):
    df = df.copy()
    fig, ax = plt.subplots(dpi=200, figsize=(7, 7))

    # Replace NaN sizes with a small value
    if sizecol is None:
        sizes = np.full(len(df), 0)
    else:
        sizes = df[sizecol].fillna(0) / df[sizecol].max() * 1000

    # Set colors based on cerf
    df["color"] = df["cerf"].map({True: "crimson", False: "royalblue"})

    scatter = ax.scatter(
        df[xcol], df[ycol], s=sizes, c=df["color"], alpha=0.5, edgecolor="none"
    )

    # Annotate year on each point
    for year, row in df.set_index("year").iterrows():
        ax.annotate(
            str(year),
            (row[xcol], row[ycol]),
            fontsize=8,
            ha="center",
            va="center",
            color=row["color"],
            rotation=rotation,
        )

    if labels is None:
        ax.set_xlabel(xcol)
        ax.set_ylabel(ycol)
        ax.set_title("")
    else:
        ax.set_xlabel(labels["x"])
        ax.set_ylabel(labels["y"])
        ax.set_title(labels["title"])

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return fig, ax
```

```python

```

```python
fig, ax = plot_comparison(
    df_compare,
    "mean_seas5_detrended",
    "mean_era5_detrended",
    sizecol="total_affected",
)

current_pred = df_compare_full.set_index("year").loc[
    2025, "mean_seas5_detrended"
]
ax.axvline(
    current_pred,
    color="mediumorchid",
    linestyle="--",
)
ax.annotate(
    "2025 forecast",
    (current_pred, df_compare["mean_era5_detrended"].min()),
    rotation=90,
    va="bottom",
    ha="right",
    color="mediumorchid",
)

ax.set_title(
    f"Detrended observations vs. forecast ({adm_name}, {valid_mo_str})"
)
ax.set_ylabel(f"Observed mean daily rainfall, detrended (mm) [ERA5]")
ax.set_xlabel(
    f"Forecasted mean daily rainfall, detrended, issued {issued_mo_str} (mm) [SEAS5]"
)
```

```python
fig, ax = plot_comparison(
    df_compare_full,
    "mean_seas5_detrended",
    "mean_era5_detrended",
    sizecol="total_affected",
)

current_pred = df_compare_full.set_index("year").loc[
    2025, "mean_seas5_detrended"
]
ax.axvline(
    current_pred,
    color="mediumorchid",
    linestyle="--",
)
ax.annotate(
    "2025 forecast",
    (current_pred, df_compare_full["mean_era5_detrended"].max()),
    rotation=90,
    va="top",
    ha="right",
    color="mediumorchid",
)

ax.set_title(
    f"Detrended observations vs. forecast ({adm_name}, {valid_mo_str})"
)
ax.set_ylabel(f"Observed mean daily rainfall, detrended (mm) [ERA5]")
ax.set_xlabel(
    f"Forecasted mean daily rainfall, detrended, issued {issued_mo_str} (mm) [SEAS5]"
)
```

```python
fig, ax = plot_comparison(
    df_compare_full,
    "mean_seas5_detrended",
    "max_exp",
    sizecol="total_affected",
)

current_pred = df_compare_full.set_index("year").loc[
    2025, "mean_seas5_detrended"
]
ax.axvline(
    current_pred,
    color="mediumorchid",
    linestyle="--",
)
ax.annotate(
    "2025 forecast",
    (current_pred, df_compare_full["max_exp"].max()),
    rotation=90,
    va="top",
    ha="right",
    color="mediumorchid",
)

ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

ax.set_title(
    f"Detrended observations vs. forecast ({adm_name}, {valid_mo_str})"
)
ax.set_ylabel("Estimated people exposed to flooding [Floodscan, WorldPop]")
ax.set_xlabel(
    f"Forecasted mean daily rainfall, detrended, issued {issued_mo_str} (mm) [SEAS5]"
)
```

```python

```

```python

```
