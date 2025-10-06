import duckdb
import ocha_stratus as stratus

from src import blob


def load_emdat():
    blob_name = f"{blob.PROJECT_PREFIX}/raw/emdat/emdat-cmr-inondations.xlsx"
    return blob.load_xlsx_from_blob(blob_name)


def load_emdat_from_global():
    blob_name = "emdat/processed/emdat_all.parquet"
    url = (
        stratus.get_container_client(container_name="global")
        .get_blob_client(blob_name)
        .url
    )

    with duckdb.connect() as con:
        df_in = con.execute(
            f"""
            SELECT *
            FROM read_parquet('{url}')
            WHERE ISO = 'CMR' AND "Disaster Type" = 'Flood' AND Historic = 'No'
        """
        ).df()

    return df_in
