# 📌 Law-RAG

A Retrieval-Augmented Generation (RAG) project using LangChain with MongoDB for message history – This project focuses on legal documents, allowing users to select relevant legal PDFs based on their input using semantic similarity and then generate responses accordingly.

## 🚀 Features
✅ Semantic Similarity-Based Legal PDF Selection  
✅ Integration with LangChain for RAG  
✅ Efficient Retrieval and Query Processing for Legal Documents  
✅ MongoDB Integration for Message History Storage  


## 🛠️ Tech Stack

- **LLM Framework**: LangChain (for retrieval and generation)
- **Embedding Models**: Google
- **Vector Database**: FAISS, In Memory Vector Store
- **LLM**: Gemini 2.0 Flash, Gemma3 4B
- **Backend**: FastAPI, Python
- **Database**: MongoDB (for message history)
- **Storage**: Local File System

# 📝 To Do
- [x] Implement pdf selector using semantic similarity with user input
- [x] Implement Document repositories for MongoDB and PostgreSQL
- [x] Implement MongoDB connector
- [x] Implement message history storage in MongoDB
- [x] Increase k in semantic pdf simulator for multiple rag.
- [x] Refactor rag_service, remove chat_thread related methods
- [x] Create a new service for managing chat threads.
- [x] Add new fields into message history part in MongoDB Model
- [x] Bring xml based instruction prompts
- [x] Implement rag service logic
- [x] Bring streamlit UI ||  FastAPI UI
- [x] Add metadata filtering for FAISS queries.
- [ ] Implement a supabase watcher as an independent component.
- [ ] Implement a new UI with streamlit.
- [ ] In RAG service, change the parameter of send message from chat model to uuid.
- [ ] Move FAISS to base doc repository class.
- [ ] For each document repository, create a method that inserts related docs with uuids.
- [ ] Implement a generic repository for custom documents uploaded by the user.
  - [ ] Implement a file upload mechanism.
  - [ ] Use InMemoryVectorStore for custom user documents.
- [ ] Bring a scaffolding mechanism for MongoDB repositories.
- [x] Bring a scaffolding Mechanism for document repositories.
- [ ] Implement a caching mechanism with redis for accessing chats
- [ ] Use nltk to count tokens for each user message.
- [ ] Bring more document repositories for different law areas to increase accuracy.
- [ ] Increase the security in the prompt.
- [ ] Create a word map for each law document to change the pdf selector examples
- [ ] Add used_pdfs field in message model
- [ ] Bring a more flexible solution in rag_service _pdf_selector.
- [ ] Try vertex ai gecko multilingual embedding.

## 🚀 How to Run

### Prerequisites
- MongoDB running locally
- Python 3.8+

### Installation & Setup

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/law-rag.git
   cd law-rag

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
   
3. Start FastAPI server
   ```bash
   uvicorn app:app --reload --port 8000 --host 0.0.0.0
   ```

4. Access the API at `http://localhost:8000/` for test UI.



# HakMate RAG – Backend Integration Guide for Mobile Developers

Welcome to **HakMate RAG**!  
This service is the backbone of HakMate's retrieval-augmented generation, chat context, and PDF legal document enrichment. This guide is tailored for mobile developers to understand how to interact with the backend, including the underlying data models, endpoints, and flows.

---

## Table of Contents

- [General Architecture](#general-architecture)
- [Data Models](#data-models)
- [Base URL & Authentication](#base-url--authentication)
- [API Endpoints](#api-endpoints)
  - [Chat Thread Service](#chat-thread-service)
  - [RAG Query Service](#rag-query-service)
  - [Internal PDF Processing Service](#internal-pdf-processing-service)
- [Request & Response Models](#request--response-models)
- [Typical Flows](#typical-flows)
- [Development & Contact Notes](#development--contact-notes)

---

## General Architecture

- **Framework:** FastAPI (async RESTful)
- **Data Store:** MongoDB (for chat threads, messages, PDF content)
- **Main Capabilities:**  
  - Chat thread management (create, update, delete, list, history)
  - AI-powered question answering with legal document retrieval & web search
  - PDF ingestion & processing
- **Connected to:**  
  - Supabase (for PDF storage)
  - Google Gemini (for AI completions)
  - Internal Python modules (for PDF extraction, retrieval, etc.)

---

## Data Models

### ChatThreadModel

```python
class ChatThreadModel(BaseModel):
    chat_name: str
    chat_id: str                   # UUID
    user_id: str                   # UUID
    anonymous_user_id: str | None  # UUID
    created_at: str
    updated_at: str
    pdf_content: list[PdfContentModel] = []
    history: list[MessageModel]
```

### MessageModel

```python
class MessageModel(BaseModel):
    created_at: str
    role: str                      # "user" or "ai"
    content: str
    web_sources: list[str] | None = None
```

### PdfContentModel

```python
class PdfContentModel(BaseModel):
    file_name: str
    file_content: str              # Extracted text from PDF
```

---

## Base URL & Authentication

- **Base URL:**  
  e.g., `http://localhost:8000/api`

- **Authentication:**  
  All endpoints require `Authorization: Bearer <JWT_TOKEN>` in the headers.

---

## API Endpoints

### Chat Thread Service

Prefix: `/api/chat_service`

| Endpoint                | Method | Description                                 | Body / Params                                      |
|-------------------------|--------|---------------------------------------------|-----------------------------------------------------|
| `/create`               | POST   | Create chat thread                          | `chat_name`, `user_id`, (optional) `anonymous_user_id` |
| `/delete/{chat_id}`     | DELETE | Delete chat thread                          | URL param: `chat_id`                                 |
| `/get_all_chat_threads/{user_id}` | GET | List all chat threads for a user           | URL param: `user_id`                                 |
| `/get_chat_history/{chat_id}`     | GET | Get chat history for a thread              | URL param: `chat_id`                                 |
| `/delete_all_chat_histories/{user_id}` | DELETE | Delete all histories for a user        | URL param: `user_id`                                 |
| `/update_chat_name/{chat_id}/{new_chat_name}` | PATCH | Rename a chat thread           | URL params: `chat_id`, `new_chat_name`               |

---

### RAG Query Service

Prefix: `/api/rag`

| Endpoint   | Method | Description                                          | Body                               |
|------------|--------|------------------------------------------------------|-------------------------------------|
| `/query`   | POST   | Make a question/ask to the legal RAG system         | `chat_id`, `user_id`, `query`, optional `web_search: bool` |

- **Request Body Example:**
  ```json
  {
    "chat_id": "abc123",
    "user_id": "xyz456",
    "query": "Boşanma davası için hangi evraklar gerekir?",
    "web_search": false
  }
  ```

- _RAG service uses chat context, retrieves legal docs, and (optionally) augments with web search before generating an answer._

---

### Internal PDF Processing Service

Prefix: `/api/internal`

| Endpoint          | Method | Description                            | Body                                |
|-------------------|--------|----------------------------------------|-------------------------------------|
| `/process_pdf`    | POST   | Trigger PDF download, extract, ingest  | `conversation_id`, `document_id`, `file_path`, `file_name`, `file_type` |

- **Typical Use:**  
  This endpoint is called by the backend (not the mobile app directly) after a PDF is uploaded and ready to be processed.  
  The PDF's text is extracted and appended to the relevant chat thread's `pdf_content` array.

---

## Request & Response Models

### Common Response Format

All responses use the following model:
```json
{
  "success": true,
  "message": "Your info here",
  "data": { ... },
  "error": ""
}
```

### Example: Creating a Chat Thread

**POST** `/api/chat_service/create`
```json
{
  "chat_name": "My First Chat",
  "user_id": "xyz456",
  "anonymous_user_id": null
}
```
_Response:_
```json
{
  "success": true,
  "message": "Chat thread created successfully",
  "data": { "chat": { ...thread data... } },
  "error": ""
}
```

---

### Example: RAG Query

**POST** `/api/rag/query`
```json
{
  "chat_id": "abc123",
  "user_id": "xyz456",
  "query": "Miras paylaşımında izlenecek yol nedir?",
  "web_search": true
}
```
_Response:_
```json
{
  "success": true,
  "message": "RAG query processed successfully",
  "data": {
    "response": "Miras paylaşımı için izlenmesi gereken temel adımlar şunlardır: ..."
  },
  "error": ""
}
```

---

## Typical Flows

### 1. Start a New Chat

- Use `/api/chat_service/create` to open a new thread and get `chat_id`.
- Store `chat_id` and associate with your user/session.

### 2. Ask Legal/AI Questions

- Use `/api/rag/query` with the current `chat_id`, `user_id`, and the user's question in `query`.
- Optionally set `"web_search": true` for up-to-date answers.

### 3. Show or Rename Chat Threads

- List all with `/api/chat_service/get_all_chat_threads/{user_id}`.
- Rename with `/api/chat_service/update_chat_name/{chat_id}/{new_chat_name}`.

### 4. Show Chat History

- Call `/api/chat_service/get_chat_history/{chat_id}`.

### 5. PDF Upload Flow (FYI)

- The backend will notify the RAG service via `/api/internal/process_pdf` when a PDF is uploaded and ready to be processed.
- Extracted PDF text is stored in the `pdf_content` array of the relevant chat thread.

---

## Development & Contact Notes

- **Authorization:** All endpoints require a valid JWT via `Authorization: Bearer <token>`.
- **All routes are under `/api` prefix.**
- **Error Handling:** Standardized response model; check `"success"` and `"message"` for status.
- **Swagger:** (Optional, if enabled) You can try endpoints via Swagger UI if backend exposes it.
- **For feature requests or questions, contact the backend developer.**

---

**Happy coding!**  
_If you need more technical details or endpoint samples, reach out to the backend dev or check the codebase._
