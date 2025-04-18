import os
import asyncio
from dotenv import load_dotenv


load_dotenv()
"""
PDF SELECTOR TEST
"""
from util.pdf_selector import PdfSelector
#obj = PdfSelector()
#while True:
    #result = asyncio.run(obj.aselect({"input": input("Enter your question: ")}))
    #print(result)

"""
RAG REPOSITORY TEST
"""
from service.rag_service import RagService

from repository.worker_laws_document_repository import WorkerLawsDocumentRepository
from repository.obligations_laws_document_repository import ObligationsLawsDocumentRepository

#obj = MongoDbDocumentRepository(file_path="./pdf/MongoDB_Cheat_Sheet.pdf")
#obj_2 = PostgreSQLDocumentRepository(file_path="./pdf/PostgreSQL_Cheat_Sheet.pdf")


#print(obj.retrieve("What is MongoDB?"))
#while True:
    #result = obj.retrieve(input("Enter your question: "))
    #print(type(result))

"""
CONTEXT REPOSITORY TEST
"""
#from repository.context_repository import ContextRepository
#from db.model.chat_thread_model import ChatThreadModel
#from db.model.history_model import HistoryModel
#import datetime
#import uuid
#history_model_user = HistoryModel(
#    created_at=datetime.datetime.now().isoformat(),
#    role="user",
#    content="Hello"
#)
#history_model_ai = HistoryModel(
#    created_at=datetime.datetime.now().isoformat(),
#    role="ai",
#    content="Hi"
#)
#model = ChatThreadModel(
#    chat_id=str(uuid.uuid4()),
#    created_at=datetime.datetime.now().isoformat(),
#    updated_at=datetime.datetime.now().isoformat(),
#    history=[history_model_user, history_model_ai]
#)
#
#model_two = ChatThreadModel(
#    chat_id=str(uuid.uuid4()),
#    created_at=datetime.datetime.now().isoformat(),
#    updated_at=datetime.datetime.now().isoformat(),
#    history=[history_model_user, history_model_ai]
#)
#print(model.model_dump())
#obj = ContextRepository()
#asyncio.run(obj.insert_one(model_two))
#asyncio.run(obj.insert_many([model, model_two]))
#results: list[ChatThreadModel] = asyncio.run(obj.get_all())
#print(results)
#print(asyncio.run(obj.get_one_by_id(results[0].chat_id)))
#print(asyncio.run(obj.delete_one_by_id("5652e52f-193e-40fe-8863-5a074607e418")))
#print(asyncio.run(obj.delete_many_by_id(["a78d3cf2-69c8-49fa-8b29-8529ffe08f12", "95046d60-60e9-4e71-b947-e1d60b2dfdd1"])))


"""
RAG SERVICE TEST
"""
#from service.rag_service import RagService
#import datetime
#import uuid
#from db.model.chat_thread_model import ChatThreadModel
#from repository.context_repository import ContextRepository

#context_repository = ContextRepository()
#new_chat = ChatThreadModel(
#    chat_id=str(uuid.uuid4()),
#    chat_name="Test",
#    created_at=datetime.datetime.now().isoformat(),
#    updated_at=datetime.datetime.now().isoformat(),
#    history=[]
#)
#asyncio.run(context_repository.insert_one(new_chat))

#obj = RagService()
#while True:
#    result = asyncio.run(obj.send_message(query=input("Enter your question: "),
#                              chat_thread=new_chat))
#    print(result)


"""
GOOGLE SEARCH UTILITY TEST
"""
from util.google_search import google_search
results: dict = asyncio.run(google_search("Kovulunca haklarım"))
print(results)