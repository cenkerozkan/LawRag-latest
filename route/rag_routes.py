from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from db.model.chat_thread_model import ChatThreadModel
from request_model.rag_request_model import RagRequestModel
from response_model.response_model import ResponseModel
from util.logger import get_logger
from service.rag_service import rag_service
from service.chat_thread_service import chat_thread_service

logger = get_logger(__name__)
rag_router = APIRouter(prefix="/rag", tags=["RAG Service"])
security = HTTPBearer()

@rag_router.post("/query", tags=["RAG Service"])
async def query_rag(
    rag_request: RagRequestModel,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> JSONResponse:
    logger.info(f"RAG query request for chat: {rag_request.chat_id}")
    chat_thread: ChatThreadModel = await chat_thread_service.retrieve_chat_thread(rag_request.chat_id)
    if not chat_thread.get("success"):
        return JSONResponse(
            status_code=500,
            content=ResponseModel(success=False, message=chat_thread.get("message", ""),
                                  data={}, error="").model_dump())
    if not chat_thread.get("data"):
        return JSONResponse(
            status_code=404,
            content=ResponseModel(success=False, message="Böyle bir sohbet bulunamadı.",
                                  data={}, error="").model_dump())
    result = await rag_service.run(query=rag_request.query, chat_thread=chat_thread.get("data"),
                                   web_search=rag_request.web_search)
    logger.info(f"RAG query result: {result}")
    return JSONResponse(
        status_code=result.get("code"),
        content=ResponseModel(
            success=result.get("success"),
            message=result.get("message"),
            data=result.get("data"),
            error=result.get("error")
        ).model_dump()
    )