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
import numpy as np
import geopandas as gpd
import pandas as pd

from src.datasources import copernicus, codab, worldpop, floodscan
from src.constants import *
from src import blob
```

```python
DATE = "2024-10-24"
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
    floodscan.get_blob_name("cmr", "exposure_raster", DATE)
)
exp_aoi = fs.rio.clip(adm2_aoi.geometry)
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
df_cems = pd.DataFrame(
    columns=["aoi_num", "cems_exp", "cems_total_pop"],
    data=[[1, 39000, 870000], [2, 6400, 300000], [3, 26000, 430000]],
)
```

```python
df_cems
```

```python
aoi_num = 3
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
```

```python
fig, ax = plt.subplots(dpi=500)
adm2_aoi.boundary.plot(ax=ax, color="grey", linewidth=0.5)
adm3_aoi.boundary.plot(ax=ax, color="grey", linewidth=0.1)
for aoi_num in range(1, 4):
    shapefile = f"EMSR772_AOI{aoi_num:02d}_DEL_PRODUCT_areaOfInterestA_v1.shp"
    gdf_aoi = copernicus.load_copernicus(aoi_num, "product", shapefile)
    gdf_aoi.boundary.plot(ax=ax, color="darkorange", linewidth=0.5)
    centroid = gdf_aoi.to_crs(3857).centroid.to_crs(4326).iloc[0]
    ax.annotate(aoi_num, (centroid.x, centroid.y), color="darkorange")

ax.axis("off")
```

```python

```

```python
39 / 870
```

```python
1844.6 / 49385
```

```python
6.4 / 300
```

```python
155.2 / 6652.9
```

```python
26 / 430
```

```python
416.3 / 7396.7
```

```python

```
