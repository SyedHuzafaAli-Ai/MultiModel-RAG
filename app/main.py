# from fastapi import FastAPI
# from api.upload import router as upload_router
# from ingestion.loaders.pdf_loader import load_pdf
# from api.search import router as search_router
# from api.chat import router as chat_router

# app=FastAPI()

# @app.get('/')
# def home():
#     return {"message":"Hello Homepage"}

# #upload router
# app.include_router(upload_router)
# #search router
# app.include_router(search_router)
# #chat router
# app.include_router(chat_router)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.logger import get_logger
from api.upload import router as upload_router
from api.search import router as search_router
from api.chat import router as chat_router

logger = get_logger(__name__)

app = FastAPI()


@app.on_event("startup")
def startup_check():
    settings.validate()


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error. Check server logs for details."})


@app.get('/')
def home():
    return {"message": "Hello Homepage"}


app.include_router(upload_router)
app.include_router(search_router)
app.include_router(chat_router)