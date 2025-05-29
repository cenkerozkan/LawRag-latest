import asyncio
from repository.borclar_kanun_document_repository import BorclarKanunDocumentRepository
from repository.kvkk_kanun_document_repository import KvkkKanunDocumentRepository

repo = BorclarKanunDocumentRepository(file_path="pdf/borclar_kanun.pdf")
#repo = KvkkKanunDocumentRepository(file_path="pdf/kvkk_kanun.pdf")

test_list = []

#query = "Arkadaşım gizlice fotoğrafımı çekti napabilirim?"
query = "Bir ev sahibinin bir kiracıyı evden çıkarabilmesi için gerekli şartlar neler?"

result = asyncio.run(repo.aretrieve(query=query, conversation_history=test_list))

print("\n", result)