from src import blob


def load_emdat():
    blob_name = f"{blob.PROJECT_PREFIX}/raw/emdat/emdat-cmr-inondations.xlsx"
    return blob.load_xlsx_from_blob(blob_name)
