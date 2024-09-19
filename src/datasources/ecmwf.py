import os
from pathlib import Path

import xarray as xr
from tqdm.auto import tqdm

from src import blob

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


def open_ecmwf_rasters_from_blob(
    issue_months: list = None,
    issue_years: list = None,
    valid_months: list = None,
):
    if issue_months is None:
        issue_months = range(1, 13)
    if valid_months is None:
        valid_months = range(1, 13)
    if issue_years is None:
        issue_years = range(1981, 2025)
    das = []
    for year in tqdm(issue_years):
        for month in issue_months:
            if valid_months is not None:
                for valid_month in valid_months:
                    leadtime = valid_month - month
                    if leadtime < 0:
                        raise ValueError(
                            "valid_month must be after issue_month"
                        )
                    elif leadtime > 6:
                        raise ValueError("leadtime must be less than 7 months")
                    da_in = blob.open_blob_cog(
                        get_blob_name(
                            month=month, leadtime=leadtime, year=year
                        ),
                        container_name="raster",
                        stage="prod",
                        chunks=True,
                    )
                    da_in = da_in.squeeze(drop=True)
                    da_in["year"] = year
                    da_in["month"] = month
                    da_in["leadtime"] = leadtime
                    da_in = da_in.expand_dims(["year", "month", "leadtime"])
                    da_in = da_in.persist()
                    das.append(da_in)
    da = xr.combine_by_coords(das, combine_attrs="drop_conflicts")
    return da


def get_blob_name(month: int, leadtime: int, year: int):
    provider = "aws" if year == 2024 else "mars"
    return (
        f"seas5/{provider}/processed/tprate_em_i{year}-"
        f"{month:02d}-01_lt{leadtime}.tif"
    )
