from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from request_model.document_notification_request_model import DocumentNotificationRequestModel
from response_model.response_model import ResponseModel
from util.logger import get_logger
from service.internal_service import internal_service

logger = get_logger(__name__)
internal_router = APIRouter(prefix="/api/internal", tags=["Internal Service"])
security = HTTPBearer()

@internal_router.post("/process_pdf", tags=["Internal Service"])
async def process_pdf(
    document: DocumentNotificationRequestModel,
    jwt: HTTPAuthorizationCredentials = Depends(security)
) -> JSONResponse:
    logger.info(f"Processing PDF for chat_id: {document.conversation_id}, file: {document.file_name}")
    result = await internal_service.handle_pdf_process(
        chat_id=document.conversation_id,
        file_path=document.file_path,
        file_name=document.file_name
    )
    if result is False:
        return JSONResponse(
            status_code=500,
            content=ResponseModel(
                success=False,
                message="PDF işlenirken hata oluştu.",
                data={},
                error=""
            ).model_dump()
        )
    return JSONResponse(
        status_code=200,
        content=ResponseModel(
            success=True,
            message="PDF başarıyla işlendi.",
            data={"extracted_text": result},
            error=""
        ).model_dump()
    )