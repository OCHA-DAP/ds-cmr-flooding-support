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

# Copernicus

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
import numpy as np
import geopandas as gpd
import pandas as pd

from src.datasources import copernicus, codab, worldpop, floodscan
from src.constants import *
from src import blob
```

```python
# first CEMS activation
DATE1 = "2024-10-24"
# second CEMS activation
DATE2 = "2024-11-23"
```

```python
date = DATE2
```

```python
pop = worldpop.load_raw_worldpop()
pop.attrs["_FillValue"] = np.nan
```

```python
adm2 = codab.load_codab(2)
adm2_aoi = adm2[adm2["ADM1_PCODE"] == EXTREMENORD]

adm3 = codab.load_codab(3)
adm3_aoi = adm3[adm3["ADM1_PCODE"] == EXTREMENORD]
```

```python
exp = blob.open_blob_cog(
    floodscan.get_blob_name("cmr", "exposure_raster", date)
)
exp_aoi = exp.rio.clip(adm2_aoi.geometry)
```

```python
fig, ax = plt.subplots()
adm2_aoi.boundary.plot(ax=ax)
exp_aoi.plot(ax=ax, vmax=100)
ax.axis("off")
```

```python
blob_name = copernicus.get_blob_name(1, "product")
```

```python
blob_name
```

```python
test = blob.list_zip_shps(blob_name)
```

```python
test
```

```python
# set CEMS exposure (based on reading from their site)
if date == DATE1:
    df_cems = pd.DataFrame(
        columns=["aoi_num", "cems_exp", "cems_total_pop"],
        data=[[1, 39000, 870000], [2, 6400, 300000], [3, 26000, 430000]],
    )
elif date == DATE2:
    df_cems = pd.DataFrame(
        columns=["aoi_num", "cems_exp", "cems_total_pop"],
        data=[[1, 1500, 870000], [2, 13000, 300000], [3, 8200, 430000]],
    )
else:
    raise ValueError(f"incorrect date {date}")
```

```python
df_cems
```

```python
plotting = False
dicts = []
for aoi_num in range(1, 4):
    # AOI
    shapefile = f"EMSR772_AOI{aoi_num:02d}_DEL_PRODUCT_areaOfInterestA_v1.shp"
    gdf_aoi = copernicus.load_copernicus(aoi_num, "product", shapefile)

    # floodDetph
    shapefile = f"EMSR772_AOI{aoi_num:02d}_DEL_PRODUCT_floodDepthA_v1.shp"
    gdf_depth = copernicus.load_copernicus(aoi_num, "product", shapefile)

    # footprint
    shapefile = f"EMSR772_AOI{aoi_num:02d}_DEL_PRODUCT_imageFootprintA_v1.shp"
    gdf_footprint = copernicus.load_copernicus(aoi_num, "product", shapefile)
    gdf_not_analysed = gdf_footprint[
        gdf_footprint["obj_type"] == "Not Analysed"
    ]

    # obsv extent
    shapefile = f"EMSR772_AOI{aoi_num:02d}_DEL_PRODUCT_observedEventA_v1.shp"
    gdf_obsv = copernicus.load_copernicus(aoi_num, "product", shapefile)

    if plotting:
        fig, ax = plt.subplots(dpi=500)
        adm2_aoi.boundary.plot(ax=ax, color="grey", linewidth=0.5)
        adm3_aoi.boundary.plot(ax=ax, color="grey", linewidth=0.1)
        gdf_aoi.boundary.plot(ax=ax, color="darkorange", linewidth=0.2)
        if not gdf_not_analysed.empty:
            gdf_not_analysed.boundary.plot(
                ax=ax, color="dodgerblue", linewidth=0.2
            )
        gdf_depth.boundary.plot(ax=ax, color="rebeccapurple", linewidth=0.2)
        gdf_obsv.boundary.plot(ax=ax, color="crimson", linewidth=0.2)
        ax.axis("off")

    gdf_cut = gdf_aoi.geometry.iloc[0].difference(gdf_not_analysed.unary_union)
    if gdf_cut is not None:
        gdf_analysed = gpd.GeoDataFrame(geometry=[gdf_cut], crs=gdf_aoi.crs)
    else:
        gdf_analysed = gdf_aoi.copy()

    exp_clip = exp.rio.clip(gdf_analysed.geometry)

    if plotting:
        fig, ax = plt.subplots()
        gdf_analysed.boundary.plot(ax=ax, color="dodgerblue", linewidth=0.5)
        exp_clip.plot(ax=ax)
        ax.axis("off")

    pop_flood_clip = pop.rio.clip(gdf_obsv.geometry)

    if plotting:
        fig, ax = plt.subplots(dpi=200)
        gdf_analysed.boundary.plot(ax=ax, color="dodgerblue", linewidth=0.5)
        gdf_obsv.boundary.plot(ax=ax, color="crimson", linewidth=0.2)
        pop_flood_clip.plot(ax=ax)
        ax.axis("off")

    dicts.append(
        {
            "aoi_num": aoi_num,
            "chd_exp": int(exp_clip.sum()),
            "chd_total_pop": int(pop.rio.clip(gdf_analysed.geometry).sum()),
            "cems_worldpop": int(pop_flood_clip.sum()),
        }
    )
```

```python
df_chd = pd.DataFrame(dicts)
```

```python
df_compare = df_chd.merge(df_cems)
df_compare["factor_error"] = df_compare["chd_exp"] / df_compare["cems_exp"]
```

```python
df_compare
```

```python

```

```python
fig, ax = plt.subplots()

cols = ["chd_exp", "cems_exp"]
df_compare.set_index("aoi_num")[cols].plot.bar(ax=ax)
ax.set_ylabel("Population exposed to flooding")
ax.yaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, pos: f"{int(x):,}")
)
ax.set_xlabel("AOI number")

ax.legend(labels=["OCHA CHD", "CEMS"], title="Exposure estimate from:")
```

```python
aoi_colors = {1: "dodgerblue", 2: "chocolate", 3: "seagreen"}
```

```python
fig, ax = plt.subplots(dpi=400)
adm2_aoi.boundary.plot(ax=ax, color="grey", linewidth=0.5)
adm3_aoi.boundary.plot(ax=ax, color="grey", linewidth=0.1)
for aoi_num in range(1, 4):
    shapefile = f"EMSR772_AOI{aoi_num:02d}_DEL_PRODUCT_areaOfInterestA_v1.shp"
    gdf_aoi = copernicus.load_copernicus(aoi_num, "product", shapefile)
    gdf_aoi.plot(
        ax=ax, color=aoi_colors.get(aoi_num), linewidth=0.5, alpha=0.2
    )
    centroid = gdf_aoi.to_crs(3857).centroid.to_crs(4326).iloc[0]
    ax.annotate(
        aoi_num, (centroid.x, centroid.y), color=aoi_colors.get(aoi_num)
    )
ax.set_title("AOI numbers over Extrême-Nord", fontsize=8)
ax.axis("off")
```

```python
aoi_dict = {1: "Yagoua", 2: "Makari", 3: "Waza"}
```

```python
# set CEMS exposure (based on reading from their site)
df_date1 = pd.DataFrame(
    columns=["aoi_num", "cems_exp", "cems_total_pop"],
    data=[[1, 39000, 870000], [2, 6400, 300000], [3, 26000, 430000]],
)
df_date1["date"] = DATE1
df_date2 = pd.DataFrame(
    columns=["aoi_num", "cems_exp", "cems_total_pop"],
    data=[[1, 1500, 870000], [2, 13000, 300000], [3, 8200, 430000]],
)
df_date2["date"] = DATE2

df_cems_plot = pd.concat([df_date1, df_date2], ignore_index=True)
# df_cems_plot["date"] = pd.to_datetime(df_cems_plot["date"])
# df_cems_plot["date_str"] = df_cems_plot["date"].dt.strftime("%b %d, %Y")

df_cems_plot["aoi_name"] = df_cems_plot["aoi_num"].map(aoi_dict)
df_cems_plot["aoi_num_name"] = df_cems_plot.apply(
    lambda x: f'{x["aoi_num"]} ({x["aoi_name"]})', axis=1
)
```

```python
fig, ax = plt.subplots(dpi=200)

df_cems_plot.pivot(
    index="date", columns="aoi_num_name", values="cems_exp"
).plot.bar(
    ax=ax, color=[aoi_colors.get(x) for x in df_cems_plot["aoi_num"].unique()]
)

# Add labels and legend
ax.set_xlabel("Date")
ax.set_ylabel("Population exposed to flooding")
ax.set_title("CEMS exposure estimates")
ax.legend(title="AOI Number")
plt.xticks(rotation=0)

ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{int(x):,}"))
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
# Show plot
plt.tight_layout()
plt.show()
```

```python

```
