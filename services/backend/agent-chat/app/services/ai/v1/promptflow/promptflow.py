def exec_websearch_v1(
        user_message: str,
        is_deep_search: bool,
        max_result_count: int,
        optimize_query: bool
) -> dict:
    return {}


def exec_vector_aisearch(
        user_message: str,
        use_websearch_result: str,
        websearch_result: dict,
        optimize_vectorsearch_query: bool,
        max_result_count: int
) -> dict:
    if use_websearch_result:
        # if websearch_result != "", muss search query optimiert werden
        optimize_vectorsearch_query = True
    return {}
