# flake8: noqa

import gvars
import requests

from requests import Response


class AzureAIChatModel:
    def __init__(
            self,
            api_key: str,
            endpoint: str,
            api_version: str,
            deployment: str
    ) -> None:
        self._api_key = api_key
        self._api_url = f"{endpoint}openai/deployments/{deployment}/chat/completions?api-version={api_version}"  # noqa
        self._deployment = deployment

    def submit(self, messages: list[dict]) -> Response:
        """
        Example:
        resp = chat.submit([
                {"role": "system", "content": [{"type": "text", "text": "You are an AI assistant that helps people find information."}]},
                {"role": "user", "content": [{"type": "text", "text": "Give me a very short definition of artificial intelligence."}]},
            ])["choices"][0]["content"]
        """
        headers = self._get_json_headers()
        data = {
            "model": self._deployment,
            "messages": messages,
            "max_tokens": 800,
            "temperature": 0.7,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        }

        response = requests.post(self._api_url, headers=headers, json=data)
        return response

    def _get_json_headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "api-key": self._api_key
        }
        return headers


chat = AzureAIChatModel(
    api_key=gvars.AZURE_OPENAI_API_KEY,
    deployment=gvars.AZURE_OPENAI_DEPLOYMENT_NAME,
    endpoint=gvars.AZURE_OPENAI_ENDPOINT,
    api_version=gvars.AZURE_OPENAI_API_VERSION
)
