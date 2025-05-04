from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from dotenv import load_dotenv
from util.supabase_pdf_downloader import SupabasePdfDownloader
from util.logger import get_logger
from response_model.response_model import ResponseModel

from route.rag_routes import rag_router
from route.chat_thread_routes import chat_thread_router

load_dotenv()
logger = get_logger(__name__)

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting PDF download from Supabase...")
    supabase_service = SupabasePdfDownloader()
    downloaded_pdfs = await supabase_service.download_pdfs()
    logger.info(f"Downloaded {len(downloaded_pdfs)} PDFs to pdf directory")

    yield
    logger.info("Application shutting down...")


# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    error_response = ResponseModel(
        success=False,
        message=str(exc.detail),
        data={},
        error=""
    ).model_dump()

    status_code_messages = {
        404: "Not found",
        401: "Unauthorized",
        403: "Not authenticated",
        500: "Internal server error",
    }

    if exc.status_code in status_code_messages:
        error_response["message"] = status_code_messages[exc.status_code]

    return JSONResponse(status_code=exc.status_code, content=error_response)

app.include_router(rag_router)
app.include_router(chat_thread_router)


@app.get("/")
async def read_root():
    return FileResponse("./index.html")

@app.get("/api/test/google_search_util/{query}")
async def test_google_search_util(query: str):
    from util.google_search import google_search

    result = await google_search(query)
    return {"result": result}