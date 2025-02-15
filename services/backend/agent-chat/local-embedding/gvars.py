import os

SEARCH_SERVICE_NAME = os.getenv("SEARCH_SERVICE_NAME", None)
SEARCH_SERVICE_INDEX_NAME = os.getenv("SEARCH_SERVICE_INDEX_NAME", None)
SEARCH_SERVICE_API_KEY = os.getenv("SEARCH_SERVICE_API_KEY", None)
SEARCH_SERVICE_API_VERSION = os.getenv("SEARCH_SERVICE_API_VERSION", None)

assert SEARCH_SERVICE_NAME is not None
assert SEARCH_SERVICE_INDEX_NAME is not None
assert SEARCH_SERVICE_API_KEY is not None
assert SEARCH_SERVICE_API_VERSION is not None
