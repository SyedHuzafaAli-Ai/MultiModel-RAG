from fastapi import APIRouter
from llm.rag_pipeline import ask_rag

router = APIRouter()

@router.get("/chat")
def chat(query: str, session_id: str = "default"):
    answer, chunks = ask_rag(query, session_id)
    return {"query": query, "answer": answer, "sources": chunks}