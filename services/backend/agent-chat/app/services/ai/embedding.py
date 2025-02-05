import time
import requests
import gvars

from requests import Response


class AzureDocumentEmbeddingModel:
    def __init__(
            self,
            endpoint: str,
            api_key: str
    ) -> None:
        self._endpoint = endpoint
        self._api_key = api_key

    def embed(
            self,
            embed_content: str | list[str],
            max_retries: int = 1,
            current_retries: int = 0
    ) -> Response:
        if embed_content is None or embed_content == "":
            raise Exception("give input!")
        headers = self._get_json_headers()
        data = {
            "input": embed_content
        }

        response = requests.post(self._endpoint, headers=headers, json=data)

        if response.status_code == 200 or response.status_code != 429:
            return response

        try:
            message = response.json()["error"]["message"]
            retry_time_str = message.split("retry after ")[1] \
                                    .split(" seconds")[0]
            retry_time = int(retry_time_str) + 5

            print(f"Sleep because of retry for: {retry_time}s")
            time.sleep(retry_time)

            new_current_retries = current_retries + 1
            if new_current_retries > max_retries:
                return response

            return self.embed(
                embed_content=embed_content,
                max_retries=max_retries,
                current_retries=new_current_retries
            )
        except Exception:
            return response

    def parse_response_single(self, resp: Response) -> list[float]:
        return resp.json()["data"][0]["embedding"]

    def _get_json_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "api-key": self._api_key
        }

        return headers


embedding_model = AzureDocumentEmbeddingModel(
    endpoint=gvars.EMBEDDING_MODEL_ENDPOINT,
    api_key=gvars.EMBEDDING_MODEL_API_KEY
)
