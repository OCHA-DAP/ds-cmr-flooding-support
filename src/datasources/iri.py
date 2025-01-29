import os
from pathlib import Path

import xarray as xr

IRI_AUTH = os.getenv("IRI_AUTH")
DATA_DIR = Path(os.getenv("AA_DATA_DIR_NEW"))
IRI_RAW_DIR = DATA_DIR / "public" / "raw" / "glb" / "iri"
IRI_BASE_URL = (
    "https://iridl.ldeo.columbia.edu/SOURCES/.IRI/.FD/"
    ".NMME_Seasonal_Forecast/.Precipitation_ELR/.prob/"
)


def load_raw_iri():
    return xr.open_dataset(IRI_RAW_DIR / "iri.nc", decode_times=False)
