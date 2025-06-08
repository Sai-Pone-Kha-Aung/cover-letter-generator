import logging
import PyPDF2
import tempfile
import os
from typing import Optional, BinaryIO

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """Extract text from PDF file."""
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            pdf_text = ""
            
            max_pages = min(len(pdf_reader.pages), 50)  # Limit to 50 pages
            
            for page_num in range(max_pages):
                try:
                    page = pdf_reader.pages[page_num]
                    pdf_text += page.extract_text() + "\n"
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num}: {e}")
                    
        logger.info(f"Extracted PDF text length: {len(pdf_text)} characters from {max_pages} pages")
        
        if len(pdf_text.strip()) < 50:
            logger.error("PDF text extraction failed or too short")
            return None
            
        return pdf_text.strip()
        
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
        return None

def save_uploaded_pdf(pdf_file: BinaryIO) -> Optional[str]:
    """Save uploaded PDF to temporary file and return path."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            # Reset file pointer if needed
            pdf_file.seek(0)
            temp_pdf.write(pdf_file.read())
            temp_pdf_path = temp_pdf.name
            
        logger.info(f"Saved PDF to temporary file: {temp_pdf_path}")
        return temp_pdf_path
        
    except Exception as e:
        logger.error(f"Error saving PDF file: {e}")
        return None

def cleanup_temp_file(file_path: str) -> bool:
    """Clean up temporary file."""
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
            logger.debug(f"Cleaned up temporary file: {file_path}")
            return True
    except Exception as e:
        logger.warning(f"Could not delete temporary file {file_path}: {e}")
    return False

def validate_pdf_file(pdf_file: BinaryIO) -> bool:
    """Validate if the uploaded file is a valid PDF."""
    try:
        pdf_file.seek(0)
        header = pdf_file.read(4)
        pdf_file.seek(0)  # Reset position
        
        return header == b'%PDF'
    except Exception as e:
        logger.error(f"Error validating PDF file: {e}")
        return False

def get_pdf_info(pdf_path: str) -> dict:
    """Get basic information about the PDF."""
    try:
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return {
                'num_pages': len(pdf_reader.pages),
                'title': pdf_reader.metadata.get('/Title', 'Unknown') if pdf_reader.metadata else 'Unknown',
                'author': pdf_reader.metadata.get('/Author', 'Unknown') if pdf_reader.metadata else 'Unknown',
                'encrypted': pdf_reader.is_encrypted
            }
    except Exception as e:
        logger.error(f"Error getting PDF info: {e}")
        return {
            'num_pages': 0,
            'title': 'Unknown',
            'author': 'Unknown',
            'encrypted': False
        }