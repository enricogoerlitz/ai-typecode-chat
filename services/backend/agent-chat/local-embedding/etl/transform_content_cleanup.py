import os
import re
import traceback
import json
import unicodedata

from symspellpy import SymSpell, Verbosity
from etl import utils


SOURCE_FOLDER_PATH = "./etl/data/02-transform-content"
DESTINATION_FOLDER_PATH = "./etl/data/03-transform-content-cleanup"


def run() -> None:
    meta = utils.read_meta(DESTINATION_FOLDER_PATH)
    meta["errorFiles"] = []
    meta["processdFiles"] = []  # DEBUG

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


def _handle(file: str) -> None:
    filepath = os.path.join(SOURCE_FOLDER_PATH, file)

    if not os.path.exists(filepath):
        raise FileExistsError()

    with open(filepath, "r") as f:
        doc_json = json.loads(f.readline())

    pages = [
        _prepare_text(text)
        for text in doc_json["pages"]
    ]

    document = {
        "documentName": file,
        "pages": pages
    }

    filepath = os.path.join(DESTINATION_FOLDER_PATH, file)

    with open(filepath, "w") as f:
        document_json_str = json.dumps(document)
        text = "\n".join([
            utils.prep_page_content_for_txt(page, i, len(pages))
            for i, page in enumerate(pages)
        ])

        final_text = document_json_str + "\n\n" + text
        f.write(final_text)


def _prepare_text(text: str) -> str:
    metadata_end_term = "# DOCUMENT METADATA END #"
    metadata, content = text.split(metadata_end_term)

    metadata = _to_lowercase(metadata)

    content = _to_lowercase(content)
    content = _clean_newlines(content)
    content = _fix_hyphenation(content)
    content = _normalize_unicode(content)
    content = _correct_spelling(content)

    replace_values = [
        "# DOCUMENT CONTENT START #",
        "# DOCUMENT CONTENT END #",
        "## OCR RESULT",
        "## PDF READER RESULT",
        "## PDF TABLES"
    ]
    for replace_value in replace_values:
        content = content.replace(replace_value.lower(), replace_value)

    return "".join([metadata, metadata_end_term, content])


def _clean_newlines(text: str):
    # Replace multiple newlines with a single newline
    text = re.sub(r"\n{2,}", "\n\n", text)  # Preserve paragraph breaks

    return text


def _fix_hyphenation(text: str) -> str:
    # Joins broken words at line breaks
    return re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)


def _normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def _to_lowercase(text: str) -> str:
    return text.lower()


def _correct_spelling(text: str) -> str:
    sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)

    # Preserve spaces & newlines while splitting
    words_with_spaces = re.split(r'(\s+)', text)  # Keeps spaces, newlines, and tabs  # noqa

    # Correct spelling but keep original whitespace
    corrected_words = [
        sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=2)[0].term if sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=2) else word  # noqa
        for word in words_with_spaces
    ]

    return "".join(corrected_words)
