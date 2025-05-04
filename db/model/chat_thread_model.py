from pydantic import BaseModel

from .message_model import MessageModel

class ChatThreadModel(BaseModel):
    chat_name: str
    chat_id: str            # UUID
    user_id: str            # UUID
    anonymous_user_id: str  # UUID
    created_at: str
    updated_at: str
    history: list[MessageModel]