# flake8: noqa

import json
import traceback

from typing import Iterator

from logger import logger
from exc import errors
from services.ai.client import aiclient
from services.websearch.v1.websearch import (
    serp_client, SERPResponseObject,
    fetch_url_content
)
from database.vectorsearch import vector_search_index
from utils.chat import (
    ChatPOSTMessagePayloadV1,
    StreamResponse,
    ChatPOSTYieldStateObject,
    INITIALIZE_CONNECTION,
    OPTIMIZE_WEB_SEARCH_QUERY,
    EXECUTE_WEB_SEARCH,
    EXECUTE_DEEP_SEARCH,
    OPTIMIZE_WEB_SEARCH_RESULT,
    OPTIMIZE_VECTOR_SEARCH_QUERY,
    EXECUTE_VECTOR_SEARCH,
    EXECUTE_GENERATE_FINAL_MESSAGE
)


def execute(cnf: ChatPOSTMessagePayloadV1) -> Iterator[bytes]:
    # 0. Prepare state and data
    yield_state = ChatPOSTYieldStateObject(
        steps=cnf.get_steps(),
        current_step=INITIALIZE_CONNECTION,
        status_code=200,
        message="",
        error=None
    )

    try:
        yield yield_state.to_yield()

        user_message = cnf.message_content

        websearch_result = {"result_string": "no results"}
        vectorsearch_result = {"result_string": "no results"}

        # 1. fetch chat history (count in payload)
        # TODO: fetch chat history (count in payload)
        chat_history = []

        # 2. execute websearch
        if cnf.websearch_enabled:
            for websearch_result in _exec_websearch(
                yield_state=yield_state,
                user_message=user_message,
                is_deep_search=cnf.websearch_depp_search_enabled,
                max_result_count=cnf.websearch_max_result_count,
                optimize_query=cnf.websearch_optimize_web_search_query,
                optimize_websearch_result=cnf.websearch_optimize_web_search_results,
                model=cnf.model_name
            ):
                yield yield_state.to_yield()

        # 3. execute vectorsearch
        if cnf.vectorsearch_enabled:
            for vectorsearch_result in _exec_vector_search(
                yield_state=yield_state,
                user_message=user_message,
                use_websearch_result=cnf.vectorsearch_use_websearch_results,
                websearch_result_str=websearch_result.get("result_string", "no results"),
                optimize_vectorsearch_query=cnf.vectorsearch_optimize_vector_search_query,
                max_result_count=cnf.vectorsearch_max_result_count,
                model=cnf.model_name
            ):
                yield yield_state.to_yield()

        # 4. execute final chat message
        for _ in _exec_generate_final_response(
            yield_state=yield_state,
            user_message=user_message,
            chat_history=chat_history,
            websearch_result=websearch_result,
            vectorsearch_result=vectorsearch_result,
            model=cnf.model_name
        ):
            yield yield_state.to_yield()

    except errors.AIClientRateLimitError as e:
        logger.warning(e)

        yield_state.error = str(e)
        yield_state.status_code = 429

        yield yield_state.to_yield()

    except (errors.RequestsException, Exception) as e:
        logger.error(e, exc_info=True)

        yield_state.error = "An unexpected error has occored."
        yield_state.status_code = 500

        yield yield_state.to_yield()


def _exec_websearch(
        yield_state: ChatPOSTYieldStateObject,
        user_message: str,
        is_deep_search: bool,
        max_result_count: int,
        optimize_query: bool,
        optimize_websearch_result: bool,
        model: str
) -> Iterator[dict]:
    google_query = user_message
    if optimize_query:
        yield_state.next_step(OPTIMIZE_WEB_SEARCH_QUERY)
        yield_state.append_message("\nOptimizing your question for websearch to:\n")
        yield

        for google_query in _optimize_websearch_query(
            yield_state=yield_state,
            user_message=user_message,
            model=model
        ):
            yield

    yield_state.next_step(EXECUTE_WEB_SEARCH)
    yield_state.append_message("\nSearching the web for you...:\n")
    yield

    serp_obj = serp_client.search(
        query=google_query,
        max_results=max_result_count
    )

    yield_state.append_message(json.dumps(serp_obj.obj, indent=2))
    yield

    if is_deep_search:
        for _ in _exec_deep_websearch(
            yield_state=yield_state,
            user_message=user_message,
            serp_obj=serp_obj,
            model=model
        ):
            yield

    if optimize_websearch_result:
        # TODO: implement; kein yield, einfach batch abfrage!
        pass
    
    yield {
        "query_result": serp_obj,
        "result_string": str(serp_obj.obj)
    }


def _exec_vector_search(
        yield_state: ChatPOSTYieldStateObject,
        user_message: str,
        use_websearch_result: str,
        websearch_result_str: str,
        optimize_vectorsearch_query: bool,
        max_result_count: int,
        model: str
) -> Iterator[dict]:
    if use_websearch_result:
        optimize_vectorsearch_query = True

    message = user_message

    if optimize_vectorsearch_query:
        for message in _optimize_vectorsearch_query(
            yield_state=yield_state,
            user_message=user_message,
            use_websearch_result=use_websearch_result,
            websearch_result_str=websearch_result_str,
            model=model
        ):
            yield

    yield_state.next_step(EXECUTE_VECTOR_SEARCH)

    embeddings = aiclient.embedding_model.embed(message)[0]

    search_results = vector_search_index.search(
        query=vector_search_index.generate_query(
            embeddings=embeddings,
            max_result_count=max_result_count
        )
    )

    if len(search_results) > max_result_count:
        search_results = search_results[:max_result_count-1]

    search_results_str = "### Document search results"
    for i, result in enumerate(search_results):
        search_results_str = _add_vectorsearch_result_string(
            prompt=search_results_str,
            result=result,
            result_number=i
        )

    yield {
        "query_result": search_results,
        "result_string": search_results_str
    }


def _exec_deep_websearch(
        yield_state: ChatPOSTYieldStateObject,
        serp_obj: SERPResponseObject,
        user_message: str,
        model: str
) -> Iterator:
    yield_state.next_step(EXECUTE_DEEP_SEARCH)
    yield_state.append_message("\nExecuting deep search for you:\n")
    yield

    deep_search_results = []
    for link in serp_obj.get_links():
        yield_state.append_message(f"Processing link: {link}\n")

        html_text = fetch_url_content(link)
        for summary in _summarize_html_content(
            yield_state=yield_state,
            user_message=user_message,
            html_content=html_text,
            model=model
        ):
            yield

        deep_search_results.append({
            "requested_link": link,
            "requested_link_content_summary": summary
        })
    
    serp_obj.set_deep_search_results(deep_search_results)


def _exec_generate_final_response(
        yield_state: ChatPOSTYieldStateObject,
        user_message: str,
        chat_history: list[dict],
        websearch_result: dict,
        vectorsearch_result: dict,
        model: str
) -> Iterator[ChatPOSTYieldStateObject]:
    yield_state.next_step(EXECUTE_GENERATE_FINAL_MESSAGE)
    yield_state.append_message("\n\n\n### Final result:\n")

    websearch_result_str = websearch_result.get("result_string", "no results")
    vectorsearch_result_str = vectorsearch_result.get("result_string", "")

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
    resp: StreamResponse
    for resp in aiclient.chat.submit_stream([
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
    ], model=model, current_message=yield_state.message):
        new_message = resp.data["message"]
        if yield_state.message == new_message:
            continue

        yield_state.set_message(new_message)
        yield


def _add_vectorsearch_result_string(
        prompt: str,
        result: dict,
        result_number: int
) -> str:
    score = result["@search.score"]
    document_name = result["documentName"]
    document_page_number = result["documentPageNumber"]
    ducument_page_content = result["documentPageContent"]

    return f"""{prompt}
#### document result {result_number}
azure_ai_search_score: {score}
document_name: {document_name}
document_page_number: {document_page_number}
ducument_page_content:
{ducument_page_content}
""".strip()


def _optimize_websearch_query(
        yield_state: ChatPOSTYieldStateObject,
        user_message: str,
        model: str
) -> Iterator:

    system_context = f"""You are an AI assistant specializing in constructing highly effective Google search queries.  

### **Task:**  
Your goal is to generate an optimized Google search query based on the user's message.  

### **Input Source:**  
1. **[USER MESSAGE]** – The user's original query. Use this as the basis to generate the best possible Google search query.  

### **Instructions:**  
- Output **only** the optimized Google search query—nothing else.  
- The query should be **short, precise, and highly relevant** to the user’s intent.  
- Focus on structuring the query in a way that maximizes the effectiveness of Google’s search algorithm.  
- Avoid including explanations, formatting, or any additional text.  
"""

    resp: StreamResponse
    for resp in aiclient.chat.submit_stream([
        {"role": "system", "content": system_context},
        {"role": "user", "content": user_message},
    ], model=model, current_message=yield_state.message):
        new_message = resp.data["message"]
        if yield_state.message == new_message:
            continue

        yield_state.set_message(new_message)
        yield

    yield resp.data["message"]

def _optimize_vectorsearch_query(
        yield_state: ChatPOSTYieldStateObject,
        user_message: str,
        use_websearch_result: bool,
        websearch_result_str: str,
        model: str
) -> Iterator[str]:
    yield_state.next_step(OPTIMIZE_VECTOR_SEARCH_QUERY)
    yield_state.append_message("\n\nWe are optimizing your message for besser vector search:\n")
    yield

    if not use_websearch_result:
        websearch_result_str = "no web search executed."

    system_context = f"""You are an AI assistant specializing in constructing highly effective Azure AI Search Index vector queries.  

### **Task:**  
Your goal is to generate an optimized vector search query based on the user's message.  
You may also receive web search results, which can provide additional context.  

### **Input Sources:**  
1. **[USER MESSAGE]** – The user's original query, which you should use to construct the best possible vector search query.  
2. **[WEBSEARCH RESULTS]** – Information gathered from web searches, which may contain relevant details.  
   - If no web search was executed, you will receive: *"no web search executed."*  
   - Use web search results *only* if they add meaningful context.  

### **Instructions:**  
- Output **only** the optimized vector search query — nothing else.  
- Ensure the query is concise, relevant, and effective for embedding-based search retrieval.  
- Do **not** include explanations, formatting, or extra text.  

Here is the provided information:  

### [WEBSEARCH RESULTS]  
{websearch_result_str}  
"""

    resp: StreamResponse
    for resp in aiclient.chat.submit_stream([
        {"role": "system", "content": system_context},
        {"role": "user", "content": user_message},
    ], model=model, current_message=yield_state.message):
        new_message = resp.data["message"]
        if yield_state.message == new_message:
            continue

        yield_state.set_message(new_message)
        yield

    yield resp.data["message"]


def _summarize_html_content(
        yield_state: ChatPOSTYieldStateObject,
        user_message: str,
        html_content: str,
        model: str
) -> Iterator[str]:
    system_context = f"""You are an AI assistant specializing in summarizing poorly structured text based on user queries.

### Task:  
Summarize the following unstructured text in relation to the user message.  
Ensure the summary is **concise, relevant, and correct**.  

### Input Sources:  
- **HTML Text Content:** Extracted raw text (without HTML tags).  
- **User Message:** The query guiding the summary.  

### Instructions:  
- **Output only the summary**—no explanations or extra text.  
- **Do not** include formatting or additional details.  

### HTML Text Content:
{html_content}
"""

    resp: StreamResponse
    for resp in aiclient.chat.submit_stream([
        {"role": "system", "content": system_context},
        {"role": "user", "content": user_message},
    ], model=model, current_message=yield_state.message):
        new_message = resp.data["message"]
        if yield_state.message == new_message:
            continue

        yield_state.set_message(new_message)
        yield

    yield resp.data["message"]
