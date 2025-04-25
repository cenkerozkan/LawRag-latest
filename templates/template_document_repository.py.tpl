import os
from util.logger import get_logger
from base.document_repository_base import DocumentRepositoryBase
from config.config import CHUNK_SIZE
from langchain_community.vectorstores import FAISS
from langchain_cohere.embeddings import CohereEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class {{ClassName}}(DocumentRepositoryBase):
    def __init__(self, file_path: str):
        super().__init__()
        self._logger = get_logger(__name__)
        self._logger.info(f"Initializing {{name}} Document Repository")

        self._logger.info(f"Loading documents from file: {file_path}")
        self._loader = PyPDFLoader(file_path)
        self._documents = (RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=100)
                           .split_documents(self._loader.load()))
        for doc in self._documents:
            doc.metadata["source"] = self.__class__.__name__
        self._db = FAISS.from_documents(
            self._documents,
            CohereEmbeddings(model=self._model)
        )

    async def aretrieve(self, query: str) -> str:
        self._logger.info(f"Retrieving documents for query: {query}")
        docs = await self._db.asimilarity_search(query=query, filter={"source": {"$eq": self.__class__.__name__}})
        return str("{{ClassName}} RAG Context\n" + docs[0].page_content + docs[1].page_content + docs[2].page_content)
