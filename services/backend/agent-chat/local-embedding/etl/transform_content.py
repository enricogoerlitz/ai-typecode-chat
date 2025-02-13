import os
import re
import traceback
import json
import pandas as pd
import unicodedata

from symspellpy import SymSpell, Verbosity

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
            break  # DEBUG


def _handle(file: str, df_catalog: pd.DataFrame) -> None:
    src_filename = file + ".txt"
    filepath = os.path.join(SOURCE_FOLDER_PATH, src_filename)

    if not os.path.exists(filepath):
        raise FileExistsError()

    with open(filepath, "r") as f:
        doc_json = json.loads(f.readline())

    pages = [
        _prepare_text(page, i, df_catalog, file)
        for i, page in enumerate(doc_json["pages"])
    ]

    document = {
        "documentName": doc_json["documentName"],
        "typeCodes": doc_json["typeCodes"],
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
        df_catalog: pd.DataFrame,
        doc_name: str
) -> str:
    ocr_result = page["ocr_text"]
    pdf_reader_result = page["pdfplumber"]["text"]
    tables = page["pdfplumber"]["tables"]

    df_result = df_catalog[df_catalog["DokName"] == doc_name]

    typcodes = ", ".join(list(df_result["Typcode"].fillna("").astype(str).unique()))  # noqa
    device_names = ", ".join(list(df_result["Gerätebezeichnung"].fillna("").astype(str).unique()))  # noqa
    type_names = ", ".join(list(df_result["Typ/Modell"].fillna("").astype(str).unique()))  # noqa
    device_categories = ", ".join(list(df_result["Kennung"].fillna("").astype(str).unique()))  # noqa
    device_manufactorers = ", ".join(list(df_result["Hersteller"].fillna("").astype(str).unique()))  # noqa
    device_additions = ", ".join(list(df_result["Zusatz / Bemerkung"].fillna("").astype(str).unique()))  # noqa

    text = f"""# DOCUMENT METADATA START #
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

    return _transform_text(text)


def _transform_text(text: str) -> str:
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
    words_with_spaces = re.split(r'(\s+)', text)

    # Correct spelling but keep original whitespace
    corrected_words = [
        sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=2)[0].term if sym_spell.lookup(word, Verbosity.CLOSEST, max_edit_distance=2) else word  # noqa
        for word in words_with_spaces
    ]

    return "".join(corrected_words)
