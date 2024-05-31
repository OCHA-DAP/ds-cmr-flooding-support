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

# IRI

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import cftime
import datetime
from dateutil.relativedelta import relativedelta

import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from src.datasources import iri, codab
from src import constants
from src.utils import upsample_dataarray
```

```python
DATE_LT_STR = "m5-l345"
PUB_MONTH_STR = "mai"
VALID_MONTHS_STR = "juillet-août-septembre"
```

```python
adm2 = codab.load_codab(admin_level=2)
```

```python
adm2.plot()
```

```python
ds = iri.load_raw_iri()
```

```python
ds.F
```

```python
datetime.date(1960, 1, 1)
```

```python
def process_F(f):
    start_date = datetime.date(1960, 1, 1)
    return start_date + pd.DateOffset(months=int(f - 0.5), days=15)


ds = ds.assign_coords(F=[process_F(f) for f in ds.F.values])
```

```python
ds = ds.rio.write_crs(4326)
ds_clip = ds.rio.clip(adm2.geometry, all_touched=True)
```

```python
da = ds_clip["prob"]
da = da.sel(L=2, C=2)
time_index = da["F"].to_index()
may_dates = time_index.month == 5
da = da.sel(F=time_index[may_dates])
da = da.groupby("F.year").sum()
```

```python
da_up = upsample_dataarray(da, lat_dim="Y", lon_dim="X")
```

```python
da_adm = da_up.rio.clip(adm2.geometry, all_touched=True)
da_adm = da_adm.where(da_adm > 0)
```

```python
da_adm.isel(year=-1).plot()
```

```python
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
adm2.boundary.plot(ax=ax, color="black", linewidth=0.5)

vmax = da_adm.sel(year=2024).max()
vmin = 100 / 3 - (vmax - 100 / 3)

da_adm.sel(year=2024).plot(
    ax=ax,
    cmap="RdBu",
    vmax=vmax,
    vmin=vmin,
    cbar_kwargs={
        "label": "Probabilité de précipitations supérieures à normale"
    },
)
ax.axis("off")
ax.set_title(
    f"Prévisions IRI 2024 Cameroun\n"
    f"mois de publication: {PUB_MONTH_STR},\npériode d'interêt: {VALID_MONTHS_STR}"
)

df_adm = da_adm.mean(dim=["X", "Y"]).to_dataframe()["prob"].reset_index()

thresh = df_adm["prob"].quantile(2 / 3)

fig, ax = plt.subplots(dpi=300)
df_adm.plot(x="year", y="prob", ax=ax, legend=False, linewidth=1)
ax.plot([2024], [df_adm.iloc[-1]["prob"]], ".r")
ax.annotate(
    "2024",
    xy=(2024, df_adm.iloc[-1]["prob"]),
    color="red",
    ha="center",
    va="top",
)
ax.axhline(y=thresh, color="grey", linestyle="--")
ax.annotate(
    " seuil\n 1-an-sur-3",
    xy=(2024, thresh),
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
