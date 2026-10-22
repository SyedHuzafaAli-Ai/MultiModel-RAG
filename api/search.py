from fastapi import APIRouter
from retrieval.search import search_chunks

router = APIRouter()

@router.get("/search")
def search(query: str):

    chunks = search_chunks(query)

    return {
        "query": query,
        "results": chunks
    }