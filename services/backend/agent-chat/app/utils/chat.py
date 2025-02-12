import json

from dataclasses import dataclass, asdict


INITIALIZE_CONNECTION = "INITIALIZE_CONNECTION"
OPTIMIZE_WEB_SEARCH_QUERY = "OPTIMIZE_WEB_SEARCH_QUERY"
EXECUTE_WEB_SEARCH = "EXECUTE_WEB_SEARCH"
EXECUTE_DEEP_SEARCH = "EXECUTE_DEEP_SEARCH"
OPTIMIZE_WEB_SEARCH_RESULT = "OPTIMIZE_WEB_SEARCH_RESULT"
OPTIMIZE_VECTOR_SEARCH_QUERY = "OPTIMIZE_VECTOR_SEARCH_QUERY"
EXECUTE_VECTOR_SEARCH = "EXECUTE_VECTOR_SEARCH"
EXECUTE_GENERATE_FINAL_MESSAGE = "EXECUTE_GENERATE_FINAL_MESSAGE"

USE_DATA_ONLY = "USE_DATA_ONLY"
USE_HYBRID_PRIORITIZE_DATA = "USE_HYBRID_PRIORITIZE_DATA"
USE_HYBRID = "USE_HYBRID"


class ChatMessagePayload:
    def __init__(self, chat_id: str, payload: dict):
        self._payload = payload
        self._chat_id = chat_id

    @property
    def payload(self) -> dict:
        return self._payload

    @property
    def chat_id(self) -> str:
        return self._chat_id

    @property
    def message_id(self) -> str:
        return self.payload.get("_id", None)

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
    def context(self) -> dict:
        return self.params.get("context", {})

    @property
    def model_dict(self) -> dict:
        return self.params.get("model", {})

    @property
    def websearch(self) -> dict:
        return self.params.get("webSearch", {})

    @property
    def vectorsearch(self) -> dict:
        return self.params.get("vectorSearch", {})

    @property
    def model_name(self) -> str:
        return self.model_dict.get("name")

    @property
    def context_device_type_code(self) -> str:
        return self.context.get("deviceTypeCode", None)

    @property
    def chat_response_type(self) -> int:
        return self.chat.get("responseType", USE_DATA_ONLY)

    @property
    def chat_history_count(self) -> int:
        return self.chat.get("messageHistoryCount", 0)

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
    def websearch_optimize_web_search_results(self) -> bool:
        return self.websearch.get("optimizeWebSearchResults", False)

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

    def validate(self) -> None:
        return

    def get_steps(self) -> dict[dict]:
        steps = {}
        self._add_step(steps, INITIALIZE_CONNECTION, "STARTED")

        if self.websearch_enabled:
            if self.websearch_optimize_web_search_query:
                self._add_step(steps, OPTIMIZE_WEB_SEARCH_QUERY)

            self._add_step(steps, EXECUTE_WEB_SEARCH)

            if self.websearch_depp_search_enabled:
                self._add_step(steps, EXECUTE_DEEP_SEARCH)

            if (
                self.websearch_optimize_web_search_results or
                self.vectorsearch_use_websearch_results
            ):
                self._add_step(steps, OPTIMIZE_WEB_SEARCH_RESULT)

        if self.vectorsearch_enabled:
            if self.vectorsearch_optimize_vector_search_query:
                self._add_step(steps, OPTIMIZE_VECTOR_SEARCH_QUERY)

            self._add_step(steps, EXECUTE_VECTOR_SEARCH)

        self._add_step(steps, EXECUTE_GENERATE_FINAL_MESSAGE)

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
class ChatPUTYieldStateObject:
    steps: dict[dict]
    currentStep: str
    statusCode: int
    message: str
    error: str | None

    def to_yield(self) -> bytes:
        return json.dumps(asdict(self)) + "\n"

    def next_step(self, next_step: str) -> None:
        self.steps[self.currentStep]["state"] = "FINISHED"

        self.steps[next_step]["state"] = "STARTED"
        self.currentStep = next_step

    def set_message(self, message: str) -> None:
        self.message = message

    def append_message(self, message: str, break_lines: int = 1) -> None:
        if self.message == "":
            self.message = message
            return

        lines = "\n" * break_lines
        self.message = lines.join([self.message, message])


@dataclass(frozen=True)
class StreamResponse:
    data: dict
    status_code: int

    def to_flask_response(self) -> tuple[dict, int]:
        return (
            self.data,
            self.status_code
        )
