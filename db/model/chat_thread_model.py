from pydantic import BaseModel

from .message_model import MessageModel
from .pdf_content_model import PdfContentModel

class ChatThreadModel(BaseModel):
    chat_name: str
    chat_id: str                   # UUID
    user_id: str                   # UUID
    anonymous_user_id: str | None  # UUID
    created_at: str
    updated_at: str
    pdf_content: list[PdfContentModel] = []
    history: list[MessageModel]