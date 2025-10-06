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

# EM-DAT all

Loading full EM-DAT database

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import ocha_stratus as stratus
import duckdb

from src import blob
```

```python
blob_name = "emdat/raw/emdat_all.xlsx"
df_in = blob.load_xlsx_from_blob(blob_name, container_name="global")
```

```python
blob_name = "emdat/processed/emdat_all.parquet"
stratus.upload_parquet_to_blob(df_in, blob_name, container_name="global")
```

```python
blob_name = "emdat/processed/emdat_all.parquet"
url = (
    stratus.get_container_client(container_name="global")
    .get_blob_client(blob_name)
    .url
)
```

```python
con = duckdb.connect()
```

```python
df_test = con.execute(
    f"""
    SELECT *
    FROM read_parquet('{url}')
    WHERE ISO = 'CMR' AND "Disaster Type" = 'Flood' AND Historic = 'No'
"""
).df()
```

```python
df_test
```
