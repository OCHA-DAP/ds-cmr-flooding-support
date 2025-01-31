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

# ERA5

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import calendar

import matplotlib.pyplot as plt

from src.datasources import era5, watersheds
from src import blob
from src.utils import upsample_dataarray
from src.constants import *
```

## Load data

```python
gdf_lc = watersheds.load_logone_chari()
```

```python
gdf_lc.plot()
```

```python
da_era5 = era5.open_era5_rasters_from_blob()
```

## Process ERA5

```python
da_era5_clip = upsample_dataarray(da_era5, lat_dim="y", lon_dim="x").rio.clip(
    gdf_lc.geometry
)
```

```python
da_era5_clip
```

```python
da_era5_clip = da_era5_clip.persist()
```

```python
da_era5_mean = da_era5_clip.mean(dim=["x", "y"])
```

```python
da_era5_mean
```

```python
df_era5 = da_era5_mean.to_dataframe("mean")["mean"].reset_index()
```

```python
blob_name = f"{blob.PROJECT_PREFIX}/processed/era5/logonechari_era5_monthly_means.parquet"
```

```python
blob_name
```

```python
blob.upload_parquet_to_blob(blob_name, df_era5)
```

```python
fig, ax = plt.subplots(dpi=200)

df_era5.groupby("month")["mean"].mean().plot.bar(ax=ax, color="dodgerblue")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.set_xlabel("Mois")
ax.set_ylabel("Précipitations moyennes historiques\n(mm / jour)")
ax.set_title("Précipitations saisonnières sur les bassins Logone et Chari")
```
