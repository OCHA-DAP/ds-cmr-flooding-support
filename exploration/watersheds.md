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
from src.constants import *
```

```python
blob.list_zip_shps(f"{blob.PROJECT_PREFIX}/raw/LCB shapefiles.zip")
```

```python
adm1 = codab.load_codab(admin_level=1)
adm1 = adm1[adm1["ADM1_PCODE"] == EXTREMENORD]
adm2 = codab.load_codab(admin_level=2)
adm2 = adm2[adm2["ADM1_PCODE"] == EXTREMENORD]
```

```python
adm1
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
fig, ax = plt.subplots(dpi=200)
adm1.boundary.plot(ax=ax, color="k", linewidth=1)
adm2.boundary.plot(ax=ax, color="k", linewidth=0.5)
combined.boundary.plot(ax=ax, color="dodgerblue", linewidth=1)
combined.plot(ax=ax, color="dodgerblue", alpha=0.2)
ax.axis("off")
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

```
