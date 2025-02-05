# flake8: noqa
import json

from services.ai.chat import chat
from services.ai.embedding import embedding_model
from services.websearch.websearch import serp_client, SERPResponseObject
from database.aisearch import azure_search_index


def exec_websearch_v1(
        user_message: str,
        is_deep_search: bool,
        max_result_count: int,
        optimize_query: bool
) -> dict:
    google_query = user_message
    if optimize_query:
        print("GOOGLE QUERY BEFORE:", google_query)
        google_query = _optimize_websearch_query(user_message)
        print("OPTIMIZED GOOGLE QUERY:", google_query)

    resp = serp_client.search(
        query=google_query,
        max_results=max_result_count
    )

    if resp.status_code != 200:
        print("ERR:", resp.text)
        raise Exception("Error")

    serp_obj = SERPResponseObject(resp)  # TODO: .search() sollte dieses Objekt zurückgeben!

    if is_deep_search:
        links = serp_obj.get_links()
        pass
    
    return {
        "query_result": serp_obj,
        "result_string": str(serp_obj.obj)
    }


def exec_vector_aisearch(
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
        print("QUERY BEFORE:", message)
        message = _optimize_vectorsearch_query(
            user_message=user_message,
            use_websearch_result=use_websearch_result,
            websearch_result_str=websearch_result_str
        )
        print("QUERY AFTER:", message)

    resp = embedding_model.embed(
        embed_content=message,
        max_retries=0
    )

    if resp.status_code != 200:
        print("ERR:", resp.text)
        err = "Error while trying to embedd user message."
        raise Exception(err)

    search_embedding_vector = embedding_model.parse_response_single(resp)

    resp = azure_search_index.search({
        # "search": search_term,  # Text search query
        "vectorQueries": [
            {
                "vector": search_embedding_vector,
                "k": 5,
                "fields": "documentPageContentEmbedding",
                "kind": "vector"
            }
        ],
        # "searchFields": "documentPageContent",  # Keyword search field
        "select": "id, deviceID, deviceTypeID, documentID, documentName, documentPageNumber, documentPageContent, metadata_json",  # noqa
        "top": max_result_count
    })

    if resp.status_code != 200:
        print("ERR:", str(resp.text))
        raise Exception("Err")

    search_results = resp.json()["value"]
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
        user_message: str
) -> str:

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

    resp = chat.submit([
        {"role": "system", "content": system_context},
        {"role": "user", "content": user_message},
    ])

    if resp.status_code != 200:
        print("ERR:", str(resp.text))
        raise Exception("Error...")

    print("RES:", resp.json()["choices"][0])
    return resp.json()["choices"][0]["message"]["content"]


def _optimize_vectorsearch_query(
        user_message: str,
        use_websearch_result: bool,
        websearch_result_str: str,
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

    resp = chat.submit([
        {"role": "system", "content": system_context},
        {"role": "user", "content": user_message},
    ])

    if resp.status_code != 200:
        print("ERR:", str(resp.text))
        raise Exception("Error...")

    print("RES:", resp.json()["choices"][0])
    return resp.json()["choices"][0]["message"]["content"]
