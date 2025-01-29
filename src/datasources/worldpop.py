import os
from pathlib import Path

import pandas as pd
import rioxarray as rxr

from src.datasources import codab

AA_DATA_DIR = Path(os.getenv("AA_DATA_DIR_NEW"))
RAW_WP_PATH = (
    AA_DATA_DIR
    / "public"
    / "raw"
    / "cmr"
    / "worldpop"
    / "cmr_ppp_2020_1km_Aggregated_UNadj.tif"
)
PROC_WP_DIR = AA_DATA_DIR / "public" / "processed" / "cmr" / "worldpop"


def load_raw_worldpop():
    da = rxr.open_rasterio(RAW_WP_PATH)
    return da.where(da != da.attrs["_FillValue"])


def aggregate_worldpop_to_adm(admin_level: int = 2):
    pop = load_raw_worldpop()
    adm = codab.load_codab(admin_level=admin_level)
    dicts = []
    for _, row in adm.iterrows():
        da_clip = pop.rio.clip([row.geometry])
        da_clip = da_clip.where(da_clip > 0)
        dicts.append(
            {
                "total_pop": da_clip.sum().values,
                f"ADM{admin_level}_PCODE": row[f"ADM{admin_level}_PCODE"],
            }
        )
    df_pop = pd.DataFrame(dicts)
    if not PROC_WP_DIR.exists():
        PROC_WP_DIR.mkdir(parents=True)
    filename = f"cmr_adm{admin_level}_2020_1km_Aggregated_UNadj.csv"
    df_pop.to_csv(PROC_WP_DIR / filename, index=False)


def load_adm_worldpop(admin_level: int = 2):
    filename = f"cmr_adm{admin_level}_2020_1km_Aggregated_UNadj.csv"
    return pd.read_csv(PROC_WP_DIR / filename)
