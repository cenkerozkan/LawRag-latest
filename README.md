# 📌 DB Cheat Sheet RAG

**A Retrieval-Augmented Generation (RAG) project using LangChain with MongoDB for message history** – This project allows users to select relevant PDFs based on their input using semantic similarity and then generate responses accordingly.

## 🚀 Features

- ✅ **Semantic Similarity-Based PDF Selection**
- ✅ **Integration with LangChain for RAG**
- ✅ **Efficient Retrieval and Query Processing**
- ✅ **MongoDB Integration for Message History Storage**

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
- [ ] Add new fields into message history part in MongoDB Model
- [ ] Bring xml based instruction prompts
- [ ] Implement rag service logic
- [ ] Bring streamlit UI ||  FastAPI UI
- [ ] Bring a more flexible solution in rag_service _pdf_selector.
- [ ] Bring streaming if streamlit supports it.
