import logging
from typing import Optional
from datetime import datetime
from ..models import ResumeExtraction, JobDescriptionExtraction, CoverLetter
from ..utils import remove_thinking_tags, format_cover_letter, validate_response_quality

logger = logging.getLogger(__name__)

class CoverLetterGenerator:
    """Service for generating professional cover letters."""
    
    @staticmethod
    async def generate_cover_letter(client, resume_info: ResumeExtraction, job_info: JobDescriptionExtraction) -> Optional[str]:
        """Enhanced LLM Call: Generate a professional cover letter."""
        if not resume_info or not job_info:
            logger.error("Missing resume or job information for cover letter generation")
            return None
            
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
- End with professional closing

Write the complete cover letter now:"""

            response = client.generate_response(prompt, max_length=2000)
            
            if response and validate_response_quality(response, min_length=200):
                # Clean the response
                clean_response = remove_thinking_tags(response)
                
                # Format the cover letter properly
                formatted_letter = format_cover_letter(
                    clean_response, 
                    job_info.job_title, 
                    job_info.company_name
                )
                
                logger.info(f"Generated cover letter length: {len(formatted_letter)} characters")
                return formatted_letter
                
            logger.error("Failed to generate valid cover letter response")
            return CoverLetterGenerator._generate_fallback_cover_letter(resume_info, job_info)
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return CoverLetterGenerator._generate_fallback_cover_letter(resume_info, job_info)
    
    @staticmethod
    def _generate_fallback_cover_letter(resume_info: ResumeExtraction, job_info: JobDescriptionExtraction) -> str:
        """Generate a fallback cover letter when AI generation fails."""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Extract key information
        top_skills = ', '.join(resume_info.skills[:3]) if resume_info.skills else "technical skills"
        experience = resume_info.experience[0] if resume_info.experience else "professional experience"
        education = resume_info.education[0] if resume_info.education else "relevant education"
        
        cover_letter = f"""{current_date}

Dear Hiring Manager,

I am writing to express my strong interest in the {job_info.job_title} position at {job_info.company_name}. Having reviewed the job requirements, I am confident that my background and skills make me an excellent candidate for this role.

My experience includes {experience}, which has provided me with a solid foundation in software development and problem-solving. This background aligns well with your requirements for {', '.join(job_info.requirements[:2]) if job_info.requirements else 'technical expertise and collaboration skills'}.

My technical skills include {top_skills}, which I believe will contribute significantly to your team's success. I am particularly drawn to this opportunity because it combines my passion for technology with the chance to make a meaningful impact at {job_info.company_name}.

I would welcome the opportunity to discuss how my background and enthusiasm can contribute to your team. Thank you for considering my application, and I look forward to hearing from you.

Sincerely,
[Your Name]"""

        logger.info("Generated fallback cover letter")
        return cover_letter
    
    @staticmethod
    def create_cover_letter_object(content: str, job_info: JobDescriptionExtraction) -> CoverLetter:
        """Create a CoverLetter object from content."""
        return CoverLetter(
            content=content,
            job_title=job_info.job_title,
            company_name=job_info.company_name,
            generated_at=datetime.now()
        )
    
    @staticmethod
    def validate_cover_letter(content: str) -> bool:
        """Validate cover letter quality."""
        if not content or len(content.strip()) < 200:
            return False
        
        # Check for required elements
        required_elements = [
            "dear",
            "sincerely" or "regards" or "respectfully",
            "position" or "role" or "opportunity"
        ]
        
        content_lower = content.lower()
        return any(element in content_lower for element in required_elements)
    
    @staticmethod
    def get_cover_letter_statistics(content: str) -> dict:
        """Get statistics about the cover letter."""
        if not content:
            return {}
        
        words = content.split()
        sentences = content.split('.')
        paragraphs = content.split('\n\n')
        
        return {
            'character_count': len(content),
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'paragraph_count': len([p for p in paragraphs if p.strip()]),
            'avg_words_per_sentence': len(words) / max(len(sentences), 1)
        }