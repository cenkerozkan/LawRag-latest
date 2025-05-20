import os
from pathlib import Path

from util.logger import get_logger
from util.pdf_extractor import extract_text_from_pdf
from util.supabase_chat_pdf_downloader import supabase_chat_pdf_downloader
from repository.context_repository import ContextRepository
from db.model.pdf_content_model import PdfContentModel

class InternalService:
    def __init__(self):
        self._supabase = supabase_chat_pdf_downloader
        self._context_repository = ContextRepository()
        self._logger = get_logger(__name__)

    async def handle_pdf_process(
            self,
            chat_id: str,
            file_path: str,
            file_name: str,
    ) -> str | bool:
        """
        Process the PDF file by downloading it from Supabase, extracting text,
        updating the chat thread with the extracted content in pdf_content array.

        Args:
            chat_id (str): The ID of the chat thread.
            file_path (str): The path to the PDF file in Supabase (with unique name).
            file_name (str): The original file name of the PDF (for info/log).
        """
        # 1. Download PDF
        is_file_downloaded: bool = await self._supabase.download_pdf(file_path)
        if not is_file_downloaded:
            self._logger.error(f"Failed to download PDF file: {file_name}")
            return False

        # 2. Extract text from the downloaded PDF file
        local_path = f"./temp/{Path(file_path).name}"
        extracted_text_from_pdf: str = extract_text_from_pdf(local_path)

        # 3. Get the chat thread from context_repository
        chat_thread = await self._context_repository.get_one_by_id(chat_id)
        if chat_thread is None:
            self._logger.error(f"Chat thread with id {chat_id} not found.")
            return False

        # 4. Prepare and add new PdfContentModel to pdf_content array (append, not overwrite)
        #    If pdf_content is None or missing, make it an empty list first
        if not hasattr(chat_thread, "pdf_content") or chat_thread.pdf_content is None:
            chat_thread.pdf_content = []
        # Append new pdf content
        pdf_content_model: PdfContentModel = PdfContentModel(
            file_name=file_name,
            file_content=extracted_text_from_pdf
        )
        chat_thread.pdf_content.append(pdf_content_model)

        # 5. Update the chat thread in context_repository
        update_success: bool = await self._context_repository.update_one(chat_thread)
        if not update_success:
            self._logger.error(f"Failed to update chat thread with id {chat_id} after adding PDF content.")
            try:
                os.remove(local_path)
            except Exception as e:
                self._logger.error(f"Error deleting temp file {local_path}: {e}")
            return False

        try:
            # 6. Delete the local PDF file after processing
            os.remove(local_path)
        except Exception as e:
            self._logger.error(f"Error deleting temp file {local_path}: {e}")

        return extracted_text_from_pdf

internal_service = InternalService()