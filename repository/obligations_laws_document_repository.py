import os
from util.logger import get_logger
from langchain_community.vectorstores import FAISS
from langchain_cohere.embeddings import CohereEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ObligationsLawsDocumentRepository:
    def __init__(
            self,
            file_path: str
    ):
        self._logger = get_logger(__name__)
        self._logger.info(f"Initializing PostgreSQL Document Repository")

        # Load and process documents (formerly in BaseDocumentRepository)
        self._logger.info(f"Loading documents from file: {file_path}")
        self._loader = PyPDFLoader(file_path)
        self._documents = (RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
                           .split_documents(self._loader.load()))
        self._db = FAISS.from_documents(
            self._documents,
            CohereEmbeddings(
                model="embed-multilingual-v3.0",
            )
        )

    async def aretrieve(
            self,
            query: str
    ) -> str:
        self._logger.info(f"Retrieving documents for query: {query}")
        docs = await self._db.asimilarity_search(query)
        return docs[0].page_content + docs[1].page_content + docs[2].page_content