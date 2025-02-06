# flake8: noqa
import re
import requests
import gvars

from typing import Literal
from abc import ABC, abstractmethod
from exc import errors


def sanitize_string_for_index_key(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9\-_]', '_', name)


class IVectorSearchIndex(ABC):
    @abstractmethod
    def search(self, query: dict) -> list[dict]: pass

    @abstractmethod
    def put_documents(self, documents: list) -> dict: pass

    @abstractmethod
    def generate_query(
        embeddings: list[float],
        max_result_count: int) -> dict: pass

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
                return ElasticsearchIndex(
                    host="",
                    port="",
                    index_name=""
                )

        err = f"Index type must be 'AZURE_AI_SEARCH' or 'ELASTICSEARCH'"
        raise errors.ValueErrorGeneral(err)


class AzureAISearchIndex(IVectorSearchIndex):
    def __init__(
            self,
            service_name: str,
            index_name: str,
            api_key: str,
            api_version: str
    ) -> None:
        super().__init__()

        self._put_endpoint = f"https://{service_name}.search.windows.net/indexes/{index_name}/docs/index?api-version={api_version}"
        self._query_endpoint = f"https://{service_name}.search.windows.net/indexes/{index_name}/docs/search?api-version={api_version}"
        self._api_key = api_key
    
    def search(self, query: dict) -> list[dict]:
        headers = self._get_json_headers()
        resp = requests.post(self._query_endpoint, headers=headers, json=query)

        if resp.status_code != 200:
            raise errors.VectorSearchRequestException(resp)

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
            raise errors.VectorSearchRequestException(resp)

        return resp.json()

    def generate_query(self, embeddings: list[float], max_result_count: int) -> dict:
        query = {
            # "search": search_term,  # Text search query
            "vectorQueries": [
                {
                    "vector": embeddings,
                    "k": 5,
                    "fields": "documentPageContentEmbedding",
                    "kind": "vector"
                }
            ],
            # "searchFields": "documentPageContent",  # Keyword search field
            "select": "id, deviceID, deviceTypeID, documentID, documentName, documentPageNumber, documentPageContent, metadata_json",  # noqa
            "top": max_result_count
        }

        return query

    def _get_json_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "api-key": self._api_key
        }

        return headers


class ElasticsearchIndex(IVectorSearchIndex):
    def __init__(
            self,
            host: str,
            port: str,
            index_name: str,
    ):
        super().__init__()

    def search(self, query: dict) -> list[dict]:
        raise NotImplementedError()

    def put_documents(self, documents: list) -> dict:
        raise NotImplementedError()

    def generate_query(embeddings, max_result_count):
        raise NotImplementedError()


vector_search_index = IVectorSearchIndex.create(gvars.VECTOR_SEARCH_SERVICE_TYPE)
