import os
from elasticsearch import AsyncElasticsearch
from config import settings
from models.llm_model import LLMModel

LOCAL_MODELS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "local_models"
)


class RAGService:
    def __init__(self):
        self.es = AsyncElasticsearch(hosts=settings.es_host)

    def _get_embeddings(self, llm_model: LLMModel):
        if llm_model.embedding_type == "local":
            from langchain_community.embeddings import HuggingFaceEmbeddings

            model_name = llm_model.embedding_model_name or "BAAI/bge-small-zh-v1.5"
            local_model_path = os.path.join(LOCAL_MODELS_DIR, model_name)
            if os.path.exists(local_model_path):
                return HuggingFaceEmbeddings(
                    model_name=local_model_path,
                    model_kwargs={"device": "cpu"},
                    encode_kwargs={"normalize_embeddings": True},
                )
            else:
                return HuggingFaceEmbeddings(
                    model_name=model_name,
                    cache_folder=LOCAL_MODELS_DIR,
                    model_kwargs={"device": "cpu"},
                    encode_kwargs={"normalize_embeddings": True},
                )
        else:
            from langchain_openai import OpenAIEmbeddings

            model_name = llm_model.embedding_model_name or "text-embedding-3-small"
            return OpenAIEmbeddings(
                model=model_name,
                openai_api_key=llm_model.api_key,
                openai_api_base=llm_model.api_base_url or "https://api.openai.com/v1",
            )

    async def search(
        self, query: str, knowledge_base_id: str, llm_model: LLMModel, top_n: int = 3
    ) -> list[str]:
        embeddings_model = self._get_embeddings(llm_model)
        query_vector = await embeddings_model.aembed_query(query)

        response = await self.es.search(
            index=settings.es_index,
            knn={
                "field": "embedding",
                "query_vector": query_vector,
                "k": top_n,
                "num_candidates": top_n * 5,
                "filter": {"term": {"knowledge_base_id": knowledge_base_id}},
            },
            size=top_n,
        )

        hits = response["hits"]["hits"]
        return [hit["_source"]["content"] for hit in hits]

    async def close(self):
        await self.es.close()
