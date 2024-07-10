from src import blob


def load_watersheds(shapefile: str = "watersheds.shp"):
    blob_name = f"{blob.PROJECT_PREFIX}/raw/LCB shapefiles.zip"
    return blob.load_gdf_from_blob(blob_name, shapefile=shapefile)


def load_logone_chari():
    blob_name = (
        f"{blob.PROJECT_PREFIX}/processed/logone_chari_watersheds.shp.zip"
    )
    return blob.load_gdf_from_blob(blob_name)
