from pydantic import BaseModel

class MessageModel(BaseModel):
    created_at: str
    role: str
    content: str
    web_sources: list[str] | None = None