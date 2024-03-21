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


def load_ecmwf_glb_raw():
    return xr.open_dataset(ECMWF_GLB_RAW_PATH, engine="cfgrib")
