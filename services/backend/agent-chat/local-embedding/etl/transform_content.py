import os
import traceback
import json
import pandas as pd

from etl import utils


SOURCE_FOLDER_PATH = "./etl/data/01-extract"
DESTINATION_FOLDER_PATH = "./etl/data/02-transform-content"


def run() -> None:
    meta = utils.read_meta(DESTINATION_FOLDER_PATH)
    meta["errorFiles"] = []

    df_catalog = utils.get_imt_catalog()

    files = list(df_catalog["DokName"].unique())
    processed_files: list[str] = meta["processdFiles"]
    error_files: list[str] = meta["errorFiles"]

    count = len(files)
    for idx, file in enumerate(files):
        if file in processed_files:
            utils.log(file, idx, count, "skipped")
            continue

        try:
            _handle(file, df_catalog)
            utils.log(file, idx, count, "successfully processed")

        except FileExistsError:
            utils.log(file, idx, count, "Error. File not found.")
            error_files.append(file)

        except Exception as e:
            traceback.print_exc()
            print("RUN ERROR:", e)
            error_files.append(file)

        finally:
            processed_files.append(file)
            utils.write_meta(DESTINATION_FOLDER_PATH, meta)


def _handle(file: str, df_catalog: pd.DataFrame) -> None:
    src_filename = file + ".txt"
    filepath = os.path.join(SOURCE_FOLDER_PATH, src_filename)

    if not os.path.exists(filepath):
        raise FileExistsError()

    with open(filepath, "r") as f:
        doc_json = json.loads(f.readline())

    df_result = df_catalog[df_catalog["DokName"] == file]

    pages = [
        _prepare_text(page, i, df_result, file)
        for i, page in enumerate(doc_json["pages"])
    ]

    # read file first line and parse to json

    document = {
        "documentName": file,
        "pages": pages
    }

    new_filename = f"{file}.txt"
    filepath = os.path.join(DESTINATION_FOLDER_PATH, new_filename)

    with open(filepath, "w") as f:
        document_json_str = json.dumps(document)
        orc_text = "\n".join([
            utils.prep_page_content_for_txt(page, i, len(pages))
            for i, page in enumerate(pages)
        ])

        final_text = document_json_str + "\n\n" + orc_text
        f.write(final_text)


def _prepare_text(
        page: dict,
        index: int,
        df_result: pd.DataFrame,
        doc_name: str
) -> str:
    ocr_result = page["ocr_text"]
    pdf_reader_result = page["pdfplumber"]["text"]
    tables = page["pdfplumber"]["tables"]

    typcodes = ", ".join(list(df_result["Typcode"].fillna("").astype(str).unique()))  # noqa
    device_names = ", ".join(list(df_result["Gerätebezeichnung"].fillna("").astype(str).unique()))  # noqa
    type_names = ", ".join(list(df_result["Typ/Modell"].fillna("").astype(str).unique()))  # noqa
    device_categories = ", ".join(list(df_result["Kennung"].fillna("").astype(str).unique()))  # noqa
    device_manufactorers = ", ".join(list(df_result["Hersteller"].fillna("").astype(str).unique()))  # noqa
    device_additions = ", ".join(list(df_result["Zusatz / Bemerkung"].fillna("").astype(str).unique()))  # noqa

    return f"""# DOCUMENT METADATA START #
Document name: {doc_name}
Document page number: {index + 1}
Typecodes: {typcodes}
Device names: {device_names}
Types / Models: {type_names}
Categories / Identifiers: {device_categories}
Manufacturer: {device_manufactorers}
Additions: {device_additions}
# DOCUMENT METADATA END #
# DOCUMENT CONTENT START #
## OCR RESULT
{ocr_result}
## PDF READER RESULT
{pdf_reader_result}
## PDF TABLES
{tables}
# DOCUMENT CONTENT END #
"""
