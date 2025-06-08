import os
import logging
from dotenv import load_dotenv

load_dotenv()

def setup_logging(level=logging.INFO):
    """Setup logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('cv_generator.log', mode='a')
        ]
    )
    return logging.getLogger(__name__)

# API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

# Model Defaults
DEFAULT_OLLAMA_MODEL = "deepseek-r1:latest"
DEFAULT_GEMINI_MODEL = "gemini-pro"

# Generation Parameters
GENERATION_CONFIG = {
    'temperature': 0.7,
    'top_p': 0.9,
    'top_k': 40,
    'max_tokens': 2000,
    'timeout': 180
}

# PDF Processing
PDF_CONFIG = {
    'max_pages': 50,
    'min_text_length': 50,
    'temp_file_suffix': '.pdf'
}

# Extraction Keywords
SKILL_KEYWORDS = [
    'python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 
    'git', 'html', 'css', 'typescript', 'angular', 'vue', 'kubernetes', 'jenkins'
]

EXPERIENCE_KEYWORDS = [
    'engineer', 'developer', 'manager', 'analyst', 'intern', 'specialist', 
    'consultant', 'architect', 'lead', 'senior', 'junior'
]

EDUCATION_KEYWORDS = [
    'university', 'college', 'degree', 'bachelor', 'master', 'phd', 
    'certification', 'diploma', 'institute', 'school'
]

REQUIREMENT_KEYWORDS = [
    'required', 'must have', 'experience with', 'proficient', 'knowledge of', 
    'familiar with', 'skilled in', 'expertise in'
]