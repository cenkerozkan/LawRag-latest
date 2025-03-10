from meta.singleton import Singleton
from repository.mongodb_document_repository import MongoDbDocumentRepository
from repository.postgresql_document_repository import PostgreSQLDocumentRepository
from repository.context_repository import ContextRepository
from util.pdf_selector import PdfSelector

class RagService(metaclass=Singleton):
    def __init__(self):
        # Inject repositories
        self._context_repository = ContextRepository()
        self._mongodb_repository = MongoDbDocumentRepository(file_path="./pdf/MongoDB_Cheat_Sheet.pdf")
        self._postgresql_repository = PostgreSQLDocumentRepository(file_path="./pdf/PostgreSQL_Cheat_Sheet.pdf")

    def _select_pdfs(self) -> list[str]:
        pass