# 🚀 Quick Start Guide

This guide will get you up and running with the AI Cover Letter Generator in under 5 minutes!

## ⚡ Fast Setup

### 1. Prerequisites Check

```bash
# Check Python version (3.8+ required)
python --version

# Check if you have pip installed
pip --version
```

### 2. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 3. Choose Your AI Provider

#### Option A: Ollama (Local AI - Recommended for Privacy)

```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama service
ollama serve

# In another terminal, pull a model
ollama pull deepseek-r1:latest
```

#### Option B: Google Gemini (Cloud AI - Faster & No Setup)

```bash
# Get your API key from: https://makersuite.google.com/app/apikey
# Copy .env.example to .env and add your API key
cp .env.example .env
# Edit .env file and add your GEMINI_API_KEY
```

### 4. Run the Application

```bash
streamlit run main.py
```

## 🎯 First Cover Letter

1. **Open your browser** - Streamlit will automatically open `http://localhost:8501`

2. **Select your AI provider** in the sidebar:

   - Choose "Ollama" if you installed it locally
   - Choose "Gemini" if you have an API key

3. **Upload your resume** - Any PDF resume file

4. **Paste a job description** - Copy the full job posting

5. **Click "Generate Cover Letter"** - Wait 30-60 seconds

6. **Review and download** - Use the tabs to preview, edit, and download

## 🔧 Troubleshooting

### Ollama Issues

```bash
# Check if Ollama is running
ps aux | grep ollama

# Restart Ollama
ollama serve

# List available models
ollama list
```

### Gemini Issues

- Verify your API key in the `.env` file
- Check your internet connection
- Ensure you haven't exceeded API limits

### Common Fixes

- Restart the app: `Ctrl+C` then `streamlit run main.py`
- Clear browser cache: `Cmd+Shift+R` (macOS)
- Check the terminal for error messages

## 📝 Tips for Best Results

### Resume Upload

- Use a well-formatted PDF
- Ensure text is readable (not just images)
- Include contact information, skills, and experience

### Job Description

- Copy the complete job posting
- Include company name, requirements, and responsibilities
- The more detail, the better the customization

### Model Selection

- **deepseek-r1** (Ollama): Best quality, slower
- **llama3.2** (Ollama): Good balance of speed/quality
- **gemini-2.0-flash** (Gemini): Fastest, requires internet
- **gemini-2.0-pro** (Gemini): Highest quality, requires internet

## 🎉 You're Ready!

Your AI Cover Letter Generator is now set up and ready to create personalized, professional cover letters. Happy job hunting! 🎯

---

Need help? Check the full Document.md for detailed documentation.
