import os
from pathlib import Path

import pandas as pd

from src.datasources import codab

DATA_DIR = Path(os.getenv("AA_DATA_DIR_NEW"))
IMPACT_RAW_DIR = DATA_DIR / "public" / "raw" / "cmr" / "ocha"
IMPACT_2022_PATH = (
    IMPACT_RAW_DIR / "cmr_exno_data_inondationlc_md_mt_v1.0_20221206.xlsx"
)
IMPACT_PROC_DIR = DATA_DIR / "public" / "processed" / "cmr" / "ocha"
IMPACT_PROC_PATH = (
    IMPACT_PROC_DIR
    / "cmr_exno_data_inondationlc_md_mt_v1.0_20221206_processed.csv"
)


def load_raw_impact_2022():
    return pd.read_excel(IMPACT_2022_PATH, sheet_name="Data", skiprows=[1])


def process_impact_2022():
    adm3 = codab.load_codab(admin_level=3)
    df = load_raw_impact_2022()
    df["PcodeAdmin3"] = df["PcodeAdmin3"].astype(str)
    # check for missing PcodeAdmin3
    # print(df[df["PcodeAdmin3"] == "nan"]["Commune"].unique())
    name2pcode = {
        "Blangoua": "CMR004002001",
        "Makari": "CMR004002008",
        "Waza": "CMR004002009",
        "Logone Birni": "CMR004002007",
        "Darack": "CMR004002002",
    }
    for n2p in name2pcode.items():
        df.loc[df["Commune"] == n2p[0], "PcodeAdmin3"] = n2p[1]
    df["ADM3_PCODE"] = df["PcodeAdmin3"].apply(lambda x: x.replace("R", ""))
    cols = [x for x in adm3.columns if "PCODE" in x]
    df_cod = df.merge(adm3[cols], on="ADM3_PCODE")
    if not IMPACT_PROC_DIR.exists():
        IMPACT_PROC_DIR.mkdir(parents=True)
    df_cod.to_csv(IMPACT_PROC_PATH, index=False)


def load_processed_impact_2022():
    return pd.read_csv(IMPACT_PROC_PATH)
