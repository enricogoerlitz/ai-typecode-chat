import os
import requests


class OpenAIEmbeddingModel:
    def __init__(
            self,
            api_key: str,
            embedding_endpoint: str
    ):
        self._api_key = api_key
        self._api_url = embedding_endpoint

    def embed(
            self,
            embed_content: str | list[str]
    ) -> list[list[float]]:
        if embed_content is None or embed_content == "":
            raise ValueError(f"The embed_content cannot be '{embed_content}'")

        headers = self._get_json_headers()
        data = {
            "input": embed_content,
            "model": "text-embedding-3-large"
        }

        resp = requests.post(self._api_url, headers=headers, json=data)

        if resp.status_code == 429:
            raise Exception("RATE LIMIT ERROR " + resp.text)  # noqa errors.AIClientRateLimitError(resp)
        elif resp.status_code != 200:
            raise Exception("EMBEDDING ERROR: " + str(resp.status_code) + resp.text)  # noqa errors.RequestsException(resp)  noqa

        return [
            embedding["embedding"]
            for embedding in resp.json().get("data", [])
        ]

    def _get_json_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}"
        }
        return headers


embedding_model = OpenAIEmbeddingModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    embedding_endpoint=os.getenv("OPENAI_API_ENDPOINT_EMBEDDINGS")
)
