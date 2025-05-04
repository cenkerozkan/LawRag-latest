from pydantic import BaseModel
from typing import Optional

class NewChatThreadModel(BaseModel):
    chat_name: str
    user_id: str
    anonymous_user_id: str | None = None