import os
from elasticsearch import AsyncElasticsearch
from config import settings
from models.file import File
from models.llm_model import LLMModel

LOCAL_MODELS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "local_models"
)


class EmbeddingService:
    def __init__(self):
        self.es = AsyncElasticsearch(hosts=settings.es_host)

    def _get_embedding_dims(self, llm_model: LLMModel) -> int:
        if llm_model.embedding_type == "local":
            dims_map = {
                "BAAI/bge-small-zh-v1.5": 512,
                "BAAI/bge-base-zh-v1.5": 768,
                "BAAI/bge-large-zh-v1.5": 1024,
                "BAAI/bge-small-en-v1.5": 384,
                "BAAI/bge-base-en-v1.5": 768,
            }
            return dims_map.get(llm_model.embedding_model_name, 768)
        else:
            dims_map = {
                "text-embedding-3-small": 1536,
                "text-embedding-3-large": 3072,
                "text-embedding-ada-002": 1536,
            }
            return dims_map.get(llm_model.embedding_model_name, 1536)

    def _get_local_embeddings(self, llm_model: LLMModel):
        from langchain_community.embeddings import HuggingFaceEmbeddings

        model_name = llm_model.embedding_model_name or "BAAI/bge-small-zh-v1.5"
        local_model_path = os.path.join(LOCAL_MODELS_DIR, model_name)
        os.makedirs(LOCAL_MODELS_DIR, exist_ok=True)
        if os.path.exists(local_model_path):
            print(f"从本地加载模型: {local_model_path}")
            return HuggingFaceEmbeddings(
                model_name=local_model_path,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        else:
            print(f"首次下载模型 {model_name} 到 {local_model_path}，请稍候...")
            return HuggingFaceEmbeddings(
                model_name=model_name,
                cache_folder=LOCAL_MODELS_DIR,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )

    def _get_api_embeddings(self, llm_model: LLMModel):
        from langchain_openai import OpenAIEmbeddings

        model_name = llm_model.embedding_model_name or "text-embedding-3-small"
        return OpenAIEmbeddings(
            model=model_name,
            openai_api_key=llm_model.api_key,
            openai_api_base=llm_model.api_base_url or "https://api.openai.com/v1",
        )

    def _get_embeddings(self, llm_model: LLMModel):
        if llm_model.embedding_type == "local":
            return self._get_local_embeddings(llm_model)
        else:
            return self._get_api_embeddings(llm_model)

    async def ensure_index(self, dims: int):
        exists = await self.es.indices.exists(index=settings.es_index)
        if not exists:
            await self.es.indices.create(
                index=settings.es_index,
                body={
                    "mappings": {
                        "properties": {
                            "file_id": {"type": "keyword"},
                            "knowledge_base_id": {"type": "keyword"},
                            "content": {"type": "text"},
                            "chunk_index": {"type": "integer"},
                            "embedding": {
                                "type": "dense_vector",
                                "dims": dims,
                                "index": True,
                                "similarity": "cosine",
                            },
                        }
                    }
                },
            )

    def _load_file(self, file: File) -> str:
        if file.file_type == "pdf":
            from langchain_community.document_loaders import PyPDFLoader

            loader = PyPDFLoader(file.file_path)
            pages = loader.load()
            return "\n".join([p.page_content for p in pages])
        elif file.file_type in ("txt", "md"):
            from langchain_community.document_loaders import TextLoader

            loader = TextLoader(file.file_path, encoding="utf-8")
            docs = loader.load()
            return docs[0].page_content
        elif file.file_type == "docx":
            from langchain_community.document_loaders import Docx2txtLoader

            loader = Docx2txtLoader(file.file_path)
            docs = loader.load()
            return docs[0].page_content
        else:
            raise ValueError(f"不支持的文件类型: {file.file_type}")

    def _split_text(self, text: str) -> list[str]:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""],
        )
        return splitter.split_text(text)

    async def parse_and_index(self, file: File, llm_model: LLMModel) -> int:
        dims = self._get_embedding_dims(llm_model)
        await self.ensure_index(dims)

        text = self._load_file(file)
        chunks = self._split_text(text)
        embeddings_model = self._get_embeddings(llm_model)
        vectors = await embeddings_model.aembed_documents(chunks)

        await self.es.delete_by_query(
            index=settings.es_index, body={"query": {"term": {"file_id": file.id}}}
        )

        from elasticsearch.helpers import async_bulk

        actions = [
            {
                "_index": settings.es_index,
                "_source": {
                    "file_id": file.id,
                    "knowledge_base_id": file.knowledge_base_id,
                    "content": chunk,
                    "chunk_index": i,
                    "embedding": vector,
                },
            }
            for i, (chunk, vector) in enumerate(zip(chunks, vectors))
        ]
        await async_bulk(self.es, actions)
        return len(chunks)

    async def delete_file_vectors(self, file_id: str):
        await self.es.delete_by_query(
            index=settings.es_index, body={"query": {"term": {"file_id": file_id}}}
        )

    async def close(self):
        await self.es.close()
