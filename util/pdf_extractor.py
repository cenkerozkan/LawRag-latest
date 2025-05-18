from PyPDF2 import PdfReader

from .logger import get_logger

logger = get_logger(__name__)

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
        reader = PdfReader(pdf_path)

        # Initialize an empty string to store all text
        full_text = ""

        # Iterate through all pages and extract text
        for page in reader.pages:
            full_text += page.extract_text() + "\n"

        return full_text.strip()

    except FileNotFoundError:
        return f"Error: The file '{pdf_path}' was not found."
    except Exception as e:
        return f"Error occurred while processing the PDF: {str(e)}"


# Example usage
if __name__ == "__main__":
    # Replace with your PDF path
    pdf_path = "../pdf/turk_ceza_kanun.pdf"
    text = extract_text_from_pdf(pdf_path)
    print(text)