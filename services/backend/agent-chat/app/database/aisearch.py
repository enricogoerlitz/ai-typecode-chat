# flake8: noqa
import re

import requests

import gvars

from requests import Response


def sanitize_string_for_index_key(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9\-_]', '_', name)


class AzureAISearchIndex:
    def __init__(
            self,
            service_name: str,
            index_name: str,
            api_key: str,
            api_version: str
    ) -> None:
        self._put_endpoint = f"https://{service_name}.search.windows.net/indexes/{index_name}/docs/index?api-version={api_version}"
        self._query_endpoint = f"https://{service_name}.search.windows.net/indexes/{index_name}/docs/search?api-version={api_version}"
        self._api_key = api_key
    
    def search(self, query: dict) -> Response:
        headers = self._get_json_headers()
        response = requests.post(self._query_endpoint, headers=headers, json=query)
        return response

    def put_documents(self, documents: list) -> Response:
        if not isinstance(documents, list):
            raise TypeError("put_documents expected an list for 'documents'")
    
        headers = self._get_json_headers()
        payload = {
            "value": documents
        }
        response = requests.post(self._put_endpoint, headers=headers, json=payload)
        return response

    def _get_json_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "api-key": self._api_key
        }

        return headers


azure_search_index = AzureAISearchIndex(
    service_name=gvars.SEARCH_SERVICE_NAME,
    index_name=gvars.SEARCH_SERVICE_INDEX_NAME,
    api_key=gvars.SEARCH_SERVICE_API_KEY,
    api_version=gvars.SEARCH_SERVICE_API_VERSION
)
