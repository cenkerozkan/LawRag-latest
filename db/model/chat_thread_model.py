from pydantic import BaseModel

from .history_model import HistoryModel

class ChatThreadModel(BaseModel):
    chat_id: str
    created_at: str
    updated_at: str
    history: list[HistoryModel]