class ChatPOSTMessagePayloadV1:
    def __init__(self, payload: dict):
        self._payload = payload

    @property
    def message(self) -> dict:
        return self._payload.get("message", {})

    @property
    def params(self) -> dict:
        return self._payload.get("requestParameters", {})

    @property
    def prompt(self) -> dict:
        return self.params.get("prompt", {})

    @property
    def chat(self) -> dict:
        return self.params.get("chat", {})

    @property
    def websearch(self) -> dict:
        return self.params.get("webSearch", {})

    @property
    def vectorsearch(self) -> dict:
        return self.params.get("vectorSearch", {})

    @property
    def message_type(self) -> str | None:
        return self.message.get("type")

    @property
    def message_content(self) -> str | None:
        return self.message.get("content")

    @property
    def websearch_enabled(self) -> bool:
        return self.websearch.get("enabled", False)

    @property
    def websearch_depp_search_enabled(self) -> bool:
        return self.websearch.get("deepSearchEnabled", False)

    @property
    def websearch_max_result_count(self) -> int:
        return self.websearch.get("maxResultCount", 5)

    @property
    def websearch_optimize_web_search_query(self) -> bool:
        return self.websearch.get("optimizeWebSearchQuery", False)

    @property
    def vectorsearch_optimize_vector_search_query(self) -> bool:
        return self.vectorsearch.get("optimizeVectorSearchQuery", False)

    @property
    def vectorsearch_max_result_count(self) -> int:
        return self.vectorsearch.get("maxResultCount", 5)

    @property
    def vectorsearch_use_websearch_results(self) -> bool:
        return self.vectorsearch.get("useWebSearchResults", False)
