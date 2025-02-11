import os
import re
import traceback
import json
import tiktoken

from etl import utils
from embedding import embedding_model


SOURCE_FOLDER_PATH = "./etl/data/03-transform-content-cleanup"
DESTINATION_FOLDER_PATH = "./etl/data/04-transform-final-embeddings"


def _count_tokens(text, model="text-embedding-3-large"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def _trim_to_token_limit(
        text,
        max_tokens=8000,
        model="text-embedding-3-large"
) -> str:
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)

    if len(tokens) <= max_tokens:
        return text

    trimmed_text = encoding.decode(tokens[:max_tokens])

    return trimmed_text


def _sanitize_string_for_index_key(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9\-_]', '_', name)


def run() -> None:
    meta = utils.read_meta(DESTINATION_FOLDER_PATH)
    meta["errorFiles"] = []
    # meta["processdFiles"] = []  # DEBUG

    processed_files: list[str] = meta["processdFiles"]
    error_files: list[str] = meta["errorFiles"]

    files = [file for file in os.listdir(SOURCE_FOLDER_PATH) if file.endswith(".txt")]  # noqa

    count = len(files)
    for idx, file in enumerate(files):
        if file in processed_files:
            utils.log(file, idx, count, "skipped")
            continue

        try:
            _handle(file)
            processed_files.append(file)
            utils.log(file, idx, count, "successfully processed")

        except FileExistsError:
            utils.log(file, idx, count, "Error. File not found.")
            error_files.append(file)

        except Exception as e:
            traceback.print_exc()
            print("RUN ERROR:", e)
            error_files.append(file)

        finally:
            utils.write_meta(DESTINATION_FOLDER_PATH, meta)
            # break  # debug


def _handle(file: str) -> None:
    src_filename = file.replace(".txt", "")
    filepath = os.path.join(SOURCE_FOLDER_PATH, file)

    if not os.path.exists(filepath):
        raise FileExistsError()

    with open(filepath, "r") as f:
        doc_json = json.loads(f.readline())

    pages = [_trim_to_token_limit(page) for page in doc_json["pages"]]

    batch_count = 25
    curr_start = 0
    page_embeddings = []
    while True:
        if curr_start >= len(pages):
            break

        batch_end = curr_start + batch_count
        batch = pages[curr_start:batch_end]

        page_embeddings += embedding_model.embed(batch)
        curr_start = batch_end

    pages = [
        {
            "id": _sanitize_string_for_index_key(f"{src_filename}_page_{page_number + 1}"),  # noqa
            "documentName": src_filename,
            "documentPageNumber": page_number,
            "documentPageContent": pages[page_number],
            "documentPageContentEmbedding": embeddings
        }
        for page_number, embeddings in enumerate(page_embeddings)
    ]

    document = {
        "documentName": src_filename,
        "pages": pages
    }

    filepath = os.path.join(DESTINATION_FOLDER_PATH, file + ".embeddings.json")

    with open(filepath, "w") as f:
        document_json_str = json.dumps(document, indent=4)
        f.write(document_json_str)
