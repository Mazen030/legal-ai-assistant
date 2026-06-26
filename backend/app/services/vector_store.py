from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import FakeEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from app.core.config import get_settings
from app.core.exceptions import VectorStoreError


class VectorStoreService:
    def __init__(self):
        self._settings = get_settings()
        self._stores: dict[str, FAISS] = {}
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self._settings.chunk_size,
            chunk_overlap=self._settings.chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""],
        )
        self._embeddings = FakeEmbeddings(size=384)

    def build_store(self, session_id: str, text: str) -> int:
        try:
            chunks = self._text_splitter.split_text(text)
            if not chunks:
                raise VectorStoreError("No text chunks were created from the document.")

            documents = [
                Document(page_content=chunk, metadata={"chunk_index": i})
                for i, chunk in enumerate(chunks)
            ]

            store = FAISS.from_documents(documents, self._embeddings)
            self._stores[session_id] = store
            return len(chunks)
        except VectorStoreError:
            raise
        except Exception as e:
            raise VectorStoreError(f"Failed to build vector store: {e}") from e

    def get_relevant_chunks(self, session_id: str, query: str) -> list[Document]:
        store = self._stores.get(session_id)
        if store is None:
            raise VectorStoreError(f"No vector store found for session: {session_id}")
        return store.similarity_search(query, k=self._settings.retrieval_k)

    def remove_store(self, session_id: str) -> None:
        self._stores.pop(session_id, None)

    def has_store(self, session_id: str) -> bool:
        return session_id in self._stores