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



## 📚 API Documentation

### Authorization

All endpoints require Bearer token authentication:

```http
Authorization: Bearer <token>
```

---

## Global Error Handling

The API implements global exception handling for HTTP errors. All error responses follow the `ResponseModel` format:

| Status Code | Message                |
| ----------- | ---------------------- |
| 404         | Not found              |
| 401         | Unauthorized           |
| 403         | Not authenticated      |
| 500         | Internal server error  |

**Example Error Response:**
```json
{
  "success": false,
  "message": "Not found",
  "data": {},
  "error": ""
}
```

Other HTTP errors will return the original error message in the `message` field.

---

## Endpoints

### Chat Thread Endpoints

#### Create Chat Thread

`POST /chat_service/create`

**Request Body:**
```json
{
  "chat_name": "string",
  "user_id": "string",
  "anonymous_user_id": "string (optional)"
}
```

**Success Response:**
```json
{
  "success": true,
  "message": "Chat thread created successfully",
  "data": {
    "chat": {
      "chat_name": "string",
      "chat_id": "string",
      "user_id": "string",
      "anonymous_user_id": "string",
      "created_at": "datetime",
      "updated_at": "datetime",
      "history": []
    }
  },
  "error": ""
}
```

**Error Responses:**
- 400: Invalid request
```json
{
  "success": false,
  "message": "Invalid request parameters",
  "data": {},
  "error": "BAD_REQUEST"
}
```
- 401: Unauthorized
```json
{
  "success": false,
  "message": "Unauthorized",
  "data": {},
  "error": "UNAUTHORIZED"
}
```
- 500: Internal server error
```json
{
  "success": false,
  "message": "Internal server error",
  "data": {},
  "error": "INTERNAL_ERROR"
}
```

---

#### Delete Chat Thread

`DELETE /chat_service/delete/{chat_id}`

**Success Response:**
```json
{
  "success": true,
  "message": "Chat thread deleted successfully.",
  "data": {},
  "error": ""
}
```

**Error Responses:**
- 404: Not found
```json
{
  "success": false,
  "message": "Chat thread not found.",
  "data": {},
  "error": "NOT_FOUND"
}
```
- 401: Unauthorized
```json
{
  "success": false,
  "message": "Unauthorized",
  "data": {},
  "error": "UNAUTHORIZED"
}
```
- 500: Internal server error
```json
{
  "success": false,
  "message": "Internal server error",
  "data": {},
  "error": "INTERNAL_ERROR"
}
```

---

#### Get All Chat Threads

`GET /chat_service/get_all_chat_threads/{user_id}`

**Success Response:**
```json
{
  "success": true,
  "message": "Chat threads retrieved successfully.",
  "data": {
    "threads": [
      {
        "chat_name": "string",
        "chat_id": "string",
        "user_id": "string",
        "anonymous_user_id": "string",
        "created_at": "datetime",
        "updated_at": "datetime",
        "history": []
      }
    ]
  },
  "error": ""
}
```

**Error Responses:**
- 404: Not found
```json
{
  "success": false,
  "message": "No chat threads found for user.",
  "data": {},
  "error": "NOT_FOUND"
}
```
- 401: Unauthorized
```json
{
  "success": false,
  "message": "Unauthorized",
  "data": {},
  "error": "UNAUTHORIZED"
}
```
- 500: Internal server error
```json
{
  "success": false,
  "message": "Internal server error",
  "data": {},
  "error": "INTERNAL_ERROR"
}
```

---

#### Get Chat History

`GET /chat_service/get_chat_history/{chat_id}`

**Success Response:**
```json
{
  "success": true,
  "message": "Chat history retrieved successfully.",
  "data": {
    "history": [
      // List of messages
    ]
  },
  "error": ""
}
```

**Error Responses:**
- 404: Not found
```json
{
  "success": false,
  "message": "Chat history not found.",
  "data": {},
  "error": "NOT_FOUND"
}
```
- 401: Unauthorized
```json
{
  "success": false,
  "message": "Unauthorized",
  "data": {},
  "error": "UNAUTHORIZED"
}
```
- 500: Internal server error
```json
{
  "success": false,
  "message": "Internal server error",
  "data": {},
  "error": "INTERNAL_ERROR"
}
```

---

#### Delete All Chat Histories

`DELETE /chat_service/delete_all_chat_histories/{user_id}`

**Success Response:**
```json
{
  "success": true,
  "message": "All chat threads deleted successfully.",
  "data": {},
  "error": ""
}
```

**Error Responses:**
- 404: Not found
```json
{
  "success": false,
  "message": "No chat histories found for user.",
  "data": {},
  "error": "NOT_FOUND"
}
```
- 401: Unauthorized
```json
{
  "success": false,
  "message": "Unauthorized",
  "data": {},
  "error": "UNAUTHORIZED"
}
```
- 500: Internal server error
```json
{
  "success": false,
  "message": "Internal server error",
  "data": {},
  "error": "INTERNAL_ERROR"
}
```

---

#### Update Chat Name

`PATCH /chat_service/update_chat_name/{chat_id}/{new_chat_name}`

**Success Response:**
```json
{
  "success": true,
  "message": "Chat thread updated successfully.",
  "data": {
    "chat": {
      "chat_name": "string",
      "chat_id": "string",
      "user_id": "string",
      "anonymous_user_id": "string",
      "created_at": "datetime",
      "updated_at": "datetime",
      "history": []
    }
  },
  "error": ""
}
```

**Error Responses:**
- 404: Not found
```json
{
  "success": false,
  "message": "Chat thread not found.",
  "data": {},
  "error": "NOT_FOUND"
}
```
- 401: Unauthorized
```json
{
  "success": false,
  "message": "Unauthorized",
  "data": {},
  "error": "UNAUTHORIZED"
}
```
- 500: Internal server error
```json
{
  "success": false,
  "message": "Internal server error",
  "data": {},
  "error": "INTERNAL_ERROR"
}
```

---

## Response Format

All endpoints return responses in the following format:

```json
{
  "success": "boolean",
  "message": "string",
  "data": "object" | {},
  "error": "string"
}
```

### RAG Endpoints

#### Query RAG

`POST /rag/query`

**Request Body:**
```json
{
  "chat_id": "string",
  "query": "string",
  "web_search": "boolean"
}
```

**Success Response:**
```json
{
  "success": true,
  "message": "RAG query processed successfully",
  "data": {
    "response": "string"
  },
  "error": ""
}
```

**Error Responses:**
- 404: Chat thread not found
```json
{
  "success": false,
  "message": "Böyle bir sohbet bulunamadı.",
  "data": {},
  "error": "NOT_FOUND"
}
```
- 401: Unauthorized
```json
{
  "success": false,
  "message": "Unauthorized",
  "data": {},
  "error": "UNAUTHORIZED"
}
```
- 500: Internal server error
```json
{
  "success": false,
  "message": "Sistemde yaşanan bir aksaklık sebebiyle şu an size yardımcı olamıyorum.",
  "data": {},
  "error": "INTERNAL_ERROR"
}
```
