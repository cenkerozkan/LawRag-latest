from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from request_model.chat_thread_request_model import NewChatThreadModel
from response_model.response_model import ResponseModel
from util.logger import get_logger
from service.chat_thread_service import chat_thread_service

logger = get_logger(__name__)
chat_thread_router = APIRouter(prefix="/api/chat_service", tags=["Chat Thread Service"])
security = HTTPBearer()

@chat_thread_router.post("/create", tags=["Chat Thread Service"])
async def create_chat_thread(
        chat_thread: NewChatThreadModel,
        jwt: HTTPAuthorizationCredentials = Depends(security),
) -> JSONResponse:
    logger.info(f"Creating chat thread for: {chat_thread.model_dump()}")
    result: dict = await chat_thread_service.create_chat_thread(chat_thread.chat_name, chat_thread.user_id,
                                                                chat_thread.anonymous_user_id)
    return JSONResponse(
        status_code=result.get("code"),
        content=ResponseModel(
            success=result.get("success"),
            message=result.get("message"),
            data=result.get("data"),
            error=result.get("error")
        ).model_dump()
    )

@chat_thread_router.delete("/delete/{chat_id}", tags=["Chat Thread Service"])
async def delete_chat_thread(
        chat_id: str,
        jwt: HTTPAuthorizationCredentials = Depends(security),
) -> JSONResponse:
        result: dict = await chat_thread_service.delete_chat_thread(chat_id)
        return JSONResponse(
            status_code=result.get("code"),
            content=ResponseModel(
                success=result.get("success"),
                message=result.get("message"),
                data=result.get("data"),
                error=result.get("error")
            ).model_dump()
        )

@chat_thread_router.get("/get_all_chat_threads/{user_id}", tags=["Chat Thread Service"])
async def get_all_chat_threads(
        user_id: str,
        jwt: HTTPAuthorizationCredentials = Depends(security)
) -> JSONResponse:
    logger.info("Listing all chat threads")
    result: dict = await chat_thread_service.get_all_chat_threads(user_id)
    return JSONResponse(
        status_code=result.get("code"),
        content=ResponseModel(
            success=result.get("success"),
            message=result.get("message"),
            data=result.get("data"),
            error=result.get("error")
        ).model_dump()
    )

@chat_thread_router.get("/get_chat_history/{chat_id}", tags=["Chat Thread Service"])
async def get_chat_history(
        chat_id: str,
        jwt: HTTPAuthorizationCredentials = Depends(security)
) -> JSONResponse:
    logger.info(f"Getting chat history for chat ID: {chat_id}")
    result: dict = await chat_thread_service.get_chat_history(chat_id)
    return JSONResponse(
        status_code=result.get("code"),
        content=ResponseModel(
            success=result.get("success"),
            message=result.get("message"),
            data=result.get("data"),
            error=result.get("error")
        ).model_dump()
    )

@chat_thread_router.delete("/delete_all_chat_histories/{user_id}", tags=["Chat Thread Service"])
async def delete_chat_thread(
        user_id: str,
        jwt: HTTPAuthorizationCredentials = Depends(security)
) -> JSONResponse:
    logger.info(f"Deleting chat thread for chat ID: {user_id}")
    result: dict = await chat_thread_service.delete_all_chat_histories(user_id)
    return JSONResponse(
        status_code=result.get("code"),
        content=ResponseModel(
            success=result.get("success"),
            message=result.get("message"),
            data=result.get("data"),
            error=result.get("error")
        ).model_dump()
    )

@chat_thread_router.patch("/update_chat_name/{chat_id}/{new_chat_name}", tags=["Chat Thread Service"])
async def update_chat_name(
        chat_id: str,
        new_chat_name: str,
        jwt: HTTPAuthorizationCredentials = Depends(security)
) -> JSONResponse:
    logger.info(f"Updating chat name for chat ID: {chat_id} to {new_chat_name}")
    result: dict = await chat_thread_service.update_chat_thread_name(chat_id, new_chat_name)
    return JSONResponse(
        status_code=result.get("code"),
        content=ResponseModel(
            success=result.get("success"),
            message=result.get("message"),
            data=result.get("data"),
            error=result.get("error")
        ).model_dump()
    )