import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from db.model.chat_thread_model import ChatThreadModel
from request_model.rag_request_model import RagRequestModel
from response_model.response_model import ResponseModel
from util.logger import get_logger
from service.rag_service import rag_service
from service.chat_service import chat_service
from service.chat_thread_service import chat_thread_service
from agents.router_agent import router_agent

logger = get_logger(__name__)
rag_router = APIRouter(prefix="/api/rag", tags=["RAG Service"])
security = HTTPBearer()

@rag_router.post("/query", tags=["RAG Service"])
async def query_rag(
    rag_request: RagRequestModel,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> JSONResponse:
    logger.info(f"RAG query request for chat: {rag_request.chat_id}")
    service_result: ChatThreadModel = await chat_thread_service.retrieve_chat_thread(rag_request.chat_id)
    if not service_result.get("success"):
        return JSONResponse(
            status_code=500,
            content=ResponseModel(success=False, message=service_result.get("message", ""),
                                  data={}, error="").model_dump())
    if not isinstance(service_result.get("data"), ChatThreadModel):
        return JSONResponse(
            status_code=500,
            content=ResponseModel(success=False, message="Bilinmeyen bir hata oluştu!",
                                  data={}, error="").model_dump())

    # Call router agent first.
    decision: str = await router_agent.run(service_result.get("data"), rag_request.query)
    result: dict = {}
    match decision:
        case "rag":
            result = await rag_service.run(query=rag_request.query, chat_thread=service_result.get("data"),
                                           web_search=rag_request.web_search)
        case "chat_agent":
            result = await chat_service.run(query=rag_request.query, chat_thread=service_result.get("data"),
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

@rag_router.post("/query_with_streaming", tags=["RAG Service"])
async def query_with_streaming(
    rag_request: RagRequestModel,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> StreamingResponse:
    logger.info(f"Streaming RAG query request for chat: {rag_request.chat_id}")

    service_result: dict = await chat_thread_service.retrieve_chat_thread(rag_request.chat_id)
    if not service_result.get("success"):
        async def error_stream():
            yield f"data: {{\"error\": \"{service_result.get('message', 'Chat thread retrieval failed')}\"}}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    chat_thread = service_result.get("data")
    if not isinstance(chat_thread, ChatThreadModel):
        async def error_stream():
            yield f"data: {{\"error\": \"Chat data is not valid.\"}}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    # Run router agent
    decision: str = await router_agent.run(chat_thread, rag_request.query)

    # Run appropriate service
    result: dict = {}
    if decision == "rag":
        result = await rag_service.run(query=rag_request.query, chat_thread=chat_thread, web_search=rag_request.web_search)
    elif decision == "chat_agent":
        result = await chat_service.run(query=rag_request.query, chat_thread=chat_thread, web_search=rag_request.web_search)

    response_text: str = result.get("data", {}).get("response", "")

    async def generate():
        # Send chat_id first
        yield f"data: {{\"chat_id\": \"{rag_request.chat_id}\"}}\n\n"

        # Send response in chunks of 3 words
        words = response_text.split()
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i + 3])
            yield f"data: {{\"chunk\": \"{chunk}\"}}\n\n"
            await asyncio.sleep(0.1)

        # Send done signal
        yield f"data: {{\"done\": true}}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")