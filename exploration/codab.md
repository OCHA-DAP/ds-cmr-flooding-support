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

# CODAB

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
from src.datasources import codab
from src.constants import *
```

```python
EXTREMENORD
```

```python
LOGONE_CHARI
```

```python
MAYO_DANAY
```

```python
adm = codab.load_codab(admin_level=3)
```

```python
adm_aoi = adm[adm["ADM1_PCODE"] == EXTREMENORD]
```

```python
adm_aoi.columns
```

```python
adm_aoi.plot()
```

```python
filepath = "temp/cmr_extremenord_adm3.shp"
adm_aoi.to_file(filepath)
```
