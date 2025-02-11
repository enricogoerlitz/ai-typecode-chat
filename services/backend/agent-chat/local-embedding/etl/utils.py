import json
import pandas as pd

from datetime import datetime


META_FILENAME = "__meta.json"
XL_FILES_PATH = "./etl/data/00-master-data/files.xlsx"
XL_DEVICE_TYPES_PATH = "./etl/data/00-master-data/imt_deviceTypes.xlsx"


step = "NOT SET"


def dtime() -> str:
    dtime = str(datetime.now())[:19]
    return f"[{dtime}]"


def log(file: str, idx: int, count: int, msg: str) -> None:
    idx += 1
    msg = f"{dtime()}\t{idx} / {count}\t{step}\t'File '{file} {msg}.'"
    print(msg)


def read_meta(folder: str) -> dict:
    path = "/".join([folder, META_FILENAME])
    with open(path, "r") as f:
        data = json.loads(f.read())

    return data


def write_meta(folder: str, data: dict) -> dict:
    path = "/".join([folder, META_FILENAME])
    with open(path, "w") as f:
        f.write(json.dumps(data, indent=3))


def get_imt_catalog() -> pd.DataFrame:
    print("Load IMT Catalog DataFrame.")
    df_files = pd.read_excel(XL_FILES_PATH)[["DokID", "Typcode", "DokName"]]
    df_typecodes = pd.read_excel(XL_DEVICE_TYPES_PATH)[
        [
            "Typcode",
            "Gerät ID",
            "Gerätebezeichnung",
            "Typbezeichnung (unique)",
            "Typ/Modell",
            "Kennung",
            "Hersteller",
            "Zusatz / Bemerkung"
        ]
    ]

    df = pd.merge(df_files, df_typecodes, how="inner", on="Typcode")

    return df


def prep_page_content_for_txt(text: str, pnum: int, psum: int) -> str:
    return f"\n###################### Page {pnum+1} of {psum} ######################\n{text}"  # noqa
