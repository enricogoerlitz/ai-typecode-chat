import os
import traceback
import json

from etl import utils
from etl import reader


SOURCE_FOLDER_PATH = os.getenv("SOURCE_DATA_PATH", None)
DESTINATION_FOLDER_PATH = "./etl/data/01-extract"


assert SOURCE_FOLDER_PATH is not None


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
            _handle(file)
            processed_files.append(file)
            utils.log(file, idx, count, "successfully processed")

        except Exception as e:
            traceback.print_exc()
            print("RUN ERROR:", e)
            error_files.append(file)

        finally:
            utils.write_meta(DESTINATION_FOLDER_PATH, meta)


def _handle(file: str) -> None:
    filepath = os.path.join(SOURCE_FOLDER_PATH, file)
    pages = reader.prepare_pdf_content(filepath)

    if pages is None:
        raise Exception(f"Error at file '{file}'.")

    document = {
        "documentName": file,
        "pages": pages
    }

    new_filename = f"{file}.txt"
    filepath = os.path.join(DESTINATION_FOLDER_PATH, new_filename)

    with open(filepath, "w") as f:
        document_json_str = json.dumps(document)
        orc_text = "\n".join([
            utils.prep_page_content_for_txt(page["ocr_text"], i, len(pages))
            for i, page in enumerate(pages)
        ])

        final_text = document_json_str + "\n\n" + orc_text
        f.write(final_text)
