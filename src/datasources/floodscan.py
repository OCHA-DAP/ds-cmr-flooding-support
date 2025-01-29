import os
from pathlib import Path
from typing import Literal

import pandas as pd
import xarray as xr

from src.datasources import codab, worldpop

DATA_DIR = Path(os.getenv("AA_DATA_DIR_NEW"))
RAW_FS_HIST_S_PATH = (
    DATA_DIR
    / "private"
    / "raw"
    / "glb"
    / "FloodScan"
    / "SFED"
    / "SFED_historical"
    / "aer_sfed_area_300s_19980112_20231231_v05r01.nc"
)
PROC_FS_DIR = DATA_DIR / "private" / "processed" / "cmr" / "floodscan"
PROC_FS_CLIP_PATH = PROC_FS_DIR / "cmr_sfed_1998_2023.nc"
PROC_FS_EXP_PATH = PROC_FS_DIR / "cmr_flood_exposure.nc"


def clip_cmr_from_glb():
    ds = xr.open_dataset(RAW_FS_HIST_S_PATH)
    da = ds["SFED_AREA"]
    da = da.rio.set_spatial_dims(x_dim="lon", y_dim="lat")
    da = da.rio.write_crs(4326)
    adm0 = codab.load_codab()
    lonmin, latmin, lonmax, latmax = adm0.total_bounds
    sfed_box = da.sel(lat=slice(latmax, latmin), lon=slice(lonmin, lonmax))
    sfed_box = sfed_box.rio.set_spatial_dims(x_dim="lon", y_dim="lat")
    sfed_clip = sfed_box.rio.clip(adm0.geometry, all_touched=True)
    if "grid_mapping" in sfed_clip.attrs:
        del sfed_clip.attrs["grid_mapping"]
    if not PROC_FS_DIR.exists():
        PROC_FS_DIR.mkdir(parents=True)
    sfed_clip.to_netcdf(PROC_FS_CLIP_PATH)


def load_raw_cmr_floodscan():
    ds = xr.open_dataset(PROC_FS_CLIP_PATH)
    da = ds["SFED_AREA"]
    da = da.rio.write_crs(4326).drop_vars("crs")
    return da


def calculate_exposure_raster(filter_months=None):
    pop = worldpop.load_raw_worldpop()
    da = load_raw_cmr_floodscan()
    if filter_months is not None:
        da = da.sel(time=da["time.month"].isin(filter_months))
    da_year = da.groupby("time.year").max()
    da_year_mask = da_year.where(da_year >= 0.05)
    da_year_mask = da_year_mask.rio.write_crs(4326)
    da_year_mask = da_year_mask.transpose("year", "lat", "lon")
    da_year_mask_resample = da_year_mask.rio.reproject_match(pop)
    da_year_mask_resample = da_year_mask_resample.where(
        da_year_mask_resample <= 1
    )
    exposure = da_year_mask_resample * pop.isel(band=0)
    save_path = (
        PROC_FS_EXP_PATH
        if filter_months is None
        else PROC_FS_DIR / f"cmr_flood_exposure_{filter_months}.nc"
    )
    exposure.to_netcdf(save_path)


def calculate_adm_exposures(admin_level: int = 2, filter_months=None):
    adm = codab.load_codab(admin_level=admin_level)
    exposure = load_raster_flood_exposures(filter_months=filter_months)

    dfs = []
    for _, row in adm.iterrows():
        da_clip = exposure.rio.clip([row.geometry])
        dff = (
            da_clip.sum(dim=["x", "y"])
            .to_dataframe(name="total_exposed")["total_exposed"]
            .astype(int)
            .reset_index()
        )
        dff[f"ADM{admin_level}_PCODE"] = row[f"ADM{admin_level}_PCODE"]
        dfs.append(dff)

    df = pd.concat(dfs, ignore_index=True)
    filename = (
        f"cmr_adm{admin_level}_count_flood_exposed.csv"
        if filter_months is None
        else f"cmr_adm{admin_level}_count_flood_exposed_{filter_months}.csv"
    )
    df.to_csv(PROC_FS_DIR / filename, index=False)


def load_raster_flood_exposures(filter_months=None):
    if filter_months is not None:
        file_path = PROC_FS_DIR / f"cmr_flood_exposure_{filter_months}.nc"
    else:
        file_path = PROC_FS_EXP_PATH
    return xr.open_dataarray(file_path)


def load_adm_flood_exposures(admin_level: int = 2, filter_months=None):
    if filter_months is not None:
        filename = (
            f"cmr_adm{admin_level}_count_flood_exposed_{filter_months}.csv"
        )
    else:
        filename = f"cmr_adm{admin_level}_count_flood_exposed.csv"
    return pd.read_csv(PROC_FS_DIR / filename)


def get_blob_name(
    iso3: str,
    data_type: Literal["exposure_raster", "exposure_tabular"],
    date: str = None,
):
    if data_type == "exposure_raster":
        if date is None:
            raise ValueError("date must be provided for exposure data")
        return (
            f"ds-floodexposure-monitoring/processed/flood_exposure/"
            f"{iso3}/{iso3}_exposure_{date}.tif"
        )
    elif data_type == "exposure_tabular":
        return (
            f"ds-floodexposure-monitoring/processed/flood_exposure/tabular/"
            f"{iso3}_adm_flood_exposure.parquet"
        )
    elif data_type == "flood_extent":
        return (
            f"ds-floodexposure-monitoring/processed/flood_extent/"
            f"{iso3}_flood_extent.tif"
        )
