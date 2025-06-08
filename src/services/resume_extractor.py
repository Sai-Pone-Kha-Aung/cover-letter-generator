import logging
from typing import Optional
from ..models import ResumeExtraction, ExtractionResult
from ..utils import clean_json_response, parse_json_safely, extract_keywords, extract_email, extract_phone
from ..config import SKILL_KEYWORDS, EXPERIENCE_KEYWORDS, EDUCATION_KEYWORDS

logger = logging.getLogger(__name__)

class ResumeExtractor:
    """Service for extracting structured information from resume text."""
    
    @staticmethod
    async def extract_resume_info(client, pdf_text: str) -> Optional[ResumeExtraction]:
        """Enhanced LLM Call: Extract structured information from resume text."""
        if not pdf_text or len(pdf_text.strip()) < 50:
            logger.warning("PDF text is too short for meaningful extraction")
            return ResumeExtractor._fallback_resume_extraction(pdf_text)
        
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
- Include actual contact information if present
- Return only valid JSON, no additional text"""
            
            response_text = client.generate_response(prompt, max_length=1000)
            logger.info(f"Resume extraction response length: {len(response_text)}")
            
            # Enhanced JSON extraction
            if response_text and not response_text.startswith(("Model", "API Error", "Request", "Cannot", "Connection")):
                json_text = clean_json_response(response_text)
                if json_text:
                    parsed_json = parse_json_safely(json_text)
                    if parsed_json:
                        logger.debug(f"Successfully parsed JSON: {parsed_json}")
                        return ResumeExtraction(**parsed_json)
                    
            # Enhanced fallback parsing
            logger.info("Using fallback extraction method")
            return ResumeExtractor._fallback_resume_extraction(pdf_text)
            
        except Exception as e:
            logger.error(f"Error extracting resume info: {e}")
            return ResumeExtractor._fallback_resume_extraction(pdf_text)

    @staticmethod
    def _fallback_resume_extraction(pdf_text: str) -> ResumeExtraction:
        """Fallback method for resume extraction using text parsing."""
        if not pdf_text:
            return ResumeExtractor._default_resume_extraction()
            
        lines = pdf_text.split('\n')
        skills = []
        experience = []
        education = []
        contact = ""
        
        # Extract skills using keyword matching
        skills = extract_keywords(pdf_text, SKILL_KEYWORDS)
        
        # Extract contact information
        email = extract_email(pdf_text)
        phone = extract_phone(pdf_text)
        contact_parts = []
        if email:
            contact_parts.append(email)
        if phone:
            contact_parts.append(phone)
        contact = " | ".join(contact_parts) if contact_parts else ""
        
        # Extract experience and education from lines
        for line in lines[:50]:  # Check first 50 lines
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            if len(line_stripped) < 5:
                continue
                
            # Extract experience
            if any(exp in line_lower for exp in EXPERIENCE_KEYWORDS) and len(line_stripped) > 10:
                # Avoid generic lines
                if not any(generic in line_lower for generic in ['experience', 'work history', 'employment']):
                    experience.append(line_stripped)
                    
            # Extract education
            if any(edu in line_lower for edu in EDUCATION_KEYWORDS):
                education.append(line_stripped)
        
        # Remove duplicates and limit results
        skills = list(set(skills))[:8]
        experience = list(set(experience))[:4]
        education = list(set(education))[:3]
        
        return ResumeExtraction(
            experience=experience if experience else ["Professional software development experience"],
            skills=skills if skills else ["Software development", "Problem solving", "Team collaboration"],
            education=education if education else ["Computer Science or related degree"],
            contact_info=contact if contact else "Contact information from resume"
        )
    
    @staticmethod
    def _default_resume_extraction() -> ResumeExtraction:
        """Default extraction when no meaningful data can be extracted."""
        return ResumeExtraction(
            experience=["Professional software development experience"],
            skills=["Software development", "Problem solving", "Team collaboration", "Technical communication"],
            education=["Computer Science or related degree"],
            contact_info="Contact information from resume"
        )
    
    @staticmethod
    def validate_extraction(extraction: ResumeExtraction) -> ExtractionResult:
        """Validate the quality of resume extraction."""
        if not extraction:
            return ExtractionResult(
                success=False,
                error_message="No extraction data provided",
                extraction_type="resume"
            )
        
        issues = []
        
        # Check if extraction has meaningful content
        if not extraction.experience or all("professional" in exp.lower() for exp in extraction.experience):
            issues.append("Generic experience information")
            
        if not extraction.skills or len(extraction.skills) < 2:
            issues.append("Insufficient skills extracted")
            
        if not extraction.education or all("computer science" in edu.lower() for edu in extraction.education):
            issues.append("Generic education information")
            
        if not extraction.contact_info or "contact information" in extraction.contact_info.lower():
            issues.append("No specific contact information")
        
        success = len(issues) < 3  # Allow some generic info
        
        return ExtractionResult(
            success=success,
            data=extraction.dict() if success else None,
            error_message="; ".join(issues) if issues else None,
            extraction_type="resume"
        )