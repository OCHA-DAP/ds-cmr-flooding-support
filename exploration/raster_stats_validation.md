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

# Raster stats validation

Validation of raster stats from Postgres DB

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import pandas as pd

from src.datasources import codab, ecmwf
from src.utils import upsample_dataarray
from src.constants import *
```

```python
adm2 = codab.load_codab(admin_level=2)
adm2 = adm2[adm2["ADM1_PCODE"] == EXTREMENORD]
```

```python
DATE_LT_STR = "m7-l123"
filename = f"cmr_ecmwf_{DATE_LT_STR}_extremenord_ranks.csv"
df_cds = pd.read_csv(ecmwf.ECMWF_PROC_DIR / filename)
df_cds["mean_daily"] = df_cds["tprate"] / 30
```

```python
df_cds
```

```python
valid_months = [7, 8, 9]
ec = ecmwf.open_ecmwf_rasters_from_blob(
    issue_months=[7], valid_months=valid_months
)
```

```python
ec_year = ec.sum(dim="leadtime").squeeze(drop=True)
ec_year_up = upsample_dataarray(ec_year, lat_dim="y", lon_dim="x")
ec_clip = ec_year_up.rio.clip(adm2.geometry)
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
filename = "cmr_ecmwf_prod_tdraster_extremenord_ranks.csv"
ec_df.to_csv(ecmwf.ECMWF_PROC_DIR / filename, index=False)
```

```python
filename = "cmr_ecmwf_prod_tdraster_extremenord_ranks.csv"
df_prod = pd.read_csv(ecmwf.ECMWF_PROC_DIR / filename)
```

```python
filename = "sql_extremenord_i7_v789.csv"
df_sql = pd.read_csv(
    ecmwf.ECMWF_PROC_DIR / filename, parse_dates=["valid_date"]
)
df_sql = (
    df_sql.groupby(df_sql["valid_date"].dt.year)["mean"].sum().reset_index()
)
```

```python
df_compare = (
    df_sql.rename(columns={"valid_date": "year"})
    .merge(df_prod[["year", "mean"]], on="year", suffixes=("_sql", "_prod"))
    .merge(
        df_cds.rename(columns={"mean_daily": "mean_cds"})[
            ["year", "mean_cds"]
        ],
        on="year",
    )
)
for x in df_compare.set_index("year").columns:
    df_compare[f"rank_{x}"] = df_compare[x].rank()
df_compare["sql_prod_bool"] = (
    df_compare["rank_mean_sql"] == df_compare["rank_mean_prod"]
)
df_compare["sql_prod_diff"] = df_compare["mean_sql"] - df_compare["mean_prod"]
df_compare
```

```python
len(df_compare) - df_compare["sql_prod_bool"].sum() - 4
```

```python
df_compare["sql_prod_diff"].mean() / df_compare["mean_prod"].mean()
```
