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