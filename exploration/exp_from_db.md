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

# Exposure from DB

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import pandas as pd

from src import db_utils
from src.constants import *
```

```python
query = """
SELECT *
FROM app.floodscan_exposure
WHERE iso3 = 'CMR'
AND adm_level = 2
"""
```

```python
df_exp = pd.read_sql(query, db_utils.get_engine(), parse_dates=["valid_date"])
```

```python
df_exp.dtypes
```

```python
df_exp_max = (
    df_exp[df_exp["valid_date"].dt.year < 2025]
    .groupby([df_exp["valid_date"].dt.year, "pcode"])["sum"]
    .max()
    .reset_index()
)
```

```python
df_exp_max
```

```python
df_exp_max[df_exp_max["pcode"] == LOGONE_CHARI].plot(x="valid_date", y="sum")
```
