from pydantic import BaseModel

class DocumentNotificationRequestModel(BaseModel):
    conversation_id: str
    document_id: str
    file_path: str
    file_name: str
    file_type: str