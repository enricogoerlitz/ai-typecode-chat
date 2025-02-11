from typing import Literal
from abc import ABC, abstractmethod
from flask import Response
from elasticsearch_dsl import (
    Document,
    DenseVector,
    Keyword,
    Text,
    Integer,
    connections,
    Search
)


INDEX_NAME = "emtec-device-type-agent-index"


_ = connections.create_connection(hosts=["http://localhost:9200"])


class IMTDeviceTypeDocument(Document):
    id = Keyword()
    typeCodes = Keyword(multi=True)
    documentName = Text(analyzer="standard")
    documentPageNumber = Integer()
    documentPageContent = Text(analyzer="standard")
    documentPageContentEmbedding = DenseVector(dims=3072)

    class Index:
        name = INDEX_NAME


class IVectorSearchIndex(ABC):
    @abstractmethod
    def search(self, query: dict) -> list[dict]: pass

    @abstractmethod
    def put_documents(self, documents: list) -> dict: pass

    @abstractmethod
    def generate_query(
        embeddings: list[float],
        max_result_count: int) -> dict: pass

    @staticmethod
    def create(
        index_type: Literal[
            "AZURE_AI_SEARCH",
            "ELASTICSEARCH"
        ]
    ) -> 'IVectorSearchIndex':
        match index_type:
            # case "AZURE_AI_SEARCH":
            #     return AzureAISearchIndex(
            #         service_name=gvars.SEARCH_SERVICE_NAME,
            #         index_name=gvars.SEARCH_SERVICE_INDEX_NAME,
            #         api_key=gvars.SEARCH_SERVICE_API_KEY,
            #         api_version=gvars.SEARCH_SERVICE_API_VERSION
            #     )
            case "ELASTICSEARCH":
                return ElasticsearchIndex()

        err = "Index type must be 'AZURE_AI_SEARCH' or 'ELASTICSEARCH'"
        raise Exception(err)


class ElasticsearchIndex(IVectorSearchIndex):
    def __init__(self):
        super().__init__()
        IMTDeviceTypeDocument().init()

    def search(self, query: dict) -> list[dict]:
        s: Search = query["search"]
        return [dict(hit) for hit in s.execute()]

    def put_documents(self, documents: list[IMTDeviceTypeDocument]) -> dict:
        try:
            for doc in documents:
                update_doc = doc.search().filter("term", id=doc.id).execute()
                if len(update_doc) == 0:
                    doc.save()
                    continue

                update_doc: IMTDeviceTypeDocument = update_doc[0]
                update_doc.documentName = doc.documentName
                update_doc.typeCodes = doc.typeCodes
                update_doc.documentPageNumber = doc.documentPageNumber
                update_doc.documentPageContent = doc.documentPageContent
                update_doc.documentPageContentEmbedding = doc.documentPageContentEmbedding  # noqa

                update_doc.save()
        except Exception as e:
            resp = Response({"error": str(e)}, 400)
            print(resp)
            raise Exception("# TODO: errors.VectorSearchRequestException(resp)")  # noqa

    def generate_query(
            self,
            embeddings: list[float],
            max_result_count: int
    ) -> dict:
        # TODO: add filter by typecode
        # wahrscheinlich einfach for .knn filter -> filter().knn(...)
        query = {
            "search": Search(index=INDEX_NAME).knn(
                field="documentPageContentEmbedding",
                k=5,
                num_candidates=max_result_count,
                query_vector=embeddings
            )
        }

        return query


vector_search_index = IVectorSearchIndex.create("ELASTICSEARCH")
