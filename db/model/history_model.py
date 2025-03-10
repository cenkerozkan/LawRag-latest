from pydantic import BaseModel

class HistoryModel(BaseModel):
    created_at: str
    role: str
    content: str