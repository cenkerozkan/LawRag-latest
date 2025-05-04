from pydantic import BaseModel

class RagRequestModel(BaseModel):
    chat_id: str
    user_id: str
    query: str
    web_search: bool = False