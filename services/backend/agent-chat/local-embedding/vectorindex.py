import requests
import gvars

from typing import Literal
from abc import ABC, abstractmethod
from flask import Response
from elasticsearch_dsl import (
    Document,
    DenseVector,
    Keyword,
    Text,
    Integer,
    connections,
    Search,
    Q
)


INDEX_NAME = "emtec-device-type-agent-index"


_ = connections.create_connection(hosts=["http://localhost:9200"])


class IMTDeviceTypeDocument(Document):
    id = Keyword()
    typeCodes = Keyword(multi=True)
    documentName = Text(analyzer="standard")
    documentPageNumber = Integer()
    documentPageContent = Text(analyzer="standard")
    documentPageContentEmbedding = DenseVector(dims=3072)

    class Index:
        name = INDEX_NAME


class IVectorSearchIndex(ABC):
    @abstractmethod
    def search(self, query: dict) -> list[dict]: pass

    @abstractmethod
    def put_documents(self, documents: list) -> dict: pass

    @abstractmethod
    def generate_query(
        embeddings: list[float],
        max_result_count: int) -> dict: pass

    @abstractmethod
    def generate_query_by_typecode(
        self,
        embeddings: list[float],
        max_result_count: int,
        typeCode: str) -> dict: pass

    @staticmethod
    def create(
        index_type: Literal[
            "AZURE_AI_SEARCH",
            "ELASTICSEARCH"
        ]
    ) -> 'IVectorSearchIndex':
        match index_type:
            case "AZURE_AI_SEARCH":
                return AzureAISearchIndex(
                    service_name=gvars.SEARCH_SERVICE_NAME,
                    index_name=gvars.SEARCH_SERVICE_INDEX_NAME,
                    api_key=gvars.SEARCH_SERVICE_API_KEY,
                    api_version=gvars.SEARCH_SERVICE_API_VERSION
                )
            case "ELASTICSEARCH":
                return ElasticsearchIndex()

        err = "Index type must be 'AZURE_AI_SEARCH' or 'ELASTICSEARCH'"
        raise Exception(err)


class ElasticsearchIndex(IVectorSearchIndex):
    def __init__(self):
        super().__init__()
        IMTDeviceTypeDocument().init()

    def search(self, query: dict) -> list[dict]:
        s: Search = query["search"]
        max_result_count = query.get("max_result_count", 10)
        return [dict(hit) for hit in s.execute()][:max_result_count]

    def put_documents(self, documents: list[IMTDeviceTypeDocument]) -> dict:
        try:
            for doc in documents:
                update_doc = doc.search().filter("term", id=doc.id).execute()
                if len(update_doc) == 0:
                    doc.save()
                    continue

                update_doc: IMTDeviceTypeDocument = update_doc[0]
                update_doc.documentName = doc.documentName
                update_doc.typeCodes = doc.typeCodes
                update_doc.documentPageNumber = doc.documentPageNumber
                update_doc.documentPageContent = doc.documentPageContent
                update_doc.documentPageContentEmbedding = doc.documentPageContentEmbedding  # noqa

                update_doc.save()
        except Exception as e:
            resp = Response({"error": str(e)}, 400)
            print(resp)
            raise Exception("# TODO: errors.VectorSearchRequestException(resp)")  # noqa

    def generate_query(
            self,
            embeddings: list[float],
            max_result_count: int
    ) -> dict:
        query = {
            "search": Search(index=INDEX_NAME).knn(
                field="documentPageContentEmbedding",
                k=5,
                num_candidates=max_result_count,
                query_vector=embeddings
            )
        }

        return query

    def generate_query_by_typecode(
            self,
            embeddings: list[float],
            max_result_count: int,
            typeCode: str
    ) -> dict:
        query = {
            "search": Search(index=INDEX_NAME).query(
                "bool",
                must=[
                    Q(
                        "script_score",
                        query={
                            "bool": {
                                "filter": [
                                    {"terms": {"typeCodes": [typeCode]}}
                                ]
                            }
                        },
                        script={
                            "source": "cosineSimilarity(params.query_vector, 'documentPageContentEmbedding') + 1.0",  # noqa
                            "params": {"query_vector": embeddings}
                        }
                    )
                ]
            ),
            "max_result_count": max_result_count
        }

        return query


class AzureAISearchIndex(IVectorSearchIndex):
    def __init__(
            self,
            service_name: str,
            index_name: str,
            api_key: str,
            api_version: str
    ) -> None:
        super().__init__()

        self._put_endpoint = f"https://{service_name}.search.windows.net/indexes/{index_name}/docs/index?api-version={api_version}"  # noqa
        self._query_endpoint = f"https://{service_name}.search.windows.net/indexes/{index_name}/docs/search?api-version={api_version}"  # noqa
        self._api_key = api_key

    def search(self, query: dict) -> list[dict]:
        headers = self._get_json_headers()
        resp = requests.post(self._query_endpoint, headers=headers, json=query)

        if resp.status_code != 200:
            print("ERROR:", resp.status_code, resp.text)
            raise Exception("# errors.VectorSearchRequestException(resp)")

        return resp.json()["value"]

    def put_documents(self, documents: list) -> dict:
        if not isinstance(documents, list):
            raise TypeError("put_documents expected an list for 'documents'")

        headers = self._get_json_headers()
        payload = {
            "value": documents
        }
        resp = requests.post(self._put_endpoint, headers=headers, json=payload)

        if resp.status_code != 200:
            raise Exception("# errors.VectorSearchRequestException(resp)")

        return resp.json()

    def generate_query(
            self,
            embeddings: list[float],
            max_result_count: int
    ) -> dict:
        query = {
            "vectorQueries": [
                {
                    "vector": embeddings,
                    "k": 5,
                    "fields": "documentPageContentEmbedding",
                    "kind": "vector"
                }
            ],
            "select": "id, typeCodes, documentName, documentPageNumber, documentPageContent",  # noqa
            "top": max_result_count
        }

        return query

    def generate_query_by_typecode(
            self,
            embeddings: list[float],
            max_result_count: int,
            typeCode: str
    ) -> dict:
        query = {
            "vectorQueries": [
                {
                    "vector": embeddings,
                    "k": 5,
                    "fields": "documentPageContentEmbedding",
                    "kind": "vector"
                }
            ],
            "select": "id, typeCodes, documentName, documentPageNumber, documentPageContent",  # noqa
            "top": max_result_count,
            "filter": f"typeCodes/any(t: t eq '{typeCode}')"
        }

        return query

    def _get_json_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "api-key": self._api_key
        }

        return headers


vector_search_index = IVectorSearchIndex.create("AZURE_AI_SEARCH")
