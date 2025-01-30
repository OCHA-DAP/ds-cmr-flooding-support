import xarray as xr
from rasterio import RasterioIOError
from tqdm.auto import tqdm

from src import blob


def open_era5_rasters_from_blob(
    years: list = None,
    months: list = None,
):
    if months is None:
        months = range(1, 13)
    if years is None:
        years = range(1981, 2026)
    das = []
    for year in tqdm(years):
        for month in months:
            try:
                da_in = blob.open_blob_cog(
                    get_blob_name(month=month, year=year),
                    container_name="raster",
                    stage="prod",
                    chunks=True,
                )
            except RasterioIOError as e:
                print(
                    f"Could not open {get_blob_name(month=month, year=year)}"
                )
                print(e)
                continue
            da_in = da_in.squeeze(drop=True)
            da_in["year"] = year
            da_in["month"] = month
            da_in = da_in.expand_dims(["year", "month"])
            # da_in = da_in.persist()
            das.append(da_in)
    da = xr.combine_by_coords(das, combine_attrs="drop_conflicts")
    return da


def get_blob_name(month: int, year: int):
    return (
        f"era5/monthly/processed/precip_reanalysis_v{year}-"
        f"{month:02d}-01.tif"
    )
