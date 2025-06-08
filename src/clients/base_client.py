from abc import ABC, abstractmethod
from typing import Optional

class BaseClient(ABC):
    def __init__(self, model_name: str = None):
        self.model_name = model_name
        
    @abstractmethod
    def check_model_availability(self) -> bool:
        """
        Check if the model is available.
        Returns True if the model is available, False otherwise.
        """
        pass
    
    @abstractmethod
    def generate_response(seld, prompt: str, max_length: int = 1024) -> str:
        """
        Generate a response based on the provided prompt.
        
        :param prompt: The input prompt to generate a response for.
        :param max_length: The maximum length of the generated response.
        :return: The generated response as a string.
        """
        pass
    
    def get_model_name(self) -> Optional[str]:
        """
        Get the name of the model.
        
        :return: The name of the model if set, otherwise None.
        """
        return self.model_name if self.model_name else None
    
    def set_model_name(self, model_name: str) -> None:
        self.model_name = model_name
