from pydantic import BaseModel

class ChatHistoryModel(BaseModel):
    chat_id: str
    history: list[dict[str, str]]