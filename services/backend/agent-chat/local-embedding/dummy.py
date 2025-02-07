import os
import re
import json
import utils
from embedding import embedding_model  # noqa
from vectorindex import vector_search_index, IMTDeviceTypeDocument  # noqa


def _sanitize_string_for_index_key(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9\-_]', '_', name)


def import_dummy() -> None:
    DATA_FOLDER = "../../../../resources/data/dummy"

    file_data = {}
    for root, _, files in os.walk(DATA_FOLDER):
        for filename in files:
            # if not filename.startswith("nik"):
            #     continue
            file_path = os.path.join(root, filename)
            text_data = utils.extract_text(file_path)
            if text_data is None:
                print("FILE\t", filename, "\tNot supported\n")
                continue

            print("FILE\t", filename, "\tProcess started")

            file_data[filename] = text_data
            embeddings = embedding_model.embed(text_data)

            document_id = "document_id_follows"
            documents = [
                IMTDeviceTypeDocument(
                    id=_sanitize_string_for_index_key(f"{document_id}_{filename}_page_{page_number + 1}"),  # noqa
                    deviceID="dummy",
                    deviceTypeID="dummy",
                    documentID="dummy",
                    documentName=filename,
                    documentPageNumber=page_number + 1,
                    documentPageContent=text_data[page_number],
                    documentPageContentEmbedding=embedding,
                    metadata_json=json.dumps({
                        "dummy": "data"
                    })
                )
                for page_number, embedding in enumerate(embeddings)
            ]

            vector_search_index.put_documents(documents)
            print("FILE\t", filename, "\tSuccessfully processed\n")

    print("FINISHED PROCESS")
