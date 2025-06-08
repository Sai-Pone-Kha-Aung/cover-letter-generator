import os
import logging
import re
import PyPDF2
import tempfile
import asyncio
from pydantic import BaseModel, Field
from typing import List, Optional
import json
import requests
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from src.models.data_models import ResumeExtraction, JobDescriptionExtraction, CoverLetter
load_dotenv()

"""Logging Configuration"""
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key 
        self.model_name = model_name
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"Initializing GeminiClient with model: {model_name}")
    
    def check_model_availability(self) -> bool:
        """Check if the Gemini API is accessible."""
        try:
            # Test with a simple prompt
            response = self.model.generate_content("Test")
            return True
        except Exception as e:
            logger.error(f"Gemini model availability check failed: {e}")
            return False
    
    def generate_response(self, prompt: str, max_length: int = 1024) -> str:
        try:
            logger.info(f"Sending request to Gemini with model: {self.model_name}")
            logger.debug(f"Prompt length: {len(prompt)} characters")
            
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                max_output_tokens=max_length,
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            generated_text = response.text.strip()
            logger.info(f"Generated response length: {len(generated_text)} characters")
            return generated_text
            
        except Exception as e:
            logger.error(f"Error generating response with Gemini: {e}")
            return f"Gemini API Error: {str(e)}"


class OllamaClient:
    def __init__(self, model_name: str = "deepseek-r1:latest", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{self.base_url}/api/generate"
        self.tags_url = f"{self.base_url}/api/tags"
        logger.info(f"Initializing OllamaClient with model: {model_name}")
        
    def check_model_availability(self) -> bool:
        """Check if the specified model is available."""
        try:
            response = requests.get(self.tags_url, timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                available_models = [model["name"] for model in models]
                logger.info(f"Available models: {available_models}")
                
                # Check for exact match or partial match
                model_available = any(
                    self.model_name in model_name or model_name.startswith(self.model_name.split(':')[0])
                    for model_name in available_models
                )
                
                if not model_available:
                    logger.warning(f"Model '{self.model_name}' not found in available models")
                
                return model_available
            return False
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False
        
    def generate_response(self, prompt: str, max_length: int = 1024) -> str:
        try:
            # Check model availability first
            if not self.check_model_availability():
                error_msg = f"Model '{self.model_name}' not available. Please pull the model first with: ollama pull {self.model_name}"
                logger.error(error_msg)
                return error_msg
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": max_length,
                    "top_p": 0.9,
                    "top_k": 40,
                }
            }
            
            logger.info(f"Sending request to Ollama with model: {self.model_name}")
            logger.debug(f"Prompt length: {len(prompt)} characters")
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=180  # Increased timeout for larger models
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                logger.info(f"Generated response length: {len(generated_text)} characters")
                return generated_text
            else:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return f"API Error: {response.status_code}. Please check if Ollama is running and the model exists."
                
        except requests.exceptions.Timeout:
            error_msg = "Request timeout - model might be too large or system is slow"
            logger.error(error_msg)
            return "Request timed out. Please try again or use a smaller model."
        except requests.exceptions.ConnectionError:
            error_msg = "Cannot connect to Ollama - make sure it's running"
            logger.error(error_msg)
            return "Cannot connect to Ollama. Please ensure Ollama is running with 'ollama serve'."
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to Ollama: {e}")
            return "Connection error. Please check if Ollama is running properly."
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "An unexpected error occurred while generating the response."

# Extract information from resume
# class ResumeExtraction(BaseModel):
#     experience: List[str] = Field(description="List of work experiences")
#     skills: List[str] = Field(description="List of skills")
#     education: List[str] = Field(description="List of education details")
#     contact_info: str = Field(description="Contact information of the candidate")

# Extract information from job description
# class JobDescriptionExtraction(BaseModel):
#     job_title: str = Field(description="Title of the job")
#     company_name: str = Field(description="Name of the company")
#     requirements: List[str] = Field(description="List of job requirements")
#     description: str = Field(description="Detailed job description")

# Generate a cover letter based on the resume and job description
# class CoverLetter(BaseModel):
#     content: str = Field(description="Generated cover letter content")

"""Information Extraction Functions"""

async def extract_resume_info(client, pdf_text: str) -> Optional[ResumeExtraction]:
    """Enhanced LLM Call: Extract structured information from resume text."""
    try:
        # Improved prompt with better instructions
        prompt = f"""You are an expert resume parser. Extract information from this resume and return ONLY valid JSON.

Resume Text:
{pdf_text[:2500]}

Return ONLY this JSON format with no additional text or explanation:
{{
    "experience": ["job title at company name (duration)", "previous role at company (duration)"],
    "skills": ["technical skill 1", "technical skill 2", "technical skill 3", "technical skill 4", "technical skill 5"],
    "education": ["degree from institution (year)", "certification or additional education"],
    "contact_info": "email address and phone number"
}}

Requirements:
- Extract real information from the resume text
- Keep job titles and company names accurate
- Focus on technical skills relevant to software development
- Include actual contact information if present"""
        
        response_text = client.generate_response(prompt, max_length=1000)
        logger.info(f"Resume extraction response length: {len(response_text)}")
        
        # Enhanced JSON extraction
        if response_text and not response_text.startswith(("Model", "API Error", "Request", "Cannot", "Connection")):
            try:
                response_text = response_text.strip()
                
                # Find JSON boundaries
                if '{' in response_text and '}' in response_text:
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    json_text = response_text[json_start:json_end]
                    
                    # Clean up the JSON
                    json_text = json_text.replace('\n', ' ').replace('  ', ' ')
                    
                    logger.debug(f"Extracted JSON: {json_text[:300]}...")
                    parsed_json = json.loads(json_text)
                    return ResumeExtraction(**parsed_json)
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON parsing failed: {e}")
                
        # Enhanced fallback parsing
        return _fallback_resume_extraction(pdf_text)
        
    except Exception as e:
        logger.error(f"Error extracting resume info: {e}")
        return _fallback_resume_extraction(pdf_text)

def _fallback_resume_extraction(pdf_text: str) -> ResumeExtraction:
    """Fallback method for resume extraction using text parsing."""
    lines = pdf_text.split('\n')
    skills = []
    experience = []
    education = []
    contact = ""
    
    # Define keyword patterns
    skill_keywords = ['python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'git', 'html', 'css']
    exp_keywords = ['engineer', 'developer', 'manager', 'analyst', 'intern', 'specialist', 'consultant']
    edu_keywords = ['university', 'college', 'degree', 'bachelor', 'master', 'phd', 'certification']
    
    for line in lines[:30]:  # Check first 30 lines
        line_lower = line.strip().lower()
        
        # Extract contact info
        if '@' in line or 'phone' in line_lower or '+' in line:
            contact = line.strip()
            
        # Extract skills
        if any(skill in line_lower for skill in skill_keywords):
            skills.append(line.strip())
            
        # Extract experience
        if any(exp in line_lower for exp in exp_keywords) and len(line.strip()) > 10:
            experience.append(line.strip())
            
        # Extract education
        if any(edu in line_lower for edu in edu_keywords):
            education.append(line.strip())
    
    return ResumeExtraction(
        experience=experience[:3] if experience else ["Professional software development experience"],
        skills=skills[:5] if skills else ["Software development skills from resume"],
        education=education[:2] if education else ["Computer Science or related degree"],
        contact_info=contact if contact else "Contact information from resume"
    )

async def extract_job_description_info(client, job_content: str) -> Optional[JobDescriptionExtraction]:
    """Enhanced LLM Call: Extract structured information from job description text."""
    try:
        # Improved prompt for better extraction
        prompt = f"""You are an expert job description parser. Extract key information and return ONLY valid JSON.

Job Description:
{job_content[:3000]}

Return ONLY this JSON format with no additional text or explanation:
{{
    "job_title": "exact job title from the posting",
    "company_name": "company name from the posting",
    "requirements": ["requirement 1", "requirement 2", "requirement 3", "requirement 4"],
    "description": "brief 2-3 sentence summary of the role and responsibilities"
}}

Requirements:
- Extract the exact job title as posted
- Find the actual company name
- Focus on technical requirements and qualifications
- Provide a concise role summary"""
        
        response_text = client.generate_response(prompt, max_length=1000)
        logger.info(f"Job extraction response length: {len(response_text)}")
        
        # Enhanced JSON extraction
        if response_text and not response_text.startswith(("Model", "API Error", "Request", "Cannot", "Connection")):
            try:
                response_text = response_text.strip()
                
                if '{' in response_text and '}' in response_text:
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    json_text = response_text[json_start:json_end]
                    json_text = json_text.replace('\n', ' ').replace('  ', ' ')
                    
                    logger.debug(f"Extracted JSON: {json_text[:300]}...")
                    parsed_json = json.loads(json_text)
                    return JobDescriptionExtraction(**parsed_json)
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON parsing failed: {e}")
        
        # Enhanced fallback parsing
        return _fallback_job_extraction(job_content)
        
    except Exception as e:
        logger.error(f"Error extracting job info: {e}")
        return _fallback_job_extraction(job_content)

def _fallback_job_extraction(job_content: str) -> JobDescriptionExtraction:
    """Fallback method for job description extraction."""
    lines = job_content.split('\n')
    job_title = "Software Engineer"
    company_name = "Company"
    requirements = []
    
    # Extract job title and company
    for line in lines[:15]:
        line = line.strip()
        if len(line) > 5 and any(title_word in line.lower() for title_word in ['engineer', 'developer', 'manager', 'analyst', 'position', 'role']):
            if not any(word in line.lower() for word in ['we are', 'looking for', 'seeking']):
                job_title = line
                break
    
    # Extract requirements
    requirement_keywords = ['required', 'must have', 'experience with', 'proficient', 'knowledge of', 'familiar with']
    for line in lines:
        line_stripped = line.strip()
        if any(req_word in line.lower() for req_word in requirement_keywords) and len(line_stripped) > 10:
            requirements.append(line_stripped)
            if len(requirements) >= 4:
                break
    
    return JobDescriptionExtraction(
        job_title=job_title,
        company_name=company_name,
        requirements=requirements if requirements else ["Relevant technical experience", "Strong problem-solving skills", "Team collaboration abilities", "Bachelor's degree preferred"],
        description=job_content[:400] + "..." if len(job_content) > 400 else job_content
    )

async def generate_cover_letter(client, resume_info: ResumeExtraction, job_info: JobDescriptionExtraction) -> Optional[str]:
    """Enhanced LLM Call: Generate a professional cover letter."""
    try:
        # More detailed and structured prompt
        prompt = f"""Write a professional, compelling cover letter for this job application. Use a formal business letter format.

**Job Details:**
- Position: {job_info.job_title}
- Company: {job_info.company_name}
- Key Requirements: {', '.join(job_info.requirements[:3])}

**Candidate Profile:**
- Top Skills: {', '.join(resume_info.skills[:4])}
- Experience: {resume_info.experience[0] if resume_info.experience else 'Professional software development experience'}
- Education: {resume_info.education[0] if resume_info.education else 'Computer Science degree'}

**Instructions:**
Write a professional cover letter with exactly 4 paragraphs:

1. **Opening**: Express interest in the specific position and company
2. **Experience**: Highlight relevant experience and how it aligns with job requirements
3. **Skills & Value**: Emphasize technical skills and what you can contribute
4. **Closing**: Professional closing with call to action

**Requirements:**
- Professional, confident tone
- Specific to the job and company
- 250-350 words total
- No generic phrases
- Start with "Dear Hiring Manager,"

Write the complete cover letter now:"""

        response = client.generate_response(prompt, max_length=2000)
        
        if response and not response.startswith(("Model", "API Error", "Request", "Cannot", "Connection")):
            # Enhanced response cleaning
            cover_letter = response.strip()
            
            # Ensure proper greeting
            if not cover_letter.startswith("Dear"):
                cover_letter = f"Dear Hiring Manager,\n\n{cover_letter}"
            
            # Ensure proper closing
            if not any(closing in cover_letter.lower() for closing in ['sincerely', 'best regards', 'respectfully']):
                cover_letter += f"\n\nSincerely,\n[Your Name]"
            
            # Add date if not present
            if not any(word in cover_letter for word in ['2024', '2025', str(datetime.now().year)]):
                current_date = datetime.now().strftime("%B %d, %Y")
                cover_letter = f"{current_date}\n\n{cover_letter}"
            
            logger.info(f"Generated cover letter length: {len(cover_letter)} characters")
            return cover_letter
            
        logger.error("Failed to generate valid cover letter response")
        return None
        
    except Exception as e:
        logger.error(f"Error generating cover letter: {e}")
        return None

"""Core Process Function"""

async def process_cover_letter_request(pdf_file, job_description: str, ollama_client) -> Optional[str]:
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
        try:
            with open(temp_pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pdf_text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        pdf_text += page.extract_text() + "\n"
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num}: {e}")
                        
            logger.info(f"Extracted PDF text length: {len(pdf_text)} characters")
            
            if len(pdf_text.strip()) < 50:
                logger.error("PDF text extraction failed or too short")
                return "Error: Could not extract sufficient text from PDF. Please ensure the PDF is readable."
                
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            return "Error: Could not read the PDF file. Please try a different file."
        
        # Step 3: Process the resume and job description concurrently
        logger.info("Starting parallel extraction of resume and job information")
        resume_info, job_info = await asyncio.gather(
            extract_resume_info(ollama_client, pdf_text),
            extract_job_description_info(ollama_client, job_description.strip()),
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
        cover_letter = await generate_cover_letter(ollama_client, resume_info, job_info)
        clean_cover_letter =  re.sub(r'<think>.*?</think>', '', cover_letter, flags=re.DOTALL)

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

"""Factory Function"""
def create_ollama_client(model_name: str = "deepseek-r1:latest"):
    """Enhanced factory function to create an OllamaClient instance."""
    return OllamaClient(model_name=model_name)

def create_gemini_client(model_name: str = None, api_key: str = None):
    """Factory function to create a GeminiClient instance."""
    return GeminiClient(model_name=model_name, api_key=api_key)