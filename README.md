# Multimodal RAG Project

**Multimodal RAG (Retrieval-Augmented Generation)** is a professional framework for building a retrieval-based AI system that can handle **text, images, audio, and video**. This repository is structured to support multimodal ingestion, embedding, retrieval, and generation using LLMs, while also supporting agentic features.
---
## 🌟 Features 
- **Multimodal Ingestion**
  - Load PDFs, text, images, audio, and video
  - Text cleaning, OCR, speech-to-text, and frame extraction
  - Captioning for images and video frames

- **Chunking & Metadata**
  - Text and multimodal chunking
  - Metadata tracking for source, modality, and timestamps

- **Embeddings**
  - Text embeddings using models like MiniLM or BGE
  - Image embeddings with CLIP / BLIP
  - Optional audio embeddings
  - Unified multimodal embeddings
  - Vector store support (FAISS, Chroma, Pinecone)

- **Retrieval**
  - Base and multimodal retrieval
  - Hybrid search (BM25 + vector)
  - Cross-encoder reranking
  - Modality routing

- **LLM Integration**
  - GPT or local LLM clients
  - Vision-capable LLMs (GPT-4V / LLaVA)
  - Context building and response generation
  - Prompt templates

- **Agents (Optional)**
  - Tool usage, planner, and memory
  - Can integrate multi-step reasoning pipelines

- **Evaluation**
  - Retrieval metrics (precision@k, recall@k)
  - Multimodal correctness evaluation

- **API & UI**
  - FastAPI endpoints for text and multimodal queries
  - Streamlit UI for uploads and chat

---
