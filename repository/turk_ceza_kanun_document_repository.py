import os
import uuid
from util.logger import get_logger
from util.embedding_model_getter import get_embedding_model
from base.document_repository_base import DocumentRepositoryBase
from config.config import CHUNK_SIZE
from config.config import DOC_REPO_RESULT_K
from langchain_community.vectorstores import FAISS
from langchain_cohere.embeddings import CohereEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class TurkCezaKanunDocumentRepository(DocumentRepositoryBase):
    def __init__(
            self,
            file_path: str
    ):
        super().__init__()
        self._ids: list = []
        self._logger = get_logger(__name__)
        self._logger.info(f"Initializing turk_ceza_kanun Document Repository")

        self._logger.info(f"Loading documents from file: {file_path}")
        self._loader = PyPDFLoader(file_path)
        self._documents = (RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=100)
                           .split_documents(self._loader.load()))
        for doc in self._documents:
            doc.metadata["source"] = self.__class__.__name__

        self._db = FAISS.from_documents(
            self._documents,
            CohereEmbeddings(model=get_embedding_model("cohere-light"))
        )

    async def aretrieve(
            self,
            query: str
    ) -> str:
        self._logger.info(f"Retrieving documents for query: {query}")
        docs = await self._db.asimilarity_search(query=query, filter={"source": {"$eq": self.__class__.__name__}})
        top_docs_content = "\n".join([doc.page_content for doc in docs[:DOC_REPO_RESULT_K]])
        return str(f"{self.__class__.__name__} RAG Context\n" + top_docs_content)