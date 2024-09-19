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

# Impact 2024

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

from tqdm.auto import tqdm

from src.datasources import impact, codab, floodscan
from src import blob
from src.constants import *
```

```python
adm = codab.load_codab(admin_level=3)
```

```python
start_date_str = "2024-07-01"
end_date_str = "2024-09-15"
dates = pd.date_range(start_date_str, end_date_str)
```

```python
das = []
for date in tqdm(dates):
    blob_name = floodscan.get_blob_name(
        "cmr", data_type="exposure_raster", date=date.date()
    )
    da_in = blob.open_blob_cog(blob_name)
    da_in["date"] = date
    das.append(da_in)
```

```python
da_exp = xr.concat(das, dim="date").squeeze(drop=True)
```

```python
da_exp_max = da_exp.max(dim="date")
```

```python
# calculate daily raster stats
dfs = []
for pcode, row in tqdm(adm.set_index("ADM3_PCODE").iterrows(), total=len(adm)):
    da_clip = da_exp.rio.clip([row.geometry])
    df_in = (
        da_clip.sum(dim=["x", "y"])
        .to_dataframe("total_exposed")["total_exposed"]
        .reset_index()
    )
    df_in["ADM3_PCODE"] = pcode
    dfs.append(df_in)
```

```python
# calculate raster stats of max
dicts = []
for pcode, row in tqdm(adm.set_index("ADM3_PCODE").iterrows(), total=len(adm)):
    dicts.append(
        {
            "ADM3_PCODE": pcode,
            "total_exposed": float(
                da_exp_max.rio.clip([row.geometry]).sum(dim=["x", "y"])
            ),
        }
    )
```

```python
df_max_exp = pd.DataFrame(dicts)
```

```python
df_max_exp
```

```python
df_exp = pd.concat(dfs, ignore_index=True)
df_exp = df_exp.merge(adm[[f"ADM{x}_PCODE" for x in range(1, 4)]])
```

```python
df_exp.groupby(["date", "ADM2_PCODE"])[
    "total_exposed"
].sum().reset_index().set_index("ADM2_PCODE").loc[LOGONE_CHARI].plot(
    x="date", y="total_exposed"
)
```

```python
df_exp_max = df_exp.groupby("ADM3_PCODE").max()["total_exposed"].reset_index()
```

```python
df_exp_max
```

```python
impact_col = "# personnes affectées"

df = impact.load_impact_2024()
df = df.merge(
    adm[["ADM3_PCODE", "ADM2_PCODE", "ADM1_PCODE", "ADM3_FR", "ADM2_FR"]]
)
df = df.rename(columns={impact_col: "total_affected"})
df = df.dropna(subset=["total_affected"])
df["total_affected"] = df["total_affected"].astype(int)
```

```python
# df = df.merge(df_exp_max)
df = df.merge(df_max_exp)
df
```

```python
def thousands_formatter(x, pos):
    return f"{int(x/1000)}k"
```

```python
df[df["ADM2_PCODE"] == MAYO_DANAY]
```

```python
df["exp_error"] = df["total_exposed"] - df["total_affected"]
```

```python
fig, ax = plt.subplots(dpi=200, figsize=(8, 8))
adm.merge(df[df["ADM1_PCODE"] == EXTREMENORD], on="ADM3_PCODE").plot(
    column="total_affected",
    legend=True,
    cmap="Reds",
    ax=ax,
)
adm[adm["ADM1_PCODE"] == EXTREMENORD].boundary.plot(
    ax=ax, linewidth=0.2, color="k"
)
ax.axis("off")
cbar = ax.get_figure().get_axes()[1]

cbar.yaxis.set_major_formatter(mticker.FuncFormatter(thousands_formatter))
cbar.set_ylabel(impact_col)
ax.set_title("Impact 2024 jusqu'à fin août\npar commune")
```

```python
fig, ax = plt.subplots(dpi=200, figsize=(8, 8))
adm[adm["ADM1_PCODE"] == EXTREMENORD].dissolve("ADM2_PCODE").merge(
    df, on="ADM2_PCODE"
).dissolve("ADM2_PCODE", aggfunc="sum").plot(
    column="total_affected",
    legend=True,
    cmap="Reds",
    ax=ax,
)
adm[adm["ADM1_PCODE"] == EXTREMENORD].dissolve("ADM2_PCODE").boundary.plot(
    ax=ax, linewidth=0.2, color="k"
)
ax.axis("off")
cbar = ax.get_figure().get_axes()[1]

cbar.yaxis.set_major_formatter(mticker.FuncFormatter(thousands_formatter))
cbar.set_ylabel(impact_col)
ax.set_title("Impact 2024 jusqu'à fin août\npar département")
```

```python
adm[adm["ADM1_PCODE"] == EXTREMENORD].dissolve("ADM2_PCODE")
```

```python
adm[adm["ADM1_PCODE"] == EXTREMENORD].dissolve("ADM2_PCODE").merge(
    df, on="ADM2_PCODE"
).dissolve("ADM2_PCODE", aggfunc="sum")
```

```python
df_plot = df.copy()

max_val = df_plot[["total_affected", "total_exposed"]].max().max() * 1.1

fig, ax = plt.subplots(dpi=200, figsize=(6, 6))
for adm_name, group in df_plot.groupby("ADM2_FR"):
    group.plot(
        x="total_exposed",
        y="total_affected",
        linewidth=0,
        marker=".",
        ax=ax,
        label=adm_name,
    )

ax.plot([0, max_val], [0, max_val], color="grey", linestyle="--")
ax.set_ylim(bottom=0, top=max_val)
ax.set_xlim(left=0, right=max_val)
ax.set_aspect("equal")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(thousands_formatter))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(thousands_formatter))
ax.set_ylabel("Population totale affectée")
ax.set_xlabel("Population totale exposée")
ax.set_title(
    "Comparaison d'impact et exposition en 2024\npar Commune, jusqu'à 15 sept."
)
```

```python
df_plot = df.groupby("ADM2_FR").sum(numeric_only=True)

max_val = df_plot[["total_affected", "total_exposed"]].max().max() * 1.1

fig, ax = plt.subplots(dpi=200, figsize=(6, 6))
for adm_name, group in df_plot.groupby("ADM2_FR"):
    group.plot(
        x="total_exposed",
        y="total_affected",
        linewidth=0,
        marker=".",
        ax=ax,
        label=adm_name,
    )
ax.plot([0, max_val], [0, max_val], color="grey", linestyle="--")
ax.set_ylim(bottom=0, top=max_val)
ax.set_xlim(left=0, right=max_val)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_xlabel("")
ax.set_aspect("equal")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(thousands_formatter))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(thousands_formatter))
ax.set_ylabel("Population totale affectée")
ax.set_xlabel("Population totale exposée")
ax.set_title(
    "Comparaison d'impact et exposition en 2024\npar Département, jusqu'à 15 sept."
)
```

```python
df_plot
```
