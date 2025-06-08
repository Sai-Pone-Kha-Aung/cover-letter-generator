import os
import logging
import re
import tempfile
import asyncio
from typing import Optional
from src.utils.pdf_utils import extract_text_from_pdf
from src.services import ResumeExtractor, JobExtractor, CoverLetterGenerator
from src.utils.text_utils import remove_thinking_tags

logger = logging.getLogger(__name__)

async def process_cover_letter_request(pdf_file, job_description: str, client) -> Optional[str]:
    """Enhanced core function to process cover letter generation."""
    try:
        # Input validation
        if not job_description or job_description.strip() == "":
            logger.error("Job description is empty")
            return None
        
        if not pdf_file:
            logger.error("PDF file is missing")
            return None
            
        logger.info(f"Processing job description with {len(job_description)} characters")
        
        # Step 1: Save uploaded PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            # Reset file pointer if needed
            pdf_file.seek(0)
            temp_pdf.write(pdf_file.read())
            temp_pdf_path = temp_pdf.name
        
        # Step 2: Extract text from the PDF resume
        pdf_text = extract_text_from_pdf(temp_pdf_path)
        if not pdf_text:
            return "Error: Could not extract sufficient text from PDF. Please ensure the PDF is readable."
        
        # Step 3: Process the resume and job description concurrently
        logger.info("Starting parallel extraction of resume and job information")
        resume_info, job_info = await asyncio.gather(
            ResumeExtractor.extract_resume_info(client, pdf_text),
            JobExtractor.extract_job_description_info(client, job_description.strip()),
            return_exceptions=True
        )
        
        # Handle extraction results
        if isinstance(resume_info, Exception):
            logger.error(f"Resume extraction failed: {resume_info}")
            resume_info = None
            
        if isinstance(job_info, Exception):
            logger.error(f"Job extraction failed: {job_info}")
            job_info = None
        
        if not resume_info or not job_info:
            logger.error("Failed to extract information from resume or job description")
            return "Error: Could not extract sufficient information from the provided documents."
        
        # Step 4: Generate the cover letter
        logger.info("Generating cover letter")
        cover_letter = await CoverLetterGenerator.generate_cover_letter(client, resume_info, job_info)
        clean_cover_letter = re.sub(r'<think>.*?</think>', '', cover_letter, flags=re.DOTALL)

        if not clean_cover_letter:
            logger.error("Cover letter generation failed")
            return "Error: Could not generate cover letter. Please try again."
            
        logger.info("Cover letter generated successfully")
        return clean_cover_letter

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return f"An unexpected error occurred: {str(e)}"
    finally:
        # Cleanup temporary file
        if "temp_pdf_path" in locals():
            try:
                os.unlink(temp_pdf_path)
                logger.debug("Temporary PDF file cleaned up")
            except Exception as e:
                logger.warning(f"Could not delete temporary file: {e}")