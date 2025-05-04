import os
import uuid
from util.logger import get_logger
from base.document_repository_base import DocumentRepositoryBase
from config.config import CHUNK_SIZE
from langchain_community.vectorstores import FAISS
from langchain_cohere.embeddings import CohereEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


# worker_laws_document_repository.py
class WorkerLawsDocumentRepository(DocumentRepositoryBase):
    def __init__(self, file_path: str):
        super().__init__()
        self._ids: list = []
        self._logger = get_logger(__name__)
        self._logger.info(f"Initializing is_isci_kanunlari Document Repository")

        self._logger.info(f"Loading documents from file: {file_path}")
        self._loader = PyPDFLoader(file_path)
        self._documents = (RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=100)
                           .split_documents(self._loader.load()))
        for doc in self._documents:
            doc.metadata["source"] = self.__class__.__name__

    def delete_documents(self) -> bool:
        try:
            DocumentRepositoryBase._db.delete(ids=[self._ids[-1]])
            self._ids = []
        except Exception as e:
            DocumentRepositoryBase._logger.error(f"Error during deletion {e}")
            return False
        return True

    def init_documents(self) -> bool:
        self._ids: list[str] = [str(uuid.uuid4()) for _ in range(len(self._documents))]
        try:
            self._logger.info(f"Initializing {self.__class__.__name__} documents")
            DocumentRepositoryBase._db.add_documents(documents=self._documents, ids=self._ids)
        except Exception as e:
            DocumentRepositoryBase._logger.error(f"Error during initialization {e}")
            return False
        return True

    async def aretrieve(self, query: str) -> str:
        self._logger.info(f"Retrieving documents for query: {query}")
        docs = await self._db.asimilarity_search(query=query, filter={"source": {"$eq": self.__class__.__name__}})

        # Take up to first 4 documents and combine their content
        contents = [doc.page_content for doc in docs[:4]]
        combined_content = "\n".join(contents)

        return f"{self.__class__.__name__} RAG Context\n{combined_content}"