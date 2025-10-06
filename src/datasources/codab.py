import os
import shutil
from pathlib import Path

import geopandas as gpd
import ocha_stratus as stratus
import requests

from src.blob import PROJECT_PREFIX
from src.constants import ISO3

DATA_DIR = Path(os.getenv("AA_DATA_DIR"))
CODAB_PATH = DATA_DIR / "public" / "raw" / "cmr" / "cod_ab" / "cmr.shp.zip"
FIELDMAPS_URL = (
    "https://data.fieldmaps.io/{data_type}/originals/{iso3}.shp.zip"
)
BLOB_NAME = "{project_prefix}/raw/codab/{iso3}.shp.zip"


def get_blob_name(iso3: str = ISO3):
    iso3 = iso3.lower()
    return BLOB_NAME.format(project_prefix=PROJECT_PREFIX, iso3=iso3)


def download_codab():
    url = "https://data.fieldmaps.io/cod/originals/cmr.shp.zip"
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(CODAB_PATH, "wb") as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)
    else:
        print(
            f"Failed to download file. "
            f"HTTP response code: {response.status_code}"
        )


def load_codab(admin_level: int = 3):
    gdf = gpd.read_file(CODAB_PATH)
    if admin_level == 2:
        cols = [x for x in gdf.columns if "ADM3" not in x]
        gdf = gdf.dissolve("ADM2_PCODE").reset_index()[cols]
    elif admin_level == 1:
        cols = [x for x in gdf.columns if "ADM3" not in x and "ADM2" not in x]
        gdf = gdf.dissolve("ADM1_PCODE").reset_index()[cols]
    elif admin_level == 0:
        cols = [
            x
            for x in gdf.columns
            if "ADM3" not in x and "ADM2" not in x and "ADM1" not in x
        ]
        gdf = gdf.dissolve("ADM0_PCODE").reset_index()[cols]
    return gdf


def download_codab_to_blob(iso3: str = ISO3):
    iso3 = iso3.lower()
    url = FIELDMAPS_URL.format(iso3=iso3, data_type="cod")
    response = requests.get(url)
    response.raise_for_status()
    blob_name = get_blob_name(iso3)
    stratus.upload_blob_data(response.content, blob_name)


def load_codab_from_blob(
    admin_level: int = 0, aoi_only: bool = False, iso3: str = ISO3
):
    iso3 = iso3.lower()
    shapefile = f"{iso3}_adm{admin_level}.shp"
    gdf = stratus.load_shp_from_blob(
        blob_name=get_blob_name(iso3),
        shapefile=shapefile,
        stage="dev",
    )
    if aoi_only:
        raise ValueError("No AOI defined")
    return gdf
