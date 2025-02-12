import os
import traceback
import json

from etl import utils
from vectorindex import vector_search_index


SOURCE_FOLDER_PATH = "./etl/data/04-transform-final-embeddings"


def run() -> None:
    files = [file for file in os.listdir(SOURCE_FOLDER_PATH) if file.endswith(".txt.embeddings.json")]  # noqa

    count = len(files)
    for idx, file in enumerate(files):
        try:
            _handle(file)
            utils.log(file, idx, count, "successfully processed")

        except FileExistsError:
            utils.log(file, idx, count, "Error. File not found.")

        except Exception as e:
            traceback.print_exc()
            print("RUN ERROR:", e)
            break


def _handle(file: str) -> None:
    filepath = os.path.join(SOURCE_FOLDER_PATH, file)

    if not os.path.exists(filepath):
        raise FileExistsError()

    with open(filepath, "r") as f:
        doc_json = json.loads(f.read())

    doc_name = doc_json["documentName"]
    doc_pages = doc_json["pages"]
    type_codes = doc_json["typeCodes"]
    pages = [
       {
            "id": page["id"],
            "typeCodes": type_codes,
            "documentName": doc_name,
            "documentPageNumber": page["documentPageNumber"],
            "documentPageContent": page["documentPageContent"],
            "documentPageContentEmbedding": page["documentPageContentEmbedding"]  # noqa
        } for page in doc_pages
    ]

    vector_search_index.put_documents(pages)
