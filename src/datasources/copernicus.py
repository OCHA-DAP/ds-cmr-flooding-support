from typing import Literal

from src import blob


def get_blob_name(aoi_number: int, type: Literal["product", "aoi"]):
    type_str = "BLP" if type == "aoi" else "DEL_PRODUCT_v1"
    return (
        f"{blob.PROJECT_PREFIX}/raw/copernicus/"
        f"EMSR772_AOI{aoi_number:02d}_{type_str}.zip"
    )


def load_copernicus(
    aoi_number: int, product_type: Literal["product", "aoi"], shapefile: str
):
    return blob.load_gdf_from_blob(
        get_blob_name(aoi_number, product_type), shapefile=shapefile
    )
