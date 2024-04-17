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

# ECMWF historical

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import matplotlib.pyplot as plt

from src.datasources import codab, ecmwf
from src.utils import upsample_dataarray
```

```python
DATE_LT_STR = "m4-l456"
PUB_MONTH_STR = "avril"
VALID_MONTHS_STR = "juillet-août-septembre"
```

```python
# codab.download_codab()
```

```python
adm2 = codab.load_codab(admin_level=2)
```

```python
adm2.plot()
```

```python
lon_min, lat_min, lon_max, lat_max = adm2.total_bounds
```

```python
print(adm2.total_bounds)
```

```python
date_lt_str = "m4-l456"
ec_members = ecmwf.load_ecmwf_specific_cmr(DATE_LT_STR)
```

```python
ec_members["latitude"].values
```

```python
ec_members["longitude"].values
```

```python
ec_members
```

```python
ax = adm2.boundary.plot(color="k")
ec_members["tprate"].isel(number=0, time=0, step=0).plot(ax=ax)
```

```python
ec_year = (
    ec_members.mean(dim="number").groupby("time.year").sum().sum(dim="step")
)
ec_year = ec_year.rio.write_crs(4326)["tprate"]
ec_year *= 3600 * 24 * 1000 * 30
```

```python
ec_year.mean(dim=["latitude", "longitude"]).plot()
```

```python
ec_year_up = upsample_dataarray(ec_year)
```

```python
ec_adm = ec_year_up.rio.clip(adm2.geometry, all_touched=True)
```

```python
ec_anom = (ec_adm - ec_adm.mean(dim="year")) / ec_adm.mean(dim="year") * 100
```

```python
fig, ax = plt.subplots(figsize=(10, 5))
adm2.boundary.plot(ax=ax, color="white", linewidth=0.5)
ec_adm.sel(year=2024).plot(
    ax=ax, cbar_kwargs={"label": "Précipitations totales prévues (mm)"}
)
ax.axis("off")
ax.set_title(
    f"Prévisions ECMWF 2024 Cameroun\n"
    f"mois de publication: {PUB_MONTH_STR},\npériode d'interêt: {VALID_MONTHS_STR}"
)

fig, ax = plt.subplots(figsize=(10, 5))
adm2.boundary.plot(ax=ax, color="k", linewidth=0.5)
ec_anom.sel(year=2024).plot(
    ax=ax,
    cmap="RdBu",
    cbar_kwargs={"label": "Anomalie de précipitations totales prévues (%)"},
)
ax.axis("off")
ax.set_title(
    f"Prévisions ECMWF 2024 Cameroun\n"
    f"mois de publication: {PUB_MONTH_STR},\npériode d'interêt: {VALID_MONTHS_STR}"
)

df_adm = (
    ec_adm.mean(dim=["latitude", "longitude"])
    .to_dataframe()["tprate"]
    .reset_index()
)

thresh = df_adm["tprate"].quantile(2 / 3)

fig, ax = plt.subplots()
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
ax.set_ylabel("Précipitations totales prévues,\nmoyenne sur tout pays (mm)")
ax.set_title(
    f"Prévisions ECMWF historiques Cameroun\n"
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
fig, ax = plt.subplots()
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
    "Période de retour de prévisions ECMWF Cameroun\n"
    f"mois de publication: {PUB_MONTH_STR}, période d'interêt: {VALID_MONTHS_STR}"
)
ax.set_xlabel("Période de retour (ans)")
ax.set_ylabel("Précipitations totales prévues,\nmoyenne sur tout pays (mm)")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.autoscale(enable=True, axis="both", tight=True)
ax.set_xlim(1, 10)
# ax.set_ylim(top=665)
ax.set_ylim(top=719)
ax.get_legend().remove()
```

```python
df_adm
```

```python
filename = f"cmr_ecmwf_{DATE_LT_STR}_ranks.csv"
df_adm.to_csv(ecmwf.ECMWF_PROC_DIR / filename, index=False)
```

```python

```
