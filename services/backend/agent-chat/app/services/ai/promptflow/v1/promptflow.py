# flake8: noqa

from typing import Iterator, Callable

from logger import logger
from exc import errors
from services.ai.client import aiclient
from services.websearch.v1.websearch import (
    serp_client, SERPResponseObject,
    fetch_url_content
)
from database.vectorsearch import vector_search_index
from utils.openai import trim_to_token_limit
from utils.chat import (
    ChatMessagePayload,
    StreamResponse,
    ChatPUTYieldStateObject,
    
    INITIALIZE_CONNECTION,
    OPTIMIZE_WEB_SEARCH_QUERY,
    EXECUTE_WEB_SEARCH,
    EXECUTE_DEEP_SEARCH,
    OPTIMIZE_WEB_SEARCH_RESULT,
    OPTIMIZE_VECTOR_SEARCH_QUERY,
    EXECUTE_VECTOR_SEARCH,
    EXECUTE_GENERATE_FINAL_MESSAGE,
    
    USE_DATA_ONLY,
    USE_HYBRID_PRIORITIZE_DATA,
    USE_HYBRID
)
from dto.document.chats import ChatMessageDTO, ChatAssistentResponse
from database.document import chatdb


class AIPromptFlow:
    def __init__(self, chat_id: str, cnf: ChatMessagePayload, message: ChatMessageDTO):
        self._run = False

        self._cnf = cnf
        self._chat_id = chat_id
        self._message = message
        self._chat_history = []
        self._model = cnf.model_name
        self._user_message = cnf.message_content
        self._websearch_result = {"result_string": "no results"}
        self._vectorsearch_result = {"result_string": "no results"}
        self._yield_state = ChatPUTYieldStateObject(
            steps=cnf.get_steps(),
            currentStep=INITIALIZE_CONNECTION,
            statusCode=200,
            message="",
            error=None
        )

    @property
    def cnf(self) -> ChatMessagePayload:
        return self._cnf

    @property
    def state(self) -> ChatPUTYieldStateObject:
        return self._yield_state

    def execute(self, add_system_message: Callable) -> Iterator[bytes]:
        if self._run:
            raise Exception("A flow can be executed only once.")

        system_error = None
        try:
            yield self.state.to_yield()

            # 1. fetch chat history
            if self.cnf.chat_history_count > 0:
                self._chat_history = chatdb.find_messages_until_id_match(
                    chat_id=self._chat_id,
                    message_id=self._message._id,
                    n=self.cnf.chat_history_count
                )

            # 2. execute websearch
            if self.cnf.websearch_enabled:
                for self._websearch_result in self._exec_websearch():
                    yield self.state.to_yield()

            # 3. execute vectorsearch
            if self.cnf.vectorsearch_enabled:
                for self._vectorsearch_result in self._exec_vector_search():
                    yield self.state.to_yield()

            # 4. execute final chat message
            for _ in self._exec_generate_final_response():
                yield self.state.to_yield()

        except ValueError as e:
            self.state.error = str(e)
            self.state.statusCode = 400
            yield self.state.to_yield()

        except errors.AIClientRateLimitError as e:
            logger.warning(e)

            self.state.error = str(e)
            self.state.statusCode = 429

            yield self.state.to_yield()

        except (errors.RequestsException, Exception) as e:
            logger.error(e, exc_info=True)

            self.state.error = "An unexpected error has occored."
            self.state.statusCode = 500

            yield self.state.to_yield()
        finally:
            add_system_message(
                chat_id=self._chat_id,
                message=self._message,
                content=self.state.message,
                response=ChatAssistentResponse(
                    statusCode=self.state.statusCode,
                    error=self.state.error
                ),
                system_error=system_error
            )


    def _exec_websearch(self) -> Iterator[dict]:
        google_query = self._user_message
        if self.cnf.websearch_optimize_web_search_query:
            self.state.next_step(OPTIMIZE_WEB_SEARCH_QUERY)
            self.state.append_message("Optimizing your question for websearch to:\n", 1)
            yield

            for google_query in self._optimize_websearch_query():
                yield

        self.state.next_step(EXECUTE_WEB_SEARCH)
        # self.state.append_message("Searching the web for you...", 1)
        yield

        serp_obj = serp_client.search(
            query=google_query,
            max_results=self.cnf.websearch_max_result_count
        )

        # self.state.append_message(json.dumps(serp_obj.obj, indent=2), 1)
        yield

        if self.cnf.websearch_depp_search_enabled:
            for _ in self._exec_deep_websearch(serp_obj):
                yield

        summary = None
        summarize_websearch_results = (
            self.cnf.websearch_optimize_web_search_results or
            self.cnf.websearch_depp_search_enabled
        )
        if summarize_websearch_results:
            for summary in self._summarize_websearch_results(serp_obj):
                yield self.state.to_yield()
            
            serp_obj.set_websearch_summary(summary)

        yield {
            "query_result": serp_obj,
            "result_string": serp_obj.as_result_string()
        }

    def _exec_deep_websearch(self, serp_obj: SERPResponseObject) -> Iterator:
        self.state.next_step(EXECUTE_DEEP_SEARCH)
        # self.state.append_message("Executing deep search for you:", 1)
        yield

        deep_search_results = []
        for link in serp_obj.get_links():
            self.state.append_message(f"Processing link: {link}", 1)

            html_text = trim_to_token_limit(fetch_url_content(link), 1000, "gpt-4o")

            for summary in self._summarize_html_content(html_content=html_text):
                yield

            deep_search_results.append({
                "requested_link": link,
                "requested_link_content_summary": summary
            })

        serp_obj.set_deep_search_results(deep_search_results)

    def _exec_vector_search(self) -> Iterator[dict]:
        message = self._user_message
        max_result_count = self.cnf.vectorsearch_max_result_count
        optimize_vectorsearch_query = self.cnf.vectorsearch_optimize_vector_search_query

        if self.cnf.vectorsearch_use_websearch_results:
            optimize_vectorsearch_query = True

        if optimize_vectorsearch_query:
            for message in self._optimize_vectorsearch_query():
                yield

        self.state.next_step(EXECUTE_VECTOR_SEARCH)

        embeddings = aiclient.embedding_model.embed(trim_to_token_limit(message))[0]
        search_results = vector_search_index.search(
            query=vector_search_index.generate_query_by_typecode(
                embeddings=embeddings,
                max_result_count=max_result_count,
                type_code=self.cnf.context_device_type_code
            )
        )

        if len(search_results) > max_result_count:
            search_results = search_results[:max_result_count-1]

        search_results_str = "Document search results\n"
        for i, result in enumerate(search_results):
            search_results_str = self._add_vectorsearch_result_string(
                prompt=search_results_str,
                result=result,
                result_number=i
            )

        yield {
            "query_result": search_results,
            "result_string": search_results_str
        }

    def _exec_generate_final_response(self) -> Iterator[ChatPUTYieldStateObject]:
        self.state.next_step(EXECUTE_GENERATE_FINAL_MESSAGE)
        self.state.append_message("# Final result\n\n", 3)

        websearch_result_str = self._websearch_result.get("result_string", "no results")
        vectorsearch_result_str = self._vectorsearch_result.get("result_string", "")

        system_context = self._generate_final_response_system_context(
            mode=self.cnf.chat_response_type,
            websearch_result_str=websearch_result_str,
            vectorsearch_result_str=vectorsearch_result_str
        )

        # 4. Generate final response
        resp: StreamResponse
        for resp in aiclient.chat.submit_stream(self._chat_history + [
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
                    "text": self._user_message
                }]
            },
        ], model=self._model, current_message=self.state.message):
            new_message = resp.data["message"]
            if self.state.message == new_message:
                continue

            self.state.set_message(new_message)
            yield

    def _generate_final_response_system_context(
            self,
            mode: str,
            websearch_result_str,
            vectorsearch_result_str
    ) -> str:
        if mode not in [USE_DATA_ONLY, USE_HYBRID_PRIORITIZE_DATA, USE_HYBRID]:
            raise ValueError("Invalid mode. Choose from 'USE_DATA_ONLY', 'USE_HYBRID_PRIORITIZE_DATA', or 'USE_HYBRID'.")
        
        base_context = """You are an AI assistant specializing in retrieving and synthesizing information from multiple sources to provide accurate and relevant answers.
You will receive structured data from the following sources:

1. **[WEBSEARCH RESULTS]** – Information gathered from web searches, which may include summarized content or deeper details from specific websites.
2. **[DOCUMENT SEARCH RESULTS]** – Information retrieved from relevant documents, selected to provide the most useful insights for the user's query.
"""
        
        if mode == "USE_DATA_ONLY":
            additional_context = """
Use ONLY the provided sources to generate well-structured, concise, and helpful responses. Do NOT rely on prior knowledge. If no relevant information is found, state that explicitly rather than guessing.
"""
        elif mode == "USE_HYBRID_PRIORITIZE_DATA":
            additional_context = """
Prioritize the provided sources when generating responses. If necessary, supplement with your general knowledge, but avoid making assumptions or hallucinating. If the provided information conflicts with general knowledge, favor the provided data.
"""
        elif mode == "USE_HYBRID":
            additional_context = """
Use all available information, including the provided sources and your general knowledge, without prioritization. Ensure coherence and accuracy in responses, and avoid making unsupported claims.
"""
        
        system_context = f"""{base_context}{additional_context}
        
Here is the provided information:

### [WEBSEARCH RESULTS]
{websearch_result_str}

### [DOCUMENT SEARCH RESULTS]
{vectorsearch_result_str}
"""
        
        return system_context

    def _add_vectorsearch_result_string(
            self,
            prompt: str,
            result: dict,
            result_number: int
    ) -> str:
        score = result.get("@search.score", "not given")
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

    def _optimize_websearch_query(self) -> Iterator:
        system_context = """You are an AI assistant specializing in constructing highly effective Google search queries.

### **Task:**
Your goal is to generate an optimized Google search query based on the user's message while considering historical context.  

### **Input Source:**
1. **[CHAT HISTORY]** - The conversation history until now.
2. **[USER MESSAGE]** – The user's original query. Use this as the basis to generate the best possible Google search query.

### **Instructions:**
- Leverage **chat history** when applicable:
  - If the user's message builds upon previous queries or document search results, extract relevant past queries to generate a **context-aware** vector query.
  - If the current message alone is insufficient for vector search, use historical context to enhance the query.
- The query should be **short, precise, and highly relevant** to the user's intent.  
- Focus on structuring the query in a way that maximizes the effectiveness of Google's search algorithm.
- Avoid including explanations, formatting, or any additional text.
- Output **only** the optimized Google search query—nothing else.
"""

        resp: StreamResponse
        for resp in aiclient.chat.submit_stream(self._chat_history + [
            {"role": "system", "content": system_context},
            {"role": "user", "content": self._user_message},
        ], model=self._model, current_message=self.state.message):
            new_message = resp.data["message"]
            if self.state.message == new_message:
                continue

            self.state.set_message(new_message)
            yield

        yield resp.data["message"]

    def _optimize_vectorsearch_query(self) -> Iterator[str]:
        self.state.next_step(OPTIMIZE_VECTOR_SEARCH_QUERY)
        # self.state.append_message("We are optimizing your message for besser vector search:", 1)
        yield

        websearch_result_str = self._websearch_result.get("result_string", "no results")
        if not self.cnf.vectorsearch_use_websearch_results:
            websearch_result_str = "no web search executed."

        system_context = f"""You are an AI assistant specializing in constructing highly effective Azure AI Search Index vector queries.

### **Task:**
Your goal is to generate an optimized vector search query based on the user's message while considering historical context.  
You may also receive web search results, which can provide additional context.

### **Input Sources:**
1. **[CHAT HISTORY]** - The conversation history until now.
2. **[USER MESSAGE]** – The user's latest query, which should be used to construct the best possible vector search query.
3. **[WEBSEARCH RESULTS]** – Information gathered from web searches, which may contain relevant details.
   - If no web search was executed, you will receive: *"no web search executed."*
   - Use web search results *only* if they add meaningful context.

### **Instructions:**
- Construct vector search queries that are concise, relevant, and effective for embedding-based search retrieval.
- Leverage **chat history** when applicable:
  - If the user's message builds upon previous queries or document search results, extract relevant past queries to generate a **context-aware** vector query.
  - If the current message alone is insufficient for vector search, use historical context to enhance the query.
- Output **only** the optimized vector search query—nothing else.
- Do **not** include explanations, formatting, or extra text.

Here is the provided information:

### [WEBSEARCH RESULTS]
{websearch_result_str}
"""

        resp: StreamResponse
        for resp in aiclient.chat.submit_stream(self._chat_history + [
            {"role": "system", "content": system_context},
            {"role": "user", "content": self._user_message},
        ], model=self._model, current_message=self.state.message):
            new_message = resp.data["message"]
            if self.state.message == new_message:
                continue

            self.state.set_message(new_message)
            yield

        yield resp.data["message"]

    def _summarize_websearch_results(self, serp_obj: SERPResponseObject) -> Iterator[str]:
        self.state.next_step(OPTIMIZE_WEB_SEARCH_RESULT)
        # self.state.append_message("Optimizing the web search results\n", 2)
        yield

        websearch_result_str = str(serp_obj.obj)

        # system_context = f"""You are an AI assistant specializing in summarizing poorly structured text (inkl. JSON-Objects as string) based on user queries.

        # ### **Task:**
        # Summarize the following unstructured text in relation to the user message.
        # Ensure the summary is **concise, relevant, and correct**.

        # ### **Input Sources:**
        # 1. **[USER MESSAGE]** – The user's original query, which you should use to construct the best possible summary of the data.
        # 2. **[WEBSEARCH RESULTS]** – Information gathered from web searches, which may contain relevant details.


        # ### **Instructions:**
        # - Ensure the summary is concise and relevant.
        # - Do include formatting (markdown).

        # Here is the provided information:

        # ### [WEBSEARCH RESULTS]
        # {websearch_result_str}
        # """

        system_context = f"""You are an AI assistant specializing in **comprehensive summarization** of poorly structured text (including JSON objects as strings) based on user queries.

### **Task:**
Provide a **detailed, structured, and informative** summary of the unstructured text in relation to the user's query.  
Ensure the summary is **accurate, well-organized, and contextually relevant**.

### **Input Sources:**
1. **[USER MESSAGE]** – The user's original query, which serves as the basis for structuring the summary.  
2. **[WEBSEARCH RESULTS]** – Information retrieved from web searches, which may contain crucial details.

### **Instructions:**
- **Provide a detailed summary** that includes key facts, explanations, and insights.  
- **Use markdown formatting** for readability, including headings, bullet points, and emphasis where necessary.  
- **Maintain logical flow** and structure the response with sections such as:
- **Overview**: Brief introduction to the topic.
- **Key Findings**: Important points from the web search.
- **Context & Explanation**: Background information and additional details.
- **Relevant Data**: Statistics, quotes, or structured data where applicable.
- **Ensure clarity and correctness**, avoiding unnecessary filler while maintaining depth.

Here is the provided information:

### **[WEBSEARCH RESULTS]**  
{websearch_result_str}
"""

        summary_start = len(self.state.message)
        resp: StreamResponse
        for resp in aiclient.chat.submit_stream([
            {"role": "system", "content": system_context},
            {"role": "user", "content": self._user_message},
        ], model=self._model, current_message=self.state.message):
            new_message = resp.data["message"]
            if self.state.message == new_message:
                continue

            self.state.set_message(new_message)
            yield

        summary = resp.data["message"][summary_start:]
        yield summary

    def _summarize_html_content(self, html_content: str) -> Iterator[str]:
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

        summary_start = len(self.state.message)
        resp: StreamResponse
        for resp in aiclient.chat.submit_stream([
            {"role": "system", "content": system_context},
            {"role": "user", "content": self._user_message},
        ], model=self._model, current_message=self.state.message):
            new_message = resp.data["message"]
            if self.state.message == new_message:
                continue

            self.state.set_message(new_message)
            yield

        yield resp.data["message"][summary_start:]
