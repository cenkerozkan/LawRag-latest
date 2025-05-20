import os
from pathlib import Path
from supabase import acreate_client, AsyncClient
from dotenv import load_dotenv
from util.logger import get_logger

import asyncio

load_dotenv()
SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY")

class SupabaseChatPDFDownloader:
    def __init__(self):
        self._logger = get_logger(__name__)
        self._supabase: AsyncClient | None = None
        self._lock = asyncio.Lock()

    async def get_supabase_client(self) -> AsyncClient:
        """
        Lazily initialize Supabase AsyncClient and reuse it for future calls.
        """
        if self._supabase is None:
            async with self._lock:
                if self._supabase is None:
                    if not SUPABASE_URL or not SUPABASE_KEY:
                        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
                    self._supabase = await acreate_client(SUPABASE_URL, SUPABASE_KEY)
        return self._supabase

    async def download_pdf(
            self,
            file_path: str,
            path: str = "./temp",
            bucket_name: str = "documents"
    ) -> bool:
        """
        Download a specific PDF file from Supabase storage and save it to the specified directory
        using the unique file name from storage.
        """
        try:
            # Ensure the Supabase client is initialized and get instance
            supabase: AsyncClient = await self.get_supabase_client()

            # Resolve the download directory
            download_directory = Path(path).resolve()
            if not download_directory.exists():
                download_directory.mkdir(parents=True)
                self._logger.info(f"Created directory: {download_directory}")

            # Only the file name is needed for local storage
            unique_file_name = Path(file_path).name
            local_path = download_directory / unique_file_name

            # Download the file from Supabase using the correct file_path
            file_data = await supabase.storage.from_(bucket_name).download(file_path)

            # Save the file locally with its unique name from storage
            with open(local_path, 'wb') as f:
                f.write(file_data)

            self._logger.info(f"Downloaded: {unique_file_name} from {file_path} to {local_path}")
            return True

        except Exception as e:
            self._logger.error(f"Error downloading PDF {file_path}: {e}")
            return False


supabase_chat_pdf_downloader = SupabaseChatPDFDownloader()