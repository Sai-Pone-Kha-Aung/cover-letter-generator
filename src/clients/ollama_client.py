import logging
import requests
from typing import Dict, Any
from .base_client import BaseClient

logger = logging.getLogger(__name__)

class OllamaClient(BaseClient):
    def __init__(self, model_name: str = None, base_url: str = None or "http://localhost:11434"):
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
        #Generate response using OLLAMA API.
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
        
    def get_available_models(self) -> list:
        """Get a list of available models from the Ollama server."""
        try:
            response = requests.get(self.tags_url, timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            else:
                logger.error(f"Failed to fetch models: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Error fetching available models: {e}")
            return []