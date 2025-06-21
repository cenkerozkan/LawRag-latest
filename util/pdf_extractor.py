from io import BytesIO

from PyPDF2 import PdfReader

from .logger import get_logger

logger = get_logger(__name__)

def extract_text_from_pdf_stream(file_bytes: bytes) -> dict:
    """
    Extracts text from all pages of a PDF using an in-memory byte stream.

    Args:
        file_bytes (bytes): The content of the PDF file in bytes.

    Returns:
        str: Concatenated text from all pages
    """
    result: dict = {
        "success": False,
        "message": "Chat thread pdf upload limit exceeded.",
        "error": "",
        "text": ""
    }
    try:
        pdf_stream: BytesIO = BytesIO(file_bytes)
        reader: PdfReader = PdfReader(pdf_stream)

        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"

        result.update({"success": True, "text": full_text.strip(), "message": "Pdf content extracted successfully."})

    except Exception as e:
        logger.error(f"Error processing PDF from stream: {e}")
        result.update({"message": "An error occured while extracting pdf content!", "error": str(e)})

    return result

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from all pages of a PDF and returns it as a single string.

    Args:
        pdf_path (str): Path to the PDF file

    Returns:
        str: Concatenated text from all pages
    """
    # Create a PDF reader object
    try:
        reader: PdfReader = PdfReader(pdf_path)

        # Initialize an empty string to store all text
        full_text: str = ""

        # Iterate through all pages and extract text
        for page in reader.pages:
            full_text += page.extract_text() + "\n"

        return full_text.strip()

    except FileNotFoundError:
        logger.error(f"File not found: {pdf_path}")
        return f"Error: The file '{pdf_path}' was not found."
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return f"Error occurred while processing the PDF: {str(e)}"