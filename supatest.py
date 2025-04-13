import os
from pathlib import Path
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv


class SupabaseService:
    def __init__(self):
        """Initialize Supabase client with credentials from environment variables"""
        load_dotenv()
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")

        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.download_directory = Path("pdf")
        self.download_directory.mkdir(exist_ok=True)

    async def list_pdfs(self, bucket_name="kanunlar"):
        """
        List all PDF files in the specified Supabase bucket

        Args:
            bucket_name (str): The Supabase storage bucket containing PDFs

        Returns:
            list: Names of PDF files in the bucket
        """
        try:
            response = self.supabase.storage.from_(bucket_name).list()
            pdf_files = [file['name'] for file in response if file['name'].lower().endswith('.pdf')]
            print(f"Found {len(pdf_files)} PDFs in bucket '{bucket_name}':")
            for pdf in pdf_files:
                print(f"- {pdf}")
            return pdf_files
        except Exception as e:
            print(f"Error listing PDFs in bucket '{bucket_name}': {e}")
            return []

    async def download_pdfs(self, bucket_name="kanunlar"):
        """
        Download all PDF files from specified Supabase bucket to local directory

        Args:
            bucket_name (str): The Supabase storage bucket containing PDFs

        Returns:
            list: Paths to downloaded PDF files
        """
        try:
            # List all PDFs in the bucket
            pdf_files = await self.list_pdfs(bucket_name)
            downloaded_paths = []

            print(f"\nDownloading {len(pdf_files)} PDFs from bucket '{bucket_name}'...")
            for pdf_file in pdf_files:
                local_path = self.download_directory / pdf_file

                # Get file data
                file_data = self.supabase.storage.from_(bucket_name).download(pdf_file)

                # Save to local file
                with open(local_path, 'wb') as f:
                    f.write(file_data)

                downloaded_paths.append(str(local_path))
                print(f"Downloaded: {pdf_file} to {local_path}")

            return downloaded_paths

        except Exception as e:
            print(f"Error downloading PDFs: {e}")
            return []

    async def download_pdf_by_name(self, file_name, bucket_name="kanunlar"):
        """
        Download a specific PDF file from Supabase storage

        Args:
            file_name (str): Name of the PDF file to download
            bucket_name (str): The Supabase storage bucket containing PDFs

        Returns:
            str: Path to downloaded file or None if download failed
        """
        try:
            local_path = self.download_directory / file_name

            # Get file data
            file_data = self.supabase.storage.from_(bucket_name).download(file_name)

            # Save to local file
            with open(local_path, 'wb') as f:
                f.write(file_data)

            print(f"Downloaded: {file_name} to {local_path}")
            return str(local_path)

        except Exception as e:
            print(f"Error downloading PDF {file_name}: {e}")
            return None


# Example usage
async def main():
    service = SupabaseService()

    # List all PDFs in the bucket and download them all
    all_pdfs = await service.download_pdfs()
    print(f"\nSuccessfully downloaded {len(all_pdfs)} PDFs to pdf directory")


if __name__ == "__main__":
    asyncio.run(main())