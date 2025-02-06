import json

from dataclasses import dataclass, asdict


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
    def model(self) -> dict:
        return self.params.get("model", {})

    @property
    def websearch(self) -> dict:
        return self.params.get("webSearch", {})

    @property
    def vectorsearch(self) -> dict:
        return self.params.get("vectorSearch", {})

    @property
    def model_name(self) -> str:
        return self.model.get("name")

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
    def vectorsearch_enabled(self) -> bool:
        return self.vectorsearch.get("enabled", True)

    @property
    def vectorsearch_optimize_vector_search_query(self) -> bool:
        return self.vectorsearch.get("optimizeVectorSearchQuery", False)

    @property
    def vectorsearch_max_result_count(self) -> int:
        return self.vectorsearch.get("maxResultCount", 5)

    @property
    def vectorsearch_use_websearch_results(self) -> bool:
        return self.vectorsearch.get("useWebSearchResults", False)

    def get_steps(self) -> dict[dict]:
        steps = {}
        self._add_step(steps, "INITIALIZE_CONNECTION", "STARTED")

        if self.websearch_enabled:
            if self.websearch_optimize_web_search_query:
                self._add_step(steps, "OPTIMIZE_WEB_SEARCH_QUERY")

            self._add_step(steps, "EXECUTE_WEB_SEARCH")

            if self.websearch_depp_search_enabled:
                self._add_step(steps, "EXECUTE_DEEP_SEARCH")

            if (
                self.vectorsearch_enabled and
                self.vectorsearch_use_websearch_results
            ):
                self._add_step(steps, "OPTIMIZE_WEB_SEARCH_RESULT")

        if self.vectorsearch_enabled:
            if self.vectorsearch_optimize_vector_search_query:
                self._add_step(steps, "OPTIMIZE_VECTOR_SEARCH_QUERY")

            self._add_step(steps, "EXECUTE_VECTOR_SEARCH")

        self._add_step(steps, "EXECUTE_GENERATE_FINAL_MESSAGE")

        return steps

    def _add_step(
            self,
            steps: dict[dict],
            name: str,
            state: str = "NOT_STARTED"
    ) -> dict[dict]:
        steps[name] = {
            "index": len(steps.keys()),
            "name": name,
            "state": state
        }


@dataclass
class ChatPOSTYieldStateObject:
    steps: dict[dict]
    current_step: str
    status_code: int
    message: str
    error: str | None

    def to_yield(self) -> bytes:
        return json.dumps(asdict(self)) + "\n"

    def next_step(self, next_step: str) -> None:
        self.steps[self.current_step]["state"] = "FINISHED"

        self.steps[next_step]
        self.steps[next_step]["state"] = "STARTED"
        self.current_step = next_step

    def set_message(self, message: str) -> None:
        self.message = message


@dataclass(frozen=True)
class StreamResponse:
    data: dict
    status_code: int

    def to_flask_response(self) -> tuple[dict, int]:
        return (
            self.data,
            self.status_code
        )
