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



# HakMateRAG Backend API Documentation

A FastAPI-based backend for the HakMateRAG application, providing services for managing chat threads, processing PDF documents, and performing RAG (Retrieval Augmented Generation) queries.

## Base URL

`https://your-hakmaterag-api-base-url.com`

All endpoints described in this documentation should be prefixed with this base URL.
For example, to access the create chat thread endpoint:

`POST https://your-hakmaterag-api-base-url.com/api/chat_service/create`

## Table of Contents

*   [Global Error Handling](#global-error-handling)
*   [Chat Thread Service API Endpoints](#chat-thread-service-api-endpoints)
    *   [Create Chat Thread](#create-chat-thread)
    *   [Delete Chat Thread](#delete-chat-thread)
    *   [Get All Chat Threads](#get-all-chat-threads)
    *   [Get Chat History](#get-chat-history)
    *   [Delete All Chat Histories](#delete-all-chat-histories)
    *   [Update Chat Name](#update-chat-name)
*   [Internal Service API Endpoints](#internal-service-api-endpoints)
    *   [Process PDF](#process-pdf)
*   [RAG Service API Endpoints](#rag-service-api-endpoints)
    *   [Query RAG](#query-rag)

## Global Error Handling

The API implements global exception handling. All responses, whether success or error, follow the `ResponseModel` format:

```json
{
  "success": true,        // boolean: Indicates if the request was successful
  "message": "Success",   // string: A human-readable message
  "data": {},             // object | null: The response data, if any
  "error": null           // string | null: An error message or code, if any
}
```

Common HTTP Status Codes:
*   `200 OK`: The request was successful.
*   `400 Bad Request`: The request was malformed or contained invalid parameters.
*   `401 Unauthorized`: Authentication is required and has failed or has not yet been provided. The token is invalid or missing.
*   `422 Unprocessable Entity`: The request was well-formed but was unable to be followed due to semantic errors (FastAPI default for validation errors).
*   `500 Internal Server Error`: An unexpected error occurred on the server.

All protected endpoints require an `Authorization` header with a Bearer token:
`Authorization: Bearer <your_jwt_token>`

## Chat Thread Service API Endpoints

Base path: `/api/chat_service`

---

### Create Chat Thread

Creates a new chat thread for a user.

*   **Endpoint:** `POST /api/chat_service/create`
*   **Headers:**
    *   `Authorization: Bearer <your_jwt_token>`
*   **Request Body:**
    ```json
    {
      "chat_name": "string",         // Name of the chat thread
      "user_id": "string",           // UUID of the user
      "anonymous_user_id": "string"  // Optional: UUID of the anonymous user
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
      "success": true,
      "message": "Chat thread created successfully",
      "data": {
        "chat": {
          "chat_name": "My Legal Questions",
          "chat_id": "uuid-generated-for-chat",
          "user_id": "user-uuid-123",
          "anonymous_user_id": "anon-uuid-456",
          "created_at": "2025-05-21T14:30:00Z",
          "updated_at": "2025-05-21T14:30:00Z",
          "pdf_content": [],
          "history": []
        }
      },
      "error": null
    }
    ```
*   **Error Response (500 Internal Server Error):**
    ```json
    {
      "success": false,
      "message": "Chat thread creation failed",
      "data": {},
      "error": "" // Potentially more specific error from service
    }
    ```

---

### Delete Chat Thread

Deletes a specific chat thread by its ID.

*   **Endpoint:** `DELETE /api/chat_service/delete/{chat_id}`
*   **Path Parameter:**
    *   `chat_id` (string, required): The ID of the chat thread to delete.
*   **Headers:**
    *   `Authorization: Bearer <your_jwt_token>`
*   **Success Response (200 OK):**
    ```json
    {
      "success": true,
      "message": "Chat thread deleted successfully",
      "data": {},
      "error": null
    }
    ```
*   **Error Response (500 Internal Server Error):**
    ```json
    {
      "success": false,
      "message": "Chat thread deletion failed",
      "data": {},
      "error": "" // Potentially "Chat with id: {chat_id} not found" if service returns more detail
    }
    ```

---

### Get All Chat Threads

Retrieves all chat threads for a given user ID.

*   **Endpoint:** `GET /api/chat_service/get_all_chat_threads/{user_id}`
*   **Path Parameter:**
    *   `user_id` (string, required): The ID of the user whose chat threads are to be retrieved.
*   **Headers:**
    *   `Authorization: Bearer <your_jwt_token>`
*   **Success Response (200 OK):**
    ```json
    {
      "success": true,
      "message": "Sohbetler başarıyla alındı", // "Chats retrieved successfully"
      "data": {
        "threads": [
          {
            "chat_name": "Legal Chat 1",
            "chat_id": "uuid-chat-1",
            "user_id": "user-uuid-123",
            "anonymous_user_id": null,
            "created_at": "2025-05-20T10:00:00Z",
            "updated_at": "2025-05-20T11:00:00Z"
            // "history" is excluded
          },
          {
            "chat_name": "Another Case",
            "chat_id": "uuid-chat-2",
            "user_id": "user-uuid-123",
            "anonymous_user_id": null,
            "created_at": "2025-05-21T09:00:00Z",
            "updated_at": "2025-05-21T09:30:00Z"
          }
        ]
      },
      "error": null
    }
    ```
*   **Error Response (500 Internal Server Error):**
    ```json
    {
      "success": false,
      "message": "Chat thread retrieval failed",
      "data": {},
      "error": ""
    }
    ```

---

### Get Chat History

Retrieves the message history for a specific chat thread.

*   **Endpoint:** `GET /api/chat_service/get_chat_history/{chat_id}`
*   **Path Parameter:**
    *   `chat_id` (string, required): The ID of the chat thread.
*   **Headers:**
    *   `Authorization: Bearer <your_jwt_token>`
*   **Success Response (200 OK):**
    ```json
    {
      "success": true,
      "message": "Chat history retrieved successfully",
      "data": {
        "history": [
          {
            "created_at": "2025-05-21T14:30:05Z",
            "role": "user",
            "content": "Hello, can you help me with a legal question?",
            "web_sources": null
          },
          {
            "created_at": "2025-05-21T14:30:10Z",
            "role": "ai",
            "content": "Yes, I can. Please state your question.",
            "web_sources": null
          }
        ]
      },
      "error": null
    }
    ```
*   **Error Response (500 Internal Server Error):**
    ```json
    {
      "success": false,
      "message": "Chat history retrieval failed",
      "data": {},
      "error": ""
    }
    ```

---

### Delete All Chat Histories

Deletes all chat threads and their histories for a specific user.

*   **Endpoint:** `DELETE /api/chat_service/delete_all_chat_histories/{user_id}`
*   **Path Parameter:**
    *   `user_id` (string, required): The ID of the user whose chat histories are to be deleted.
*   **Headers:**
    *   `Authorization: Bearer <your_jwt_token>`
*   **Success Response (200 OK):**
    ```json
    {
      "success": true,
      "message": "Chat histories deleted successfully",
      "data": {},
      "error": null
    }
    ```
*   **Error Response (500 Internal Server Error):**
    ```json
    {
      "success": false,
      "message": "Chat history deletion failed",
      "data": {},
      "error": ""
    }
    ```

---

### Update Chat Name

Updates the name of a specific chat thread.

*   **Endpoint:** `PATCH /api/chat_service/update_chat_name/{chat_id}/{new_chat_name}`
*   **Path Parameters:**
    *   `chat_id` (string, required): The ID of the chat thread to update.
    *   `new_chat_name` (string, required): The new name for the chat thread.
*   **Headers:**
    *   `Authorization: Bearer <your_jwt_token>`
*   **Success Response (200 OK):**
    ```json
    {
      "success": true,
      "message": "Chat thread updated successfully",
      "data": {
        "chat": {
          "chat_name": "Updated Legal Query",
          "chat_id": "uuid-chat-1",
          "user_id": "user-uuid-123",
          "anonymous_user_id": null,
          "created_at": "2025-05-20T10:00:00Z",
          "updated_at": "2025-05-21T15:00:00Z", // Reflects update time
          "pdf_content": [],
          "history": [ /* ... existing history ... */ ]
        }
      },
      "error": null
    }
    ```
*   **Error Response (500 Internal Server Error):**
    *   If chat thread retrieval fails:
        ```json
        {
          "success": false,
          "message": "Chat thread retrieval failed",
          "data": {},
          "error": ""
        }
        ```
    *   If chat thread update fails:
        ```json
        {
          "success": false,
          "message": "Chat thread update failed",
          "data": {},
          "error": ""
        }
        ```

## Internal Service API Endpoints

Base path: `/api/internal`

---

### Process PDF

Processes a PDF document by downloading it, extracting text, and associating it with a chat thread.

*   **Endpoint:** `POST /api/internal/process_pdf`
*   **Headers:**
    *   `Authorization: Bearer <your_jwt_token>`
*   **Request Body:**
    ```json
    {
      "conversation_id": "string", // The chat_id to associate the PDF with
      "document_id": "string",     // A unique ID for the document
      "file_path": "string",       // Path to the PDF file in storage (e.g., Supabase path)
      "file_name": "string",       // Original name of the PDF file
      "file_type": "string"        // MIME type of the file (e.g., "application/pdf")
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
      "success": true,
      "message": "PDF başarıyla işlendi.", // "PDF processed successfully."
      "data": {
        "extracted_text": "The full extracted text content from the PDF..."
      },
      "error": null
    }
    ```
*   **Error Response (500 Internal Server Error):**
    ```json
    {
      "success": false,
      "message": "PDF işlenirken hata oluştu.", // "Error occurred while processing PDF."
      "data": {},
      "error": ""
    }
    ```
    (This can be due to download failure, text extraction failure, or database update failure.)

## RAG Service API Endpoints

Base path: `/api/rag`

---

### Query RAG

Submits a query to the RAG service for a specific chat thread. The service retrieves relevant document context, optionally performs a web search, and generates a response using an AI model.

*   **Endpoint:** `POST /api/rag/query`
*   **Headers:**
    *   `Authorization: Bearer <your_jwt_token>`
*   **Request Body:**
    ```json
    {
      "chat_id": "string",    // ID of the chat thread
      "user_id": "string",    // ID of the user making the query (Note: currently seems to be used for logging/future use, chat retrieval is by chat_id)
      "query": "string",      // The user's query
      "web_search": false   // Optional boolean (default: false): Whether to perform a web search
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
      "success": true,
      "message": "RAG query processed successfully",
      "data": {
        "response": "The AI-generated answer based on retrieved documents and/or web search."
      },
      "error": null
    }
    ```
*   **Error Responses:**
    *   If `retrieve_chat_thread` fails (500 Internal Server Error):
        ```json
        {
          "success": false,
          "message": "Sohbet getirilirken bir sorun oluştu.", // "An issue occurred while fetching the chat."
          "data": {},
          "error": ""
        }
        ```
    *   If retrieved chat data is not in the expected format (500 Internal Server Error):
        ```json
        {
          "success": false,
          "message": "Bilinmeyen bir hata oluştu!", // "An unknown error occurred!"
          "data": {},
          "error": ""
        }
        ```
    *   If AI model content generation fails (from `rag_service.run`):
        ```json
        {
          "success": false,
          "message": "Sistemde yaşanan bir aksaklık sebebiyle şu an size yardımcı olamıyorum.", // "I cannot assist you right now due to a system issue."
          "data": null, // Or some other structure depending on the error
          "error": "Details of the Gemini API error or other internal error"
        }
        ```
    *   If updating the chat thread after successful generation fails multiple times:
        ```json
        {
          "success": false,
          "message": "Sohbet sırasında bir şeyler ters gitti!.", // "Something went wrong during the chat!"
          "data": {
            "response": "Şu anda size yardımcı olamıyorum." // "I cannot help you right now."
          },
          "error": "" // Potentially more specific error
        }
        ```

---
