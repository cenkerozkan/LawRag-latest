import os
import asyncio
from dotenv import load_dotenv


load_dotenv()

from util.pdf_selector import PdfSelector
# TEST FOR PDF SELECTOR
#obj = PdfSelector()
#while True:
    #result = asyncio.run(obj.aselect({"input": input("Enter your question: ")}))
    #print(result)


from service.rag_service import RagService

from repository.mongodb_document_repository import MongoDbDocumentRepository
from repository.postgresql_document_repository import PostgreSQLDocumentRepository

obj = MongoDbDocumentRepository(file_path="./pdf/MongoDB_Cheat_Sheet.pdf")
obj_2 = PostgreSQLDocumentRepository(file_path="./pdf/PostgreSQL_Cheat_Sheet.pdf")

#print(obj.retrieve("What is MongoDB?"))
while True:
    print(obj_2.retrieve(input("Enter your question: ")))