# 🚀 AI Cover Letter Generator

An intelligent cover letter generation tool powered by AI that creates personalized, professional cover letters by analyzing your resume and job descriptions. Built with Streamlit and supports both local Ollama models and cloud-based Gemini AI.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### Core Capabilities

- **Resume Analysis**: Automatically extracts skills, experience, and education from PDF resumes
- **Job Description Processing**: Analyzes job postings to identify key requirements and company information
- **AI-Powered Generation**: Creates personalized cover letters using advanced AI models
- **Multi-Provider Support**: Works with both local Ollama and cloud-based Gemini AI
- **Interactive UI**: Modern Streamlit interface with real-time progress tracking
- **Export Options**: Download generated letters as TXT or Markdown files

### AI Providers Supported

- **Ollama** (Local): deepseek-r1, llama3.2, llama3.1, mistral, codellama
- **Google Gemini** (Cloud): gemini-2.0-flash, gemini-2.0-pro, gemini-1.5-flash, gemini-1.5-pro

### Smart Features

- Fallback generation for reliable operation
- Progress tracking with detailed status updates
- Content validation and quality checks
- Automatic cleanup of temporary files
- Session state management for generation statistics

## 🏗️ Architecture

The application follows a modular architecture with clear separation of concerns:

```
├── main.py                    # Streamlit UI and main application logic
├── src/
│   ├── core/                  # Core processing logic
│   │   └── processor.py       # Main cover letter processing pipeline
│   ├── clients/               # AI provider implementations
│   │   ├── base_client.py     # Abstract base client interface
│   │   ├── ollama_client.py   # Ollama API client
│   │   └── gemini_client.py   # Google Gemini API client
│   ├── services/              # Business logic services
│   │   ├── resume_extractor.py      # Resume information extraction
│   │   ├── job_extractor.py         # Job description processing
│   │   └── cover_letter_generator.py # Cover letter generation
│   ├── models/                # Data models and schemas
│   │   └── data_models.py     # Pydantic models for type safety
│   ├── utils/                 # Utility functions
│   │   ├── pdf_utils.py       # PDF processing utilities
│   │   └── text_utils.py      # Text processing and cleaning
│   └── config/                # Configuration and settings
│       └── settings.py        # Application configuration
```

### Design Patterns Used

- **Strategy Pattern**: Multiple AI providers with common interface
- **Factory Pattern**: AI client creation and initialization
- **Service Layer**: Business logic separation
- **Repository Pattern**: Data extraction services
- **Async Processing**: Concurrent resume and job analysis

## 📋 Prerequisites

### System Requirements

- Python 3.8 or higher
- 4GB+ RAM (for local AI models)
- Internet connection (for Gemini API)

### For Ollama (Local AI)

- Ollama installed and running
- At least one AI model pulled (e.g., `deepseek-r1:latest`)
- Minimum 8GB RAM for larger models

### For Gemini (Cloud AI)

- Google AI Studio API key
- Active internet connection
- Valid Google account

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd cover-letter-generator
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama (Optional - for local AI)

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows - Download from https://ollama.ai
```

### 5. Pull AI Models (for Ollama)

```bash
# Start Ollama service
ollama serve

# In another terminal, pull models
ollama pull deepseek-r1:latest
ollama pull llama3.2
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# For Gemini AI (Optional)
GEMINI_API_KEY=your_gemini_api_key_here

# For Ollama (Optional - defaults provided)
OLLAMA_BASE_URL=http://localhost:11434
```

### Getting API Keys

#### Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy and add to your `.env` file

### Configuration Options

The application can be configured through `src/config/settings.py`:

```python
# Model Defaults
DEFAULT_OLLAMA_MODEL = "deepseek-r1:latest"
DEFAULT_GEMINI_MODEL = "gemini-pro"

# Generation Parameters
GENERATION_CONFIG = {
    'temperature': 0.7,      # Creativity level (0.0-1.0)
    'top_p': 0.9,           # Nucleus sampling
    'top_k': 40,            # Top-k sampling
    'max_tokens': 2000,     # Maximum response length
    'timeout': 180          # Request timeout (seconds)
}
```

## 📖 Usage Guide

### Quick Start

#### 1. Start the Application

```bash
streamlit run main.py
```

#### 2. Configure AI Provider

- **For Ollama**: Ensure Ollama is running (`ollama serve`)
- **For Gemini**: Enter your API key in the sidebar

#### 3. Generate Cover Letter

1. **Upload Resume**: Select your PDF resume file
2. **Paste Job Description**: Copy and paste the complete job posting
3. **Click Generate**: Wait for AI to process and generate your cover letter
4. **Review & Edit**: Use the tabs to preview, edit, and download

### Detailed Workflow

#### Step 1: Provider Selection

```python
# The app supports two AI providers:
providers = ["Ollama", "Gemini"]

# Each with multiple model options:
ollama_models = ["deepseek-r1:latest", "llama3.2", "llama3.1", "mistral"]
gemini_models = ["gemini-2.0-flash", "gemini-2.0-pro", "gemini-1.5-flash"]
```

#### Step 2: Document Processing

The application processes your inputs through several stages:

1. **PDF Text Extraction**: Extracts text from uploaded resume
2. **Resume Analysis**: Identifies skills, experience, and education
3. **Job Analysis**: Extracts requirements, company info, and role details
4. **Cover Letter Generation**: Creates personalized content using AI

#### Step 3: Output Options

- **Preview Tab**: Formatted display of generated letter
- **Edit Tab**: Editable text area with download options
- **Analysis Tab**: Generation statistics and improvement tips

### Advanced Features

#### Preview Mode

Enable "Preview Mode" to see detailed processing steps:

- Resume information extraction progress
- Job description analysis status
- Generation process updates

#### Generation Statistics

Track your usage with built-in metrics:

- Total cover letters generated
- Provider and model used
- Word count and paragraph analysis

## 🔧 Troubleshooting

### Common Issues

#### Ollama Connection Issues

**Problem**: "Cannot connect to Ollama"

```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama service
ollama serve

# Verify models are available
ollama list
```

#### Model Not Available

**Problem**: "Model 'model-name' not available"

```bash
# Pull the required model
ollama pull deepseek-r1:latest

# List available models
ollama list
```

#### Gemini API Issues

**Problem**: "Gemini API not accessible"

- Verify API key in `.env` file
- Check Google AI Studio quota limits
- Ensure internet connection is stable

#### PDF Processing Errors

**Problem**: "Could not extract text from PDF"

- Ensure PDF is not password protected
- Try with a different PDF file
- Check if PDF contains readable text (not just images)

#### Memory Issues

**Problem**: "Out of memory" errors

- Use smaller Ollama models (e.g., `llama3.2` instead of `deepseek-r1`)
- Close other applications
- Consider using Gemini instead of local models

### Performance Optimization

#### For Better Speed

- Use Gemini models for faster processing
- Ensure stable internet connection
- Use smaller Ollama models for local processing

#### For Better Quality

- Use larger models like `deepseek-r1:latest` or `gemini-2.0-pro`
- Provide detailed job descriptions
- Use well-formatted PDF resumes

### Logging and Debugging

#### Enable Debug Logging

```python
# In src/config/settings.py
setup_logging(level=logging.DEBUG)
```

#### Check Log Files

```bash
# View application logs
tail -f cv_generator.log

# Search for specific errors
grep "ERROR" cv_generator.log
```

### Getting Help

#### Common Solutions

1. **Restart the application**: `Ctrl+C` then `streamlit run main.py`
2. **Clear browser cache**: Hard refresh with `Cmd+Shift+R` (macOS)
3. **Check model status**: Verify AI provider is working correctly
4. **Update dependencies**: `pip install -r requirements.txt --upgrade`

#### Error Messages Guide

- `"Model not available"`: Pull the model with Ollama
- `"API Error"`: Check API keys and internet connection
- `"PDF extraction failed"`: Try a different PDF file
- `"Generation failed"`: Check AI provider configuration

## 🎯 Example Usage Scenarios

### Scenario 1: Software Engineer Position

```
1. Upload your technical resume (PDF)
2. Paste job description for "Senior Full Stack Developer at TechCorp"
3. Select provider (Ollama with deepseek-r1 or Gemini 2.0-flash)
4. Generate personalized cover letter highlighting relevant experience
5. Download and customize for submission
```

### Scenario 2: Career Change Application

```
1. Upload resume showing transferable skills
2. Paste job posting for new industry/role
3. Use Gemini for creative content generation
4. Focus on transferable skills and motivation
5. Edit generated content to add personal touch
```

### Scenario 3: Multiple Applications

```
1. Upload resume once
2. Process multiple job descriptions sequentially
3. Generate tailored cover letters for each position
4. Track generation statistics
5. Compare different approaches and models
```

## 🔄 Development Workflow

### Testing the Application

```bash
# Start the application
streamlit run main.py

# Test with sample data
# 1. Use a sample PDF resume
# 2. Paste a job description
# 3. Test both Ollama and Gemini providers
# 4. Verify output quality and formatting
```

### Code Quality Checks

```bash
# Format code with black
black src/

# Check type hints with mypy
mypy src/

# Run linting with flake8
flake8 src/
```

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🔗 Related Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Google Gemini API](https://ai.google.dev/)
- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

_Built with ❤️ using Python, Streamlit, and AI_
