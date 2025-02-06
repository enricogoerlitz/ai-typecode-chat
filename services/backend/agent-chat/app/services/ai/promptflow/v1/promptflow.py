# flake8: noqa

import json
import time
from typing import Iterator

from services.ai.client import aiclient
from services.ai.promptflow.v1 import promptflow
from services.websearch.v1.websearch import (
    serp_client, SERPResponseObject,
    fetch_url_content
)
from database.vectorsearch import vector_search_index
from utils.chat import (
    ChatPOSTMessagePayloadV1,
    StreamResponse,
    ChatPOSTYieldStateObject
)


def execute(cnf: ChatPOSTMessagePayloadV1) -> Iterator[bytes]:
    steps = cnf.get_steps()
    yield_state = ChatPOSTYieldStateObject(
        steps=steps,
        current_step="INITIALIZE_CONNECTION",
        status_code=200,
        message="Initial message :)\n",
        error=None
    )

    try:
        yield yield_state.to_yield()

        user_message = cnf.message_content

        websearch_result = {"result_string": "no results"}
        vectorsearch_result = {"result_string": "no results"}

        # 1. fetch chat history (count in payload)
        chat_history = []

        # 2. execute websearch
        if cnf.websearch_enabled:
            websearch_result = promptflow._exec_websearch(
                yield_state=yield_state,
                user_message=user_message,
                is_deep_search=cnf.websearch_depp_search_enabled,
                max_result_count=cnf.websearch_max_result_count,
                optimize_query=cnf.websearch_optimize_web_search_query
            )

        # 3. execute vectorsearch
        if cnf.vectorsearch_enabled:
            vectorsearch_result = promptflow._exec_vector_search(
                user_message=user_message,
                use_websearch_result=cnf.vectorsearch_use_websearch_results,
                websearch_result_str=websearch_result.get("result_string", "no results"),
                optimize_vectorsearch_query=cnf.vectorsearch_optimize_vector_search_query,
                max_result_count=cnf.vectorsearch_max_result_count
            )

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


    except Exception as e:
        print("ERR", str(e))
        yield_state.error = "Unexpected server error occurred."
        yield_state.status_code = 500

        yield yield_state.to_yield()


def __execute_t(cnf: ChatPOSTMessagePayloadV1) -> Iterator[StreamResponse]:
    steps = [
        {"step": 1, "message": "Sending data to API1"},
        {"step": 2, "message": "Sending data to API2"},
        {"step": 3, "message": "Parsing responses"},
        {"step": 4, "message": "Generating response"},
        {"step": 5, "message": "Completed!"}
    ]

    yield json.dumps(steps[0]) + "\n"
    time.sleep(1)
    yield json.dumps(steps[1]) + "\n"
    time.sleep(1)
    yield json.dumps(steps[4]) + "\n"

    # for step in steps:
    #     yield json.dumps(step) + "\n"
    #     time.sleep(2)


def _exec_websearch(
        yield_state: ChatPOSTYieldStateObject,
        user_message: str,
        is_deep_search: bool,
        max_result_count: int,
        optimize_query: bool
) -> Iterator[dict]:
    google_query = user_message
    if optimize_query:
        yield_state.next_step("OPTIMIZE_WEB_SEARCH_QUERY")
        google_query = _optimize_websearch_query(user_message)

    serp_obj = serp_client.search(
        query=google_query,
        max_results=max_result_count
    )

    if is_deep_search:
        _exec_deep_websearch(
            user_message=user_message,
            serp_obj=serp_obj
        )
    
    return {
        "query_result": serp_obj,
        "result_string": str(serp_obj.obj)
    }


def _exec_vector_search(
        user_message: str,
        use_websearch_result: str,
        websearch_result_str: str,
        optimize_vectorsearch_query: bool,
        max_result_count: int
) -> dict:
    if use_websearch_result:
        optimize_vectorsearch_query = True

    message = user_message

    if optimize_vectorsearch_query:
        message = _optimize_vectorsearch_query(
            user_message=user_message,
            use_websearch_result=use_websearch_result,
            websearch_result_str=websearch_result_str
        )

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

    return {
        "query_result": search_results,
        "result_string": search_results_str
    }


def _exec_deep_websearch(
        serp_obj: SERPResponseObject,
        user_message: str
) -> None:
    deep_search_results = []
    for link in serp_obj.get_links():
        html_text = fetch_url_content(link)
        summary = _summarize_html_content(
            user_message=user_message,
            html_content=html_text
        )

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
    yield_state.next_step("EXECUTE_GENERATE_FINAL_MESSAGE")

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
        

    print("\n\n\n---------------SYSTEM-CONTEXT------------------\n\n")
    print(system_context)
    print("\n\n---------------------------------\n\n")


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


def _optimize_websearch_query(user_message: str, model: str) -> str:

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

    resp = aiclient.chat.submit([
        {"role": "system", "content": system_context},
        {"role": "user", "content": user_message},
    ], model=model)

    if resp.status_code != 200:
        print("ERR:", str(resp.text))
        raise Exception("Error...")

    print("RES:", resp.json()["choices"][0])
    return resp.json()["choices"][0]["message"]["content"]


def _optimize_vectorsearch_query(
        user_message: str,
        use_websearch_result: bool,
        websearch_result_str: str,
        model: str
) -> str:
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

    resp = aiclient.chat.submit([
        {"role": "system", "content": system_context},
        {"role": "user", "content": user_message},
    ], model=model)

    if resp.status_code != 200:
        print("ERR:", str(resp.text))
        raise Exception("Error...")

    print("RES:", resp.json()["choices"][0])
    return resp.json()["choices"][0]["message"]["content"]


def _summarize_html_content(
        user_message: str,
        html_content: str,
        model: str
) -> str:
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

    resp = aiclient.chat.submit([
        {"role": "system", "content": system_context},
        {"role": "user", "content": user_message},
    ], model=model)

    if resp.status_code != 200:
        print("ERR:", str(resp.text))
        raise Exception("Error...")

    print("RES:", resp.json()["choices"][0])
    return resp.json()["choices"][0]["message"]["content"]
