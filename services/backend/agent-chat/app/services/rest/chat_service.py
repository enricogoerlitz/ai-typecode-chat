# flake8: noqa

from flask import Response

from utils import chatpayload
from services.ai.promptflow.v1 import promptflow
from services.ai.embedding import embedding_model
from exc import http_errors
from services.ai.chat import chat


def handle_post_chat_message(chat_id: str, payload: dict) -> Response:
    # 0. Prepare data
    try:
        cnf = chatpayload.ChatPOSTMessagePayloadV1(payload=payload)

        user_message = cnf.message_content

        websearch_result = None
        vectorsearch_result = None

        # 1. fetch chat history (count in payload)
        # pass

        # 2. execute websearch
        if cnf.websearch_enabled:
            websearch_result = promptflow.exec_websearch_v1(
                user_message=user_message,
                is_deep_search=cnf.websearch_depp_search_enabled,
                max_result_count=cnf.websearch_max_result_count,
                optimize_query=cnf.websearch_optimize_web_search_query
            )

        websearch_result_str = websearch_result.get("result_string", "") if isinstance(websearch_result, dict) else "no results"
        print("websearch_result_str:", websearch_result_str)

        # 3. execute vectorsearch
        vectorsearch_result = promptflow.exec_vector_aisearch(
            user_message=user_message,
            use_websearch_result=cnf.vectorsearch_use_websearch_results,
            websearch_result_str=websearch_result_str,
            optimize_vectorsearch_query=cnf.vectorsearch_optimize_vector_search_query,
            max_result_count=cnf.vectorsearch_max_result_count
        )

        vectorsearch_result_str = vectorsearch_result.get("result_string", "") if isinstance(vectorsearch_result, dict) else "no results"
        system_context = f"""You are an AI assistant specializing in retrieving and synthesizing information from multiple sources to provide accurate and relevant answers.  
You will receive structured data from the following sources:  

1. **[WEBSEARCH RESULTS]** – Information gathered from web searches, which may include summarized content or deeper details from specific websites.  
2. **[DOCUMENT SEARCH RESULTS]** – Information retrieved from relevant documents, selected to provide the most useful insights for the user's query.  

Use these sources to generate well-structured, concise, and helpful responses. If information from both sources is available, prioritize accuracy and coherence when combining them. If no relevant information is found, state that explicitly rather than guessing.  

Here is the provided information:  

### [WEBSEARCH RESULTS]  
{websearch_result_str}  

### [DOCUMENT SEARCH RESULTS]  
{vectorsearch_result_str}  
"""

        # 4. Generate final response
        resp = chat.submit([
            {
                "role": "system",
                "content": [{
                    "type": "text",
                    "text": system_context
                }]
            },
            {
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": user_message
                }]
            },
        ])

        print("\n\n\n---------------SYSTEM-CONTEXT------------------\n\n")
        print(system_context)
        print("\n\n---------------------------------\n\n")

        return resp.text, 200

    except Exception as e:
        print("ERR:", str(e))
        return http_errors.UNEXPECTED_ERROR_RESULT


def _fn() -> None:
    pass
