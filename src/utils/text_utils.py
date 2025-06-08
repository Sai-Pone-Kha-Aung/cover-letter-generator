import re
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

def remove_thinking_tags(text: str) -> str:
    """Remove <think>...</think> tags from text."""
    if not text:
        return ""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

def clean_json_response(response_text: str) -> Optional[str]:
    """Extract and clean JSON from response text."""
    try:
        if not response_text:
            return None
            
        response_text = response_text.strip()
        
        # Find JSON boundaries
        if '{' in response_text and '}' in response_text:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_text = response_text[json_start:json_end]
            
            # Clean up the JSON
            json_text = json_text.replace('\n', ' ').replace('  ', ' ')
            return json_text
            
    except Exception as e:
        logger.warning(f"Error cleaning JSON response: {e}")
    
    return None

def parse_json_safely(json_text: str) -> Optional[Dict[Any, Any]]:
    """Safely parse JSON with error handling."""
    try:
        if not json_text:
            return None
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parsing failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error parsing JSON: {e}")
    
    return None

def extract_keywords(text: str, keywords: List[str]) -> List[str]:
    """Extract keywords from text."""
    if not text or not keywords:
        return []
    
    text_lower = text.lower()
    found_keywords = []
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)
    
    return list(set(found_keywords))  # Remove duplicates

def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep alphanumeric and basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\"\'@]', '', text)
    
    return text.strip()

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def extract_email(text: str) -> Optional[str]:
    """Extract email address from text."""
    if not text:
        return None
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)
    
    return matches[0] if matches else None

def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text."""
    if not text:
        return None
    
    # Pattern for various phone formats
    phone_patterns = [
        r'\+?1?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        r'\(\d{3}\)\s?\d{3}[-.]?\d{4}'
    ]
    
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0] if isinstance(matches[0], str) else ''.join(matches[0])
    
    return None

def format_cover_letter(content: str, job_title: str = None, company_name: str = None) -> str:
    """Format cover letter with proper structure."""
    if not content:
        return ""
    
    content = content.strip()
    
    # Ensure proper greeting
    if not content.startswith("Dear"):
        greeting = "Dear Hiring Manager,"
        if company_name:
            greeting = f"Dear {company_name} Hiring Team,"
        content = f"{greeting}\n\n{content}"
    
    # Ensure proper closing
    closings = ['sincerely', 'best regards', 'respectfully', 'regards']
    if not any(closing in content.lower() for closing in closings):
        content += f"\n\nSincerely,\n[Your Name]"
    
    # Add date if not present
    from datetime import datetime
    if not any(str(year) in content for year in range(2020, 2030)):
        current_date = datetime.now().strftime("%B %d, %Y")
        content = f"{current_date}\n\n{content}"
    
    return content

def validate_response_quality(response: str, min_length: int = 50) -> bool:
    """Validate if response meets quality requirements."""
    if not response:
        return False
    
    # Check minimum length
    if len(response.strip()) < min_length:
        return False
    
    # Check for error indicators
    error_indicators = [
        "Model", "API Error", "Request", "Cannot", "Connection",
        "Error:", "Failed to", "Unable to", "Exception"
    ]
    
    return not any(indicator in response for indicator in error_indicators)