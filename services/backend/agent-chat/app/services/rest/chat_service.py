# flake8: noqa

from flask import Response

from utils import chatpayload
from services.ai.v1.promptflow import promptflow
from services.ai.v1.promptflow.promptflow import exec_vector_aisearch


def handle_post_chat_message(chat_id: str, payload: dict) -> Response:
    # 0. Prepare data
    cnf = chatpayload.ChatPOSTMessagePayloadV1(payload=payload)

    user_message = cnf.message_content
    websearch_result = None
    vectorsearch_result = None

    # 1. fetch chat history (count in payload)
    # pass

    # 2. embed message, if is text
    if cnf.message_type == "text":
        # TODO: embed
        pass

    if cnf.websearch_enabled:
        websearch_result = promptflow.exec_websearch_v1(
            user_message=user_message,
            is_deep_search=cnf.websearch_depp_search_enabled,
            max_result_count=cnf.websearch_max_result_count
        )

    vectorsearch_result = promptflow.exec_vector_aisearch(
        user_message=user_message,
        use_websearch_result=cnf.vectorsearch_use_websearch_results,
        websearch_result=websearch_result,
        optimize_vectorsearch_query=cnf.vectorsearch_optimize_vector_search_query,
        max_result_count=cnf.vectorsearch_max_result_count
    )

    return cnf, 200
