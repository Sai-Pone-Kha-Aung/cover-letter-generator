from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ResumeExtraction(BaseModel):
    """Model for extracted resume information."""
    experience: List[str] = Field(description="List of work experiences")
    skills: List[str] = Field(description="List of technical skills")
    education: List[str] = Field(description="List of education details")
    contact_info: str = Field(description="Contact information of the candidate")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class JobDescriptionExtraction(BaseModel):
    """Model for extracted job description information."""
    job_title: str = Field(description="Title of the job position")
    company_name: str = Field(description="Name of the hiring company")
    requirements: List[str] = Field(description="List of job requirements and qualifications")
    description: str = Field(description="Brief summary of job responsibilities")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CoverLetter(BaseModel):
    """Model for generated cover letter."""
    content: str = Field(description="Generated cover letter content")
    job_title: Optional[str] = Field(default=None, description="Target job title")
    company_name: Optional[str] = Field(default=None, description="Target company name")
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ExtractionResult(BaseModel):
    """Model for extraction operation results."""
    success: bool = Field(description="Whether the extraction was successful")
    data: Optional[dict] = Field(default=None, description="Extracted data")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    extraction_type: str = Field(description="Type of extraction performed")
    
class ProcessingStatus(BaseModel):
    """Model for tracking processing status."""
    stage: str = Field(description="Current processing stage")
    progress: float = Field(ge=0.0, le=100.0, description="Progress percentage")
    message: str = Field(description="Status message")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }