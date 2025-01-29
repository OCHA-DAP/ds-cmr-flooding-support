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

# Watersheds

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import matplotlib.pyplot as plt
import pandas as pd

from src.datasources import watersheds, codab
from src import blob
```

```python
blob.list_zip_shps(f"{blob.PROJECT_PREFIX}/raw/LCB shapefiles.zip")
```

```python
adm = codab.load_codab()
```

```python
logone = watersheds.load_watersheds(
    shapefile="shape/LCB_Logone_river_basin_28062023.shp"
)
logone["river_name"] = "logone"
chari = watersheds.load_watersheds(
    shapefile="shape/LCB_chari_river_basin_28062023.shp"
)
chari["river_name"] = "chari_upstream"
logone_chari = watersheds.load_watersheds(
    shapefile="shape/LCB_Logone_et_Chari_river_basin_28062023.shp"
)
logone_chari["river_name"] = "chari_downstream"
```

```python
combined = pd.concat([logone, chari, logone_chari], ignore_index=True)
```

```python
cols = ["HYBAS_ID", "NEXT_DOWN", "NEXT_SINK", "MAIN_BAS"]
combined[cols] = combined[cols].astype(int)
```

```python
blob.upload_gdf_to_blob(
    combined,
    f"{blob.PROJECT_PREFIX}/processed/logone_chari_watersheds.shp.zip",
)
```

```python
fig, ax = plt.subplots()
adm.boundary.plot(ax=ax)
combined.boundary.plot(ax=ax, color="red")
```

```python
combined.plot()
```

```python
combined.dissolve().plot()
```

```python
combined.total_bounds
```

```python
test = watersheds.load_logone_chari()
```

```python
test.plot()
```
