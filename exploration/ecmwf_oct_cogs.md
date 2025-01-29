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

# ECMWF Oct COGs

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import matplotlib.pyplot as plt

from src.datasources import ecmwf, watersheds
from src import blob
from src.utils import upsample_dataarray
```

```python
DATE_LT_STR = "m10-l01"
PUB_MONTH_STR = "octobre"
VALID_MONTHS_STR = "octobre-novembre"
```

```python
adm2 = watersheds.load_logone_chari()
```

```python
valid_months = [10, 11]
issue_months = [10]
ec = ecmwf.open_ecmwf_rasters_from_blob(
    issue_months=issue_months, valid_months=valid_months
)
```

```python
ec
```

```python
ec_year = ec.sum(dim="leadtime").squeeze(drop=True)
ec_year_up = upsample_dataarray(ec_year, lat_dim="y", lon_dim="x")
ec_clip = ec_year_up.rio.clip(adm2.geometry)
```

```python
ec_clip
```

```python
ec_clip = ec_clip.persist()
```

```python
ec_mean = ec_clip.mean(dim=["x", "y"])
```

```python
ec_df = ec_mean.to_dataframe("mean")["mean"].reset_index()
```

```python
ec_df["rank"] = ec_df["mean"].rank()
ec_df["percentile"] = ec_df["mean"].rank(pct=True)
ec_df
```

```python
filename = f"cmr_ecmwf_i{issue_months}_v{valid_months}_logone-chari_ranks.csv"
ec_df.to_csv(ecmwf.ECMWF_PROC_DIR / filename, index=False)
```

## Plotting

```python
ec_adm = ec_clip * 30
```

```python
ec_adm.isel(year=0).plot()
```

```python
ec_anom = (ec_adm - ec_adm.mean(dim="year")) / ec_adm.mean(dim="year") * 100
```

```python
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
adm2.boundary.plot(ax=ax, color="white", linewidth=1)
ec_adm.sel(year=2024).plot(
    ax=ax, cbar_kwargs={"label": "Précipitations totales prévues (mm)"}
)
ax.axis("off")
ax.set_title(
    f"Prévisions ECMWF 2024 Logone et Chari\n"
    f"mois de publication: {PUB_MONTH_STR},\npériode d'interêt: {VALID_MONTHS_STR}"
)

fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
adm2.boundary.plot(ax=ax, color="k", linewidth=1)
ec_anom.sel(year=2024).plot(
    ax=ax,
    cmap="RdBu",
    vmax=float(ec_anom.sel(year=2024).max()),
    vmin=-float(ec_anom.sel(year=2024).max()),
    cbar_kwargs={"label": "Anomalie de précipitations totales prévues (%)"},
)
ax.axis("off")
ax.set_title(
    f"Prévisions ECMWF 2024 Logone et Chari\n"
    f"mois de publication: {PUB_MONTH_STR},\npériode d'interêt: {VALID_MONTHS_STR}"
)

df_adm = (
    ec_adm.mean(dim=["x", "y"]).to_dataframe("tprate")["tprate"].reset_index()
)

thresh = df_adm["tprate"].quantile(2 / 3)

fig, ax = plt.subplots(dpi=300)
df_adm.plot(x="year", y="tprate", ax=ax, legend=False, linewidth=1)
ax.plot([2024], [df_adm.iloc[-1]["tprate"]], ".r")
ax.annotate(
    "2024",
    xy=(2024, df_adm.iloc[-1]["tprate"]),
    color="red",
    ha="center",
    va="top",
)
ax.axhline(y=thresh, color="grey", linestyle="--")
ax.annotate(
    " seuil\n 1-an-sur-3",
    xy=(2026, thresh),
    color="grey",
    ha="left",
    va="center",
)

ax.set_xlabel("Année")
ax.set_ylabel(
    "Précipitations totales prévues,\nmoyenne sur tout le bassin (mm)"
)
ax.set_title(
    f"Prévisions ECMWF historiques Logone et Chari\n"
    f"mois de publication: {PUB_MONTH_STR}, période d'interêt: {VALID_MONTHS_STR}"
)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
```

```python
df_adm["rank"] = df_adm["tprate"].rank(ascending=False).astype(int)
df_adm["percentile"] = df_adm["tprate"].rank(ascending=True, pct=True)
df_adm["rp"] = len(df_adm) / df_adm["rank"]
```

```python
df_adm.sort_values("rp")
```

```python
fig, ax = plt.subplots(dpi=300)
df_adm.sort_values("rp").plot(x="rp", y="tprate", ax=ax)

rp_2023, val_2023, per_2023 = df_adm.set_index("year").loc[2024][
    ["rp", "tprate", "percentile"]
]
ax.plot(rp_2023, val_2023, "r.")
annotation = (
    f" 2024:\n Période ret. = {rp_2023:.1f} ans\n "
    f"Valeur = {val_2023:.0f} mm\n Centile = {per_2023:.2f}"
)
ax.annotate(
    annotation,
    (rp_2023, val_2023),
    color="red",
    va="top",
    ha="left",
)
ax.set_title(
    "Période de retour de prévisions ECMWF Logone et Chari\n"
    f"mois de publication: {PUB_MONTH_STR}, période d'interêt: {VALID_MONTHS_STR}"
)
ax.set_xlabel("Période de retour (ans)")
ax.set_ylabel(
    "Précipitations totales prévues,\nmoyenne sur tout le bassin (mm)"
)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.autoscale(enable=True, axis="both", tight=True)
# ax.set_xlim(1, 10)
# ax.set_ylim(top=105)
ax.get_legend().remove()
```

```python

```
