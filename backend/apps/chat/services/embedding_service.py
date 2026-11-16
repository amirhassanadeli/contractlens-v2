from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

from django.conf import settings


class EmbeddingService:
    _vector_store = None

    @staticmethod
    def _get_embeddings() -> OllamaEmbeddings:
        return OllamaEmbeddings(
            model=settings.EMBEDDING_MODEL,
            base_url=settings.LLM_BASE_URL,
        )

    @classmethod
    def get_vector_store(cls) -> Chroma:
        """
        Create (once) and return the Chroma vector database.
        """
        if cls._vector_store is None:
            cls._vector_store = Chroma(
                persist_directory=str(settings.CHROMA_DIR),
                embedding_function=cls._get_embeddings(),
            )
        return cls._vector_store

    @classmethod
    def add_documents(
            cls,
            contract_id: str,
            chunks: list[Document],
    ) -> None:
        """
        Add & save chunks to Chroma.
        """
        for index, chunk in enumerate(chunks):
            chunk.metadata.update(
                {
                    "contract_id": contract_id,
                    "chunk_id": index,
                }
            )

        vector_store = cls.get_vector_store()
        vector_store.add_documents(chunks)

    @classmethod
    def get_retriever(cls, contract_id: str):
        """
        Return a Hybrid Retriever (Dense + BM25)
        """
        vector_store = cls.get_vector_store()

        # 1. Dense Retriever (Vector Search + MMR)
        dense_retriever = vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": settings.TOP_K,
                "fetch_k": settings.FETCH_K,
                "filter": {"contract_id": contract_id},
            },
        )

        # 2. Get all chunks of this contract for BM25
        results = vector_store.get(
            where={"contract_id": contract_id},
            include=["documents", "metadatas"],
        )

        documents = []
        if results and results.get("documents"):
            for doc_text, metadata in zip(
                    results["documents"],
                    results["metadatas"]
            ):
                documents.append(
                    Document(
                        page_content=doc_text,
                        metadata=metadata or {}
                    )
                )

        if not documents:
            return dense_retriever

        # 3. BM25 Retriever
        bm25_retriever = BM25Retriever.from_documents(
            documents=documents,
            k=settings.TOP_K,
        )

        # 4. Ensemble (Hybrid)
        hybrid_retriever = EnsembleRetriever(
            retrievers=[dense_retriever, bm25_retriever],
            weights=[0.6, 0.4],
        )

        return hybrid_retriever
