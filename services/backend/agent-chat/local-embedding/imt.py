# flake8: noqa
import os
import re
import pandas as pd
import traceback
import utils
import json

from datetime import datetime
from embedding import embedding_model  # noqa
from vectorindex import vector_search_index, IMTDeviceTypeDocument  # noqa


DATA_FOLDER_PATH = "../../../../resources/data/imt/files"
XL_FILES_PATH = "../../../../resources/data/imt/files.xlsx"
XL_DEVICE_TYPES_PATH = "../../../../resources/data/imt/imt_deviceTypes.xlsx"

TRANSFORMED_DATA_PATH = "./documents"
TRANSFORMED_META_PATH = "./documents/__meta.json"


def _sanitize_string_for_index_key(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9\-_]', '_', name)


def transform_imt() -> None:
    metadata: dict = {
        "matermarkIndex": 0,
        "errors": []
    }

    with open(TRANSFORMED_META_PATH, "r") as f:
        metadata = json.loads(f.read())

    if metadata["matermarkIndex"] == 0:
        metadata["errors"] = []

    watermark_index = metadata["matermarkIndex"]

    print("\n\n\nSTART LOADING EXCEL FILES")
    df_files = pd.read_excel(XL_FILES_PATH)[["DokID", "Typcode", "DokName"]]
    df_device_types = pd.read_excel(XL_DEVICE_TYPES_PATH)[["Typcode", "Gerät ID"]]

    df = pd.merge(df_files, df_device_types, how="inner", on="Typcode")

    errors: list[str] = metadata["errors"]
    total_count = df["Typcode"].count()

    print(f"START TRANSFORMING: {total_count} FILES\n\n")
    for idx, row in df.iloc[watermark_index:].iterrows():
        cidx = idx + 1
        doc_name = row["DokName"]
        metadata["matermarkIndex"] = cidx

        try:
            _handle_save(row)

            dtime = str(datetime.now())[:19]
            msg = f"[{dtime}]\tPROCESS: {cidx} / {total_count}\tFile '{doc_name}' successfully transformed.\n"
            print(msg)
        except Exception as e:
            traceback.print_exc()
            msg = f"PROCESS: {cidx} / {total_count}\tError at file {doc_name}. Err: {e}\n"
            print(msg)
            errors.append(msg)
        finally:
            with open(TRANSFORMED_META_PATH, "w") as f:
                f.write(json.dumps(metadata))


    print("\n\n\n-------------------- ERRORS --------------------\n\n")
    if len(errors) == 0:
        print("No errors :)")
    else:
        for err in errors:
            print(err)
    print("\n\n------------------ END ERRORS ------------------")


def import_imt() -> None:
    print("\n\n\nSTART LOADING EXCEL FILES")
    df_files = pd.read_excel(XL_FILES_PATH)[["DokID", "Typcode", "DokName"]]
    df_device_types = pd.read_excel(XL_DEVICE_TYPES_PATH)[["Typcode", "Gerät ID"]]

    df = pd.merge(df_files, df_device_types, how="inner", on="Typcode")

    errors = []
    total_count = df["Typcode"].count()

    print(f"START INDEXING: {total_count} FILES\n\n")
    for idx, row in df.iterrows():
        cidx = idx + 1
        doc_name = row["DokName"]

        try:
            _handle_import(row)

            msg = f"PROCESS: {cidx} / {total_count}\tFile '{doc_name}' successfully indexed.\n"
            print(msg)
            # break  # TODO DEBUG!
        except Exception as e:
            msg = f"PROCESS: {cidx} / {total_count}\tError at file {doc_name}. Err: {e}\n"
            print(msg)
            errors.append(msg)

    print("\n\n\n-------------------- ERRORS --------------------\n\n")
    if len(errors) == 0:
        print("No errors :)")
    else:
        for err in errors:
            print(err)
    print("\n\n------------------ END ERRORS ------------------")


def _handle_import(row: dict) -> None:
    typcode = row["Typcode"]
    doc_id = row["DokID"]
    doc_name = row["DokName"]
    device_id = row["Gerät ID"]

    file_path = os.path.join(DATA_FOLDER_PATH, doc_name)
    text_data = utils.extract_text(file_path)

    if text_data is None:
        raise Exception(f"File '{doc_name}' not supported.")

    embeddings = embedding_model.embed(text_data)

    documents = [
        IMTDeviceTypeDocument(
            id=_sanitize_string_for_index_key(f"{doc_id}_{doc_name}_page_{page_number + 1}"),  # noqa
            deviceID=device_id,
            deviceTypeID=typcode,
            documentID=doc_id,
            documentName=doc_name,
            documentPageNumber=page_number + 1,
            documentPageContent=text_data[page_number],
            documentPageContentEmbedding=embedding,
            metadata_json=""
        )
        for page_number, embedding in enumerate(embeddings)
    ]

    vector_search_index.put_documents(documents)


def _handle_save(row: dict) -> None:
    typcode = row["Typcode"]
    doc_id = row["DokID"]
    doc_name = row["DokName"]
    device_id = row["Gerät ID"]

    filepath = os.path.join(DATA_FOLDER_PATH, doc_name)
    pages = utils.prepare_pdf_content(filepath)

    if pages is None:
        raise Exception(f"File '{doc_name}' not supported.")

    document = {
        "doc_id": doc_id,
        "doc_name": doc_name,
        "typcode": typcode,
        "device_id": device_id,
        "pages": pages
    }

    filepath = TRANSFORMED_DATA_PATH + "/" + doc_name + ".imt.txt"
    with open(filepath, "w") as f:
        document_json_str = json.dumps(document)
        orc_text = "\n".join([
            _prep_page_content_for_txt(page["ocr_text"], i, len(pages))
            for i, page in enumerate(pages)
        ])

        final_text = document_json_str + "\n\n" + orc_text
        f.write(final_text)


def _prep_page_content_for_txt(ocr_text: str, pnum: int, psum: int) -> str:
    return f"\n###################### Page {pnum+1} of {psum} ######################\n{ocr_text}"
