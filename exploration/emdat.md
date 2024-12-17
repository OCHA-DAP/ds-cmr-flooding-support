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

# EMDAT

```python
%load_ext jupyter_black
%load_ext autoreload
%autoreload 2
```

```python
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from src.datasources import emdat, impact
from src.constants import *
```

```python
df = emdat.load_emdat()
```

```python
df
```

```python
df.columns
```

```python
MIN_YEAR = 2000
df_year = (
    df[df["Start Year"] >= MIN_YEAR]
    .groupby("Start Year")["Total Affected"]
    .sum()
    .reset_index()
)
```

```python
df_year
```

```python
df_year.plot.bar(x="Start Year", y="Total Affected")
```

```python
col = "Total personne affecté"
df_impact = impact.load_processed_impact_2022()
df_impact_adm2 = df_impact.groupby("ADM2_PCODE")[col].sum()
```

```python
df_impact
```

```python
df_impact_adm2
```

```python
df_year["Logone-et-Chari"] = 0
df_year["Mayo-Danay"] = 0
```

```python
df_year.loc[df_year["Start Year"] == 2022, "Mayo-Danay"] = df_impact_adm2.loc[
    MAYO_DANAY
]

df_year.loc[df_year["Start Year"] == 2020, "Mayo-Danay"] = 19218
df_year.loc[df_year["Start Year"] == 2010, "Mayo-Danay"] = 3095
df_year.loc[df_year["Start Year"] == 2013, "Mayo-Danay"] = 805


df_year.loc[df_year["Start Year"] == 2022, "Logone-et-Chari"] = (
    df_impact_adm2.loc[LOGONE_CHARI]
)
```

```python
other_col_name = "Several"
df_year[other_col_name] = (
    df_year["Total Affected"]
    - df_year["Logone-et-Chari"]
    - df_year["Mayo-Danay"]
)
df_year[other_col_name] = df_year[other_col_name].apply(lambda x: max(x, 0))
```

```python
full_year_range = range(
    df_year["Start Year"].min(), df_year["Start Year"].max() + 1
)
df_full = (
    df_year.set_index("Start Year").reindex(full_year_range).reset_index()
)
df_full = df_full.fillna(0)
```

```python
df_full
```

```python
fig, ax = plt.subplots(dpi=200, figsize=(8, 4))

for col in [other_col_name, "Logone-et-Chari", "Mayo-Danay"]:
    ax.bar(df_full["Start Year"], df_full[col], label=col)

ax.legend(title="Department", loc="upper left")
ax.set_xticks(df_full["Start Year"])
ax.xaxis.set_tick_params(labelbottom=True, rotation=90)
ax.yaxis.set_major_formatter(
    ticker.FuncFormatter(lambda x, pos: "{:,.0f}".format(x))
)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_xlabel("Year")
ax.set_ylabel("People affected")
ax.set_title(
    "People affected by flooding in Cameroon\nSources: EM-DAT (2000-2021), OCHA (2022)"
)
```

```python
[x for x in df[df["Start Year"] == 2012]["Location"].values]
```
