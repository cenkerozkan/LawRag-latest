from abc import ABC, abstractmethod
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_cohere.embeddings import CohereEmbeddings
from util.embedding_model_getter import get_embedding_model
from util.logger import get_logger

INDEX_TEXT: str = """
Türk Medeni Kanunu uyarınca taraflar arasında kurulan sözleşmenin geçerliliği, 
şekil şartına tabi olup olmadığına göre değerlendirilir. 
Hukuki işlemlerde irade beyanı, dürüstlük kuralı ve iyi niyet ilkeleri esas alınır. 
Borçlar Kanunu kapsamında tazminat sorumluluğu, 
haksız fiil, sebepsiz zenginleşme ve sözleşmeye aykırılık gibi durumları kapsar. 
Ceza hukukunda kusurluluk ilkesi, 
kast ve taksir ayrımı büyük önem arz ederken; idare hukukunda kamu yararı, 
yetki devri ve idari işlemin iptali gibi kavramlar öne çıkar. 
Ayrıca, Anayasa Mahkemesi bireysel başvuru hakkı çerçevesinde temel hak 
ve özgürlüklerin ihlalini denetler. Yargıtay içtihatları, 
iç hukukta bağlayıcı olmasa da uygulamada emsal teşkil eder. 
Tapu sicilinin aleniyeti, ayni hakların üçüncü kişilere karşı ileri sürülebilmesi 
açısından kritik öneme sahiptir.
"""


def get_faiss_instance() -> FAISS:
    """Factory function to get or create FAISS instance"""
    logger = get_logger(__name__)

    try:
        model = get_embedding_model("cohere-light")
        embeddings = CohereEmbeddings(model=model)
        index = faiss.IndexFlatL2(
            len(embeddings.embed_query(INDEX_TEXT))
        )

        db = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        logger.info("FAISS initialized successfully")
        return db
    except Exception as e:
        logger.error(f"Error during FAISS initialization: {e}")
        raise e


class DocumentRepositoryBase(ABC):
    _db: FAISS = None
    _logger = get_logger(__name__)

    def __init__(self):
        if DocumentRepositoryBase._db is None:
            DocumentRepositoryBase._db = get_faiss_instance()
        self._db = DocumentRepositoryBase._db

    @abstractmethod
    def delete_documents(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def init_documents(self) -> bool:
        raise NotImplementedError()

    @abstractmethod
    async def aretrieve(self, query: str) -> str:
        raise NotImplementedError()