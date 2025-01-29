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

# Flooding Exposure

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import matplotlib.pyplot as plt
import pandas as pd

from src.datasources import worldpop, codab, floodscan
from src.constants import *
```

```python
# worldpop.aggregate_worldpop_to_adm(admin_level=3)
# worldpop.aggregate_worldpop_to_adm(admin_level=2)
# worldpop.aggregate_worldpop_to_adm(admin_level=1)
```

```python
# floodscan.clip_cmr_from_glb()
```

```python
# floodscan.calculate_exposure_raster()
```

```python
# for admin_level in range(1, 4):
#     floodscan.calculate_adm_exposures(admin_level=admin_level)
```

```python
adm3 = codab.load_codab(admin_level=3)
adm2 = codab.load_codab(admin_level=2)
adm3_aoi = adm3[adm3["ADM1_PCODE"].isin(ADM1_FLOOD_PCODES)]
adm2_aoi = adm2[adm2["ADM1_PCODE"].isin(ADM1_FLOOD_PCODES)]
adm3_aoi_en = adm3[adm3["ADM1_PCODE"] == "CM004"]
```

```python
pop = worldpop.load_raw_worldpop()
pop_aoi = pop.rio.clip(adm2_aoi.geometry, all_touched=True)
pop_aoi = pop_aoi.where(pop_aoi > 0)
```

```python
fs_raster = floodscan.load_raw_cmr_floodscan()
fs_raster = fs_raster.rio.write_crs(4326)
fs_aoi = fs_raster.rio.clip(adm3_aoi.geometry, all_touched=True)

fs_aoi_year = fs_aoi.groupby("time.year").max()
fs_aoi_mean = fs_aoi_year.mean(dim="year")

fs_year = fs_raster.groupby("time.year").max()
fs_mean = fs_year.mean(dim="year")
```

```python
adm2_pop = worldpop.load_adm_worldpop(admin_level=2)
adm3_pop = worldpop.load_adm_worldpop(admin_level=3)
```

```python
adm2_pop.hist(bins=20)
```

```python
adm3_pop.hist(bins=20)
```

```python
exposure2 = floodscan.load_adm_flood_exposures(admin_level=2)
exposure2 = exposure2.merge(adm2_pop, on="ADM2_PCODE")
exposure2["frac_exposed"] = exposure2["total_exposed"] / exposure2["total_pop"]
avg_exposure2 = (
    exposure2.groupby("ADM2_PCODE").mean().reset_index().drop(columns=["year"])
)
int_cols = ["total_exposed", "total_pop"]
avg_exposure2[int_cols] = avg_exposure2[int_cols].astype(int)
avg_exposure_plot2 = adm2.merge(avg_exposure2, on="ADM2_PCODE")
avg_exposure_plot_aoi2 = avg_exposure_plot2[
    avg_exposure_plot2["ADM1_PCODE"].isin(ADM1_FLOOD_PCODES)
]

exposure3 = floodscan.load_adm_flood_exposures(admin_level=3)
exposure3 = exposure3.merge(adm3_pop, on="ADM3_PCODE")
exposure3["frac_exposed"] = exposure3["total_exposed"] / exposure3["total_pop"]
avg_exposure3 = (
    exposure3.groupby("ADM3_PCODE").mean().reset_index().drop(columns=["year"])
)
int_cols = ["total_exposed", "total_pop"]
avg_exposure3[int_cols] = avg_exposure3[int_cols].astype(int)
avg_exposure_plot3 = adm3.merge(avg_exposure3, on="ADM3_PCODE")
avg_exposure_plot_aoi3 = avg_exposure_plot3[
    avg_exposure_plot3["ADM1_PCODE"].isin(ADM1_FLOOD_PCODES)
]
avg_exposure_plot_aoi_en3 = avg_exposure_plot3[
    avg_exposure_plot3["ADM1_PCODE"] == "CM004"
]
```

```python
exposure1 = floodscan.load_adm_flood_exposures(admin_level=1)
```

```python
exposure1[exposure1["ADM1_PCODE"].isin(ADM1_FLOOD_PCODES)].groupby("year")[
    "total_exposed"
].sum().plot()
```

```python
filename = "cmr_adm3_average_flood_exposed.csv"
avg_exposure3.to_csv(floodscan.PROC_FS_DIR / filename, index=False)

filename = "cmr_adm2_average_flood_exposed.csv"
avg_exposure2.to_csv(floodscan.PROC_FS_DIR / filename, index=False)
```

```python
fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))

for j, variable in enumerate(["total_exposed", "frac_exposed"]):
    avg_exposure_plot2.plot(
        column=variable, ax=axs[j], legend=True, cmap="Purples"
    )
    # for index, row in (
    #     avg_exposure_plot_aoi.sort_values(variable).iloc[-10:].iterrows()
    # ):
    #     centroid = row["geometry"].centroid

    #     axs[j].annotate(
    #         row["ADM2_EN"],
    #         xy=(centroid.x, centroid.y),
    #         xytext=(0, 0),
    #         textcoords="offset points",
    #         ha="center",
    #         va="center",
    #     )

    adm2.boundary.plot(ax=axs[j], linewidth=0.2, color="k")
    axs[j].axis("off")


axs[0].set_title(
    "Population totale typiquement exposée aux inondations\nPar Département"
)
axs[1].set_title(
    "Fraction de la population typiquement exposée aux inondations\n"
    "Par Département"
)

plt.subplots_adjust(wspace=0)
```

```python
fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))

for j, variable in enumerate(["total_exposed", "frac_exposed"]):
    avg_exposure_plot_aoi2.plot(
        column=variable, ax=axs[j], legend=True, cmap="Purples"
    )

    adm2_aoi.boundary.plot(ax=axs[j], linewidth=0.2, color="k")
    axs[j].axis("off")


axs[0].set_title(
    "Population totale typiquement exposée aux inondations\n"
    "Régions: Extrême-Nord et Nord, par Département"
)
axs[1].set_title(
    "Fraction de la population typiquement exposée aux inondations\n"
    "Régions: Extrême-Nord et Nord, par Département"
)

for idx, row in avg_exposure_plot_aoi2.iterrows():
    color = "black"
    centroid = row.geometry.centroid
    axs[0].annotate(
        row["ADM2_FR"],
        xy=(centroid.x + x_shift, centroid.y + y_shift),
        ha="center",
        va="center",
        fontsize=10,
        color=color,
    )

plt.subplots_adjust(wspace=0)
```

```python
fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))

for j, variable in enumerate(["total_exposed", "frac_exposed"]):
    avg_exposure_plot_aoi_en3.plot(
        column=variable, ax=axs[j], legend=True, cmap="Purples"
    )

    adm3_aoi_en.boundary.plot(ax=axs[j], linewidth=0.2, color="k")
    axs[j].axis("off")


axs[0].set_title(
    "Population totale typiquement exposée aux inondations\n"
    "Région: Extrême-Nord, par Commune"
)
axs[1].set_title(
    "Fraction de la population typiquement exposée aux inondations\n"
    "Région: Extrême-Nord, par Commune"
)

for idx, row in avg_exposure_plot_aoi_en3.iterrows():
    color = "black" if row["total_exposed"] < 20000 else "white"
    centroid = row.geometry.centroid
    axs[0].annotate(
        row["ADM3_FR"],
        xy=(centroid.x + x_shift, centroid.y + y_shift),
        ha="center",
        va="center",
        fontsize=10,
        color=color,
    )

plt.subplots_adjust(wspace=0)
```

```python
cols = [
    # "ADM1_PCODE",
    # "ADM1_FR",
    # "ADM2_PCODE",
    "ADM2_FR",
    # "ADM3_PCODE",
    "ADM3_FR",
    # "total_pop",
    "total_exposed",
    "frac_exposed",
    # "geometry",
]
tot_label = "Pop. totale exposée"
frac_label = "Frac. de pop. exposée"
avg_exposure_plot_aoi_en3[cols].sort_values(
    "total_exposed", ascending=False
).iloc[:10].rename(
    columns={
        "total_exposed": tot_label,
        "frac_exposed": frac_label,
        "ADM1_FR": "Région",
        "ADM2_FR": "Département",
        "ADM3_FR": "Commune",
    }
).style.background_gradient(
    cmap="Purples"
).format(
    "{:,.0f}", subset=[tot_label]
).format(
    "{:.2f}", subset=[frac_label]
)
```

```python
exposure3_2022 = exposure3[exposure3["year"] == 2022].copy()
int_cols = ["total_exposed", "total_pop"]
exposure3_2022[int_cols] = exposure3_2022[int_cols].astype(int)
exposure_2022_plot3 = adm3.merge(exposure3_2022, on="ADM3_PCODE")
exposure_2022_plot_aoi_en3 = exposure_2022_plot3[
    exposure_2022_plot3["ADM1_PCODE"] == "CM004"
]

fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))

for j, variable in enumerate(["total_exposed", "frac_exposed"]):
    exposure_2022_plot_aoi_en3.plot(
        column=variable, ax=axs[j], legend=True, cmap="Purples"
    )

    exposure_2022_plot_aoi_en3.boundary.plot(
        ax=axs[j], linewidth=0.2, color="k"
    )
    axs[j].axis("off")


axs[0].set_title(
    "Population totale exposée aux inondations de 2022\n"
    "Région: Extrême-Nord, par Commune"
)
axs[1].set_title(
    "Fraction de la population exposée aux inondations de 2022\n"
    "Région: Extrême-Nord, par Commune"
)

for idx, row in exposure_2022_plot_aoi_en3.iterrows():
    color = "black" if row["total_exposed"] < 20000 else "white"
    centroid = row.geometry.centroid
    axs[0].annotate(
        row["ADM3_FR"],
        xy=(centroid.x + x_shift, centroid.y + y_shift),
        ha="center",
        va="center",
        fontsize=10,
        color=color,
    )

plt.subplots_adjust(wspace=0)
```

```python
exposure2_2022 = exposure2[exposure2["year"] == 2022].copy()
int_cols = ["total_exposed", "total_pop"]
exposure2_2022[int_cols] = exposure2_2022[int_cols].astype(int)
exposure_2022_plot2 = adm2.merge(exposure2_2022, on="ADM2_PCODE")
exposure_2022_plot_aoi_en2 = exposure_2022_plot2[
    exposure_2022_plot2["ADM1_PCODE"] == "CM004"
]

fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))

for j, variable in enumerate(["total_exposed", "frac_exposed"]):
    exposure_2022_plot_aoi_en2.plot(
        column=variable, ax=axs[j], legend=True, cmap="Purples"
    )

    exposure_2022_plot_aoi_en2.boundary.plot(
        ax=axs[j], linewidth=0.2, color="k"
    )
    axs[j].axis("off")


axs[0].set_title(
    "Population totale exposée aux inondations de 2022\n"
    "Région: Extrême-Nord, par Département"
)
axs[1].set_title(
    "Fraction de la population exposée aux inondations de 2022\n"
    "Région: Extrême-Nord, par Département"
)

for idx, row in exposure_2022_plot_aoi_en2.iterrows():
    color = "black"
    x_shift = -0.35 if row["ADM2_FR"] == "Logone-et-Chari" else 0
    centroid = row.geometry.centroid
    axs[0].annotate(
        row["ADM2_FR"],
        xy=(centroid.x + x_shift, centroid.y + y_shift),
        ha="center",
        va="center",
        fontsize=10,
        color=color,
    )

plt.subplots_adjust(wspace=0)
```

```python
exposure3
```

```python
cols = [
    # "ADM1_PCODE",
    "ADM1_FR",
    # "ADM2_PCODE",
    "ADM2_FR",
    # "total_pop",
    "total_exposed",
    "frac_exposed",
    # "geometry",
]
tot_label = "Pop. totale exposée"
frac_label = "Frac. de pop. exposée"
avg_exposure_plot2[cols].sort_values("total_exposed", ascending=False).iloc[
    :10
].rename(
    columns={
        "total_exposed": tot_label,
        "frac_exposed": frac_label,
        "ADM1_FR": "Région",
        "ADM2_FR": "Département",
    }
).style.background_gradient(
    cmap="Purples"
).format(
    "{:,.0f}", subset=[tot_label]
).format(
    "{:.2f}", subset=[frac_label]
)
```

```python
exposure_raster = floodscan.load_raster_flood_exposures()
exposure_raster_aoi = exposure_raster.rio.clip(
    adm2_aoi.geometry, all_touched=True
)
```

```python
exposure_raster_aoi_mean = exposure_raster_aoi.mean(dim="year")
exposure_raster_aoi_mean = exposure_raster_aoi_mean.where(
    exposure_raster_aoi_mean > 5
)

exposure_raster_mean = exposure_raster.mean(dim="year")
exposure_raster_mean = exposure_raster_mean.where(exposure_raster_mean > 5)
```

```python
fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(20, 20))

# pop
pop.plot(ax=axs[0], cmap="Greys", vmax=500, add_colorbar=False)
axs[0].set_title("Population, 2020")

# flooding
fs_mean.where(fs_mean > 0.05).plot(ax=axs[1], cmap="Blues", add_colorbar=False)
axs[1].set_title("Fraction inondée typique, 1998-2023")

# exposure
exposure_raster_mean.plot(
    ax=axs[2], cmap="Purples", vmax=50, add_colorbar=False
)
axs[2].set_title(
    "Population totale typiquement exposée aux inondations, 1998-2023"
)

for ax in axs:
    adm2.boundary.plot(ax=ax, linewidth=0.2, color="k")
    ax.axis("off")

plt.subplots_adjust(wspace=0.2)
```

```python
fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(20, 20))

# pop
pop_aoi.plot(ax=axs[0], cmap="Greys", vmax=500, add_colorbar=False)
axs[0].set_title("Population, 2020")

# flooding
fs_aoi_mean.where(fs_aoi_mean > 0.05).plot(
    ax=axs[1], cmap="Blues", add_colorbar=False
)
axs[1].set_title("Fraction inondée typique, 1998-2023")

# exposure
exposure_raster_aoi_mean.plot(
    ax=axs[2], cmap="Purples", vmax=50, add_colorbar=False
)
axs[2].set_title(
    "Population totale typiquement exposée aux inondations, 1998-2023"
)
for idx, row in adm2_aoi.iterrows():
    # Calculate the centroid of each geometry
    centroid = row.geometry.centroid
    x_shift, y_shift = (
        (-0.4, 0) if row["ADM2_FR"] == "Logone-et-Chari" else (0, 0)
    )
    # axs[2].annotate(
    #     row["ADM2_FR"],
    #     xy=(centroid.x + x_shift, centroid.y + y_shift),
    #     ha="center",
    #     va="center",
    #     fontsize=8,
    #     color="red",
    # )

for ax in axs:
    adm2_aoi.boundary.plot(ax=ax, linewidth=0.2, color="k")
    ax.axis("off")

plt.subplots_adjust(wspace=0.2)
```

```python

```
