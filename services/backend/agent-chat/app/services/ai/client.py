# flake8: noqa

import json
import gvars
import requests

from exc import errors
from abc import ABC, abstractmethod
from typing import Iterator, Literal
from requests import Response
from utils.chat import StreamResponse


class IChatModel(ABC):
    @abstractmethod
    def submit(messages: list[dict], model: str) -> Response: pass

    @abstractmethod
    def submit_stream(
        messages: list[dict],
        model: str,
        current_message: str) -> Iterator[StreamResponse]: pass


class IEmbeddingModel(ABC):
    @abstractmethod
    def embed(embed_content: str | list[str]) -> list[list[float]]: pass


class IAIClient(ABC):
    @property
    def chat() -> IChatModel: pass

    @property
    def embedding_model() -> IEmbeddingModel: pass

    @staticmethod
    def create(ai_client_type: Literal["OPENAI"]) -> 'IAIClient':
        match ai_client_type:
            case "OPENAI":
                return OpenAIClient(
                    api_key=gvars.OPENAI_API_KEY,
                    chat_endpoint=gvars.OPENAI_API_ENDPOINT_CHAT_COMPLEATIONS,
                    embedding_endpoint=gvars.OPENAI_API_ENDPOINT_EMBEDDINGS
                )

        err = f"AIClient type must be 'OPENAI'."
        raise errors.ValueErrorGeneral(err)


class OpenAIChatModel(IChatModel):
    def __init__(
            self,
            api_key: str,
            chat_endpoint: str
    ):
        self._api_key = api_key
        self._api_url = chat_endpoint

    def submit(
            self,
            messages: list[dict],
            model: str
    ) -> Response:
        headers = self._get_json_headers()
        req = {
            "model": model,
            "messages": messages
        }

        resp = requests.post(self._api_url, headers=headers, json=req)

        if resp.status_code == 429:
            raise errors.AIClientRateLimitError(resp)
        elif resp.status_code != 200:
            raise errors.RequestsException(resp)

        return resp.json()["choices"][0]["message"]["content"]

    def submit_stream(
            self,
            messages: list[dict],
            model: str,
            current_message: str = ""
    ) -> Iterator[StreamResponse]:
        headers = self._get_json_headers()
        req = {
            "model": model,
            "messages": messages,
            "stream": True
        }

        with requests.post(self._api_url, headers=headers, json=req, stream=True) as resp:
            if resp.status_code == 429:
                raise errors.AIClientRateLimitError(resp)
            elif resp.status_code != 200:
                raise errors.RequestsException(resp)

            for line in resp.iter_lines():
                if line is None:
                    continue

                stream_resp = self._generate_stream_yield_response(
                    line=line,
                    current_message=current_message
                )
                current_message = stream_resp.data["message"]

                yield stream_resp

    def _get_json_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}"
        }
        return headers

    def _generate_stream_yield_response(
            self,
            line: str,
            current_message: str
    ) -> StreamResponse:
        try:
            resp_data = {
                "message": current_message
            }

            decoded_line = line.decode("utf-8").strip()
            decoded_line = decoded_line[len("data: "):]

            json_data: dict = json.loads(decoded_line)
            content = json_data["choices"][0]["delta"].get("content", "")

            current_message += content
            resp_data["message"] = current_message

            return StreamResponse(resp_data, 200)

        except Exception:
            return StreamResponse(resp_data, 200)


class OpenAIEmbeddingModel(IEmbeddingModel):
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
            raise errors.AIClientRateLimitError(resp)
        elif resp.status_code != 200:
            raise errors.RequestsException(resp)

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


class OpenAIClient(IAIClient):
    def __init__(
            self,
            api_key: str,
            chat_endpoint: str,
            embedding_endpoint: str,
    ):
        self._chat = OpenAIChatModel(
            api_key=api_key,
            chat_endpoint=chat_endpoint
        )
        self._embedding_model = OpenAIEmbeddingModel(
            api_key=api_key,
            embedding_endpoint=embedding_endpoint
        )

    @property
    def chat(self) -> OpenAIChatModel:
        return self._chat

    @property
    def embedding_model(self) -> OpenAIEmbeddingModel:
        return self._embedding_model


aiclient = IAIClient.create("OPENAI")
