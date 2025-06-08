import logging
from typing import Optional
from ..models import JobDescriptionExtraction, ExtractionResult
from ..utils import clean_json_response, parse_json_safely, extract_keywords, truncate_text
from ..config import REQUIREMENT_KEYWORDS

logger = logging.getLogger(__name__)

class JobExtractor:
    """Service for extracting structured information from job descriptions."""
    
    @staticmethod
    async def extract_job_description_info(client, job_content: str) -> Optional[JobDescriptionExtraction]:
        """Enhanced LLM Call: Extract structured information from job description text."""
        if not job_content or len(job_content.strip()) < 50:
            logger.warning("Job content is too short for meaningful extraction")
            return JobExtractor._fallback_job_extraction(job_content)
        
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
- Provide a concise role summary
- Return only valid JSON, no additional text"""
            
            response_text = client.generate_response(prompt, max_length=1000)
            logger.info(f"Job extraction response length: {len(response_text)}")
            
            # Enhanced JSON extraction
            if response_text and not response_text.startswith(("Model", "API Error", "Request", "Cannot", "Connection")):
                json_text = clean_json_response(response_text)
                if json_text:
                    parsed_json = parse_json_safely(json_text)
                    if parsed_json:
                        logger.debug(f"Successfully parsed JSON: {parsed_json}")
                        return JobDescriptionExtraction(**parsed_json)
            
            # Enhanced fallback parsing
            logger.info("Using fallback extraction method")
            return JobExtractor._fallback_job_extraction(job_content)
            
        except Exception as e:
            logger.error(f"Error extracting job info: {e}")
            return JobExtractor._fallback_job_extraction(job_content)

    @staticmethod
    def _fallback_job_extraction(job_content: str) -> JobDescriptionExtraction:
        """Fallback method for job description extraction."""
        if not job_content:
            return JobExtractor._default_job_extraction()
            
        lines = job_content.split('\n')
        job_title = "Software Engineer"
        company_name = "Company"
        requirements = []
        
        # Extract job title and company from early lines
        for line in lines[:20]:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            if len(line_stripped) < 5:
                continue
                
            # Look for job titles
            job_indicators = ['engineer', 'developer', 'manager', 'analyst', 'position', 'role', 'specialist']
            if any(indicator in line_lower for indicator in job_indicators):
                # Avoid lines that are descriptions rather than titles
                exclude_phrases = ['we are', 'looking for', 'seeking', 'hiring', 'join our', 'opportunity']
                if not any(phrase in line_lower for phrase in exclude_phrases):
                    if len(line_stripped) < 100:  # Titles are usually short
                        job_title = line_stripped
                        break
        
        # Look for company name in first few lines
        for line in lines[:10]:
            line_stripped = line.strip()
            if len(line_stripped) > 2 and len(line_stripped) < 50:
                # Skip obvious non-company lines
                skip_indicators = ['job', 'position', 'role', 'we are', 'about', 'description']
                if not any(indicator in line_stripped.lower() for indicator in skip_indicators):
                    # Check if it looks like a company name
                    if line_stripped.replace(' ', '').isalnum() or 'inc' in line_stripped.lower() or 'llc' in line_stripped.lower():
                        company_name = line_stripped
                        break
        
        # Extract requirements
        requirements = extract_keywords(job_content, REQUIREMENT_KEYWORDS)
        
        # If no keyword-based requirements, extract from requirement sections
        if not requirements:
            for i, line in enumerate(lines):
                line_lower = line.strip().lower()
                if any(req_word in line_lower for req_word in REQUIREMENT_KEYWORDS):
                    # Look at next few lines for actual requirements
                    for j in range(i, min(i+5, len(lines))):
                        req_line = lines[j].strip()
                        if len(req_line) > 15 and len(req_line) < 200:
                            requirements.append(req_line)
                            if len(requirements) >= 4:
                                break
                    if len(requirements) >= 4:
                        break
        
        # Generate description
        description = truncate_text(job_content, 400, "...")
        
        return JobDescriptionExtraction(
            job_title=job_title,
            company_name=company_name,
            requirements=requirements[:4] if requirements else [
                "Relevant technical experience", 
                "Strong problem-solving skills", 
                "Team collaboration abilities", 
                "Bachelor's degree preferred"
            ],
            description=description
        )
    
    @staticmethod
    def _default_job_extraction() -> JobDescriptionExtraction:
        """Default extraction when no meaningful data can be extracted."""
        return JobDescriptionExtraction(
            job_title="Software Engineer",
            company_name="Company",
            requirements=[
                "Relevant technical experience",
                "Strong problem-solving skills", 
                "Team collaboration abilities",
                "Bachelor's degree preferred"
            ],
            description="Software engineering position with competitive compensation and benefits."
        )
    
    @staticmethod
    def validate_extraction(extraction: JobDescriptionExtraction) -> ExtractionResult:
        """Validate the quality of job description extraction."""
        if not extraction:
            return ExtractionResult(
                success=False,
                error_message="No extraction data provided",
                extraction_type="job_description"
            )
        
        issues = []
        
        # Check for generic/default values
        if extraction.job_title == "Software Engineer":
            issues.append("Generic job title")
            
        if extraction.company_name == "Company":
            issues.append("Generic company name")
            
        if not extraction.requirements or len(extraction.requirements) < 2:
            issues.append("Insufficient requirements extracted")
            
        if len(extraction.description) < 50:
            issues.append("Description too short")
        
        success = len(issues) < 2  # Allow some generic info
        
        return ExtractionResult(
            success=success,
            data=extraction.dict() if success else None,
            error_message="; ".join(issues) if issues else None,
            extraction_type="job_description"
        )