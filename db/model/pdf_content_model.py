from pydantic import BaseModel

class PdfContentModel(BaseModel):
    file_name: str
    file_content: str