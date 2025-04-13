from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from service.rag_service import RagService
from service.chat_thread_service import ChatThreadService
from db.model.chat_thread_model import ChatThreadModel
from dotenv import load_dotenv
from util.supatest import SupabaseService

load_dotenv()
app = FastAPI()

# Move service initialization to after startup event
rag_service: RagService = None
chat_thread_service: ChatThreadService = None

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models for request/response
class ChatCreate(BaseModel):
    chat_name: str


class MessageSend(BaseModel):
    message: str
    chat_id: str


# Run Supabase download on startup before initializing services
@app.on_event("startup")
async def startup_event():
    global rag_service, chat_thread_service

    print("Starting PDF download from Supabase...")
    supabase_service = SupabaseService()
    downloaded_pdfs = await supabase_service.download_pdfs()
    print(f"Downloaded {len(downloaded_pdfs)} PDFs to pdf directory")

    # Initialize services AFTER PDFs are downloaded
    print("Initializing RAG and chat services...")
    rag_service = RagService()
    chat_thread_service = ChatThreadService()
    print("Application startup complete!")


@app.get("/")
async def read_root():
    return FileResponse("./index.html")


@app.post("/api/chats")
async def create_chat(chat: ChatCreate):
    result = await chat_thread_service.create_chat_thread(chat.chat_name)
    if not result:
        raise HTTPException(status_code=400, detail="Failed to create chat")
    return result


@app.get("/api/chats")
async def get_chats():
    result: list[ChatThreadModel] = await chat_thread_service.retrieve_all_chat_threads()
    return result


@app.get("/api/chats/{chat_id}")
async def get_chat(chat_id: str):
    chat = await chat_thread_service.retrieve_chat_thread(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@app.delete("/api/chats/{chat_id}")
async def delete_chat(chat_id: str):
    success = await chat_thread_service.delete_chat_thread(chat_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"success": True}


@app.post("/api/chats/{chat_id}/messages")
async def send_message(chat_id: str, message: MessageSend):
    chat = await chat_thread_service.retrieve_chat_thread(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    response = await rag_service.send_message(message.message, chat)
    return {"response": response}