import os
from util.logger import get_logger
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class WorkerLawsDocumentRepository:
    def __init__(
            self,
            file_path: str
    ):
        self._logger = get_logger(__name__)
        self._logger.info(f"Initializing MongoDB Document Repository")

        # Initialize embedding vector
        self._embedding_vector = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

        # Load and process documents (formerly in BaseDocumentRepository)
        self._logger.info(f"Loading documents from file: {file_path}")
        self._loader = PyPDFLoader(file_path)
        self._documents = (RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
                           .split_documents(self._loader.load()))
        self._db = FAISS.from_documents(
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
        # NOTE: In docs there is a list of document chunks sorted by their
        #       relevance to the query. We are returning the most relevant
        return docs[0].page_content + docs[1].page_content