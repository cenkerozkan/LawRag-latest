# 📌 Law-RAG Cheat Sheet

A Retrieval-Augmented Generation (RAG) project using LangChain with MongoDB for message history – This project focuses on legal documents, allowing users to select relevant legal PDFs based on their input using semantic similarity and then generate responses accordingly.

## 🚀 Features
✅ Semantic Similarity-Based Legal PDF Selection  
✅ Integration with LangChain for RAG  
✅ Efficient Retrieval and Query Processing for Legal Documents  
✅ MongoDB Integration for Message History Storage  


## 🛠️ Tech Stack

- **LLM Framework**: LangChain (for retrieval and generation)
- **Embedding Models**: Google
- **Vector Database**: ChromaDB
- **LLM**: Google
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
- [ ] Refactor repository for not db but collections.
- [ ] Add used_pdfs field in message model
- [ ] Bring a more flexible solution in rag_service _pdf_selector.
