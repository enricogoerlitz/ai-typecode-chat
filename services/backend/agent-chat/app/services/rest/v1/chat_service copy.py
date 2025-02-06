# flake8: noqa

# from flask import Response
# from typing import Iterator

# from utils.chat import ChatPOSTMessagePayloadV1
# from services.ai.promptflow.v1 import promptflow
# from exc import http_errors
# from services.ai.client import aiclient


# def handle_post_chat_message(chat_id: str, payload: dict) -> Response:
#     try:
#         cnf = ChatPOSTMessagePayloadV1(payload=payload)

#         user_message = cnf.message_content

#         websearch_result = None
#         vectorsearch_result = None

#         # 1. fetch chat history (count in payload)
#         # pass

#         # 2. execute websearch
#         if cnf.websearch_enabled:
#             websearch_result = promptflow._exec_websearch(
#                 user_message=user_message,
#                 is_deep_search=cnf.websearch_depp_search_enabled,
#                 max_result_count=cnf.websearch_max_result_count,
#                 optimize_query=cnf.websearch_optimize_web_search_query
#             )

#         websearch_result_str = websearch_result.get("result_string", "") if isinstance(websearch_result, dict) else "no results"
#         print("websearch_result_str:", websearch_result_str)

#         # 3. execute vectorsearch
#         if cnf.vectorsearch_enabled:
#             vectorsearch_result = promptflow._exec_vector_search(
#                 user_message=user_message,
#                 use_websearch_result=cnf.vectorsearch_use_websearch_results,
#                 websearch_result_str=websearch_result_str,
#                 optimize_vectorsearch_query=cnf.vectorsearch_optimize_vector_search_query,
#                 max_result_count=cnf.vectorsearch_max_result_count
#             )

#         vectorsearch_result_str = vectorsearch_result.get("result_string", "") if isinstance(vectorsearch_result, dict) else "no results"
        

#     except Exception as e:
#         print("ERR:", str(e))
#         return http_errors.UNEXPECTED_ERROR_RESULT


# def _fn() -> None:
#     pass