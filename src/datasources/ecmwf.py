import os
from pathlib import Path

import xarray as xr

DATA_DIR = Path(os.getenv("AA_DATA_DIR_NEW"))
ECMWF_GLB_RAW_PATH = (
    DATA_DIR
    / "collaborations"
    / "mapaction"
    / "raw"
    / "glb"
    / "ecmwf"
    / "ecmwf-monthly-seasonalforecast-1981-2023.grib"
)
ECMWF_CMR_RAW_DIR = DATA_DIR / "public" / "raw" / "cmr" / "ecmwf"
ECMWF_PROC_DIR = DATA_DIR / "public" / "processed" / "cmr" / "ecmwf"


def load_ecmwf_glb_raw():
    return xr.open_dataset(ECMWF_GLB_RAW_PATH, engine="cfgrib")


def load_ecmwf_specific_cmr(
    date_lt_str: str = "m3-l456", area_str: str = "cmr"
):
    # note: these datasets were just downloaded manually from CDS
    # using the total_bounds of adm2

    # recall that CDS re-grids based on query coordinates
    # so to stay consistent query coordinates should be rounded to integer

    # for reference the area is:
    # for Cameroon:
    # 'area': [
    #     15, 8, 1,
    #     18,
    # ],
    # for Logone and Chari:
    # 'area': [
    #     14, 13, 6,
    #     20,
    # ],
    filename = f"ecmwf-seasonal-{area_str}-{date_lt_str}.grib"
    return xr.open_dataset(
        ECMWF_CMR_RAW_DIR / filename,
        engine="cfgrib",
        backend_kwargs={"indexpath": ""},
    )
