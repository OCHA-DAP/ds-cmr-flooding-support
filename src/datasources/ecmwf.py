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


def load_ecmwf_m1l456():
    filename = "ecmwf-seasonal-cmr-m3-l456.grib"
    return xr.open_dataset(ECMWF_CMR_RAW_DIR / filename, engine="cfgrib")
