import logging
import google.generativeai as genai
from .base_client import BaseClient

logger = logging.getLogger(__name__)

class GeminiClient(BaseClient):
    def __init__(self, api_key: str = None, model_name: str = None):
        super().__init__(model_name)
        self.api_key = api_key 
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please provide API key.")
        
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
        """Generate response using Gemini API."""
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
    
    def get_model_info(self) -> dict:
        """Get information about the current model."""
        return {
            "model_name": self.model_name,
            "provider": "Google Gemini",
            "api_configured": bool(self.api_key)
        }