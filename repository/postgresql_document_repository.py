import os
from util.logger import get_logger
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class ObligationsLawsDocumentRepository:
    def __init__(
            self,
            file_path: str
    ):
        self._logger = get_logger(__name__)
        self._logger.info(f"Initializing PostgreSQL Document Repository")

        # Initialize embedding vector
        self._embedding_vector = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

        # Load and process documents (formerly in BaseDocumentRepository)
        self._logger.info(f"Loading documents from file: {file_path}")
        self._loader = PyPDFLoader(file_path)
        self._documents = (RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                           .split_documents(self._loader.load()))
        self._db = Chroma.from_documents(
            self._documents,
            GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=os.getenv("GEMINI_API_KEY")
            )
        )

    def retrieve(
            self,
            query: str
    ) -> str:
        self._logger.info(f"Retrieving documents for query: {query}")
        docs = self._db.similarity_search_by_vector(self._embedding_vector.embed_query(query))
        return docs[0].page_content