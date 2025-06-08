import streamlit as st
import os
import asyncio
from src.core import process_cover_letter_request
from dotenv import load_dotenv

load_dotenv()


def main():
    st.set_page_config(
        page_title="AI Cover Letter Generator",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Add sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model provider selection
        provider = st.selectbox(
            "Select AI Provider",
            ["Ollama", "Gemini"],
            help="Choose between local Ollama models or Google Gemini"
        )
        
        if provider == "Ollama":
            model_name = st.selectbox(
                "Select Ollama Model",
                ["deepseek-r1:latest", "llama3.2", "llama3.1", "mistral", "codellama"],
                help="Choose the AI model for generation"
            )
            
            model_base_url = st.text_input(
                "Ollama Base URL",
                value="http://localhost:11434",
                help="Base URL for Ollama server (default: http://localhost:11434)",
                placeholder="http://localhost:11434"
            )
        else:  # Gemini
            model_name = st.selectbox(
                "Select Gemini Model",
                ["gemini-2.0-flash", "gemini-2.0-pro", "gemini-1.5-flash", "gemini-1.5-pro"],
                help="Choose the Gemini model for generation"
            )
            
            model_api_key = st.text_input(
                "Gemini API Key",
                type="password",
                placeholder="Enter your Gemini API key",
                help="Get your API key from Google AI Studio"
            )
        
        st.header("📊 Generation Stats")
        if 'generation_count' not in st.session_state:
            st.session_state.generation_count = 0
        st.metric("Cover Letters Generated", st.session_state.generation_count)

    st.title("🚀 AI Cover Letter Generator")
    st.caption("Upload your resume and paste the job description to generate a personalized cover letter powered by AI")

    # Initialize AI client based on provider
    @st.cache_resource
    def load_ai_client(provider_type, model, api_key=None, model_base_url=None):
        try:
            if provider_type == "Ollama":
                from src.clients import OllamaClient
                client = OllamaClient(model_name=model, base_url=model_base_url)
            else:  # Gemini
                from src.clients import GeminiClient
                client = GeminiClient(model_name=model, api_key=api_key)
            return client
        except Exception as e:
            st.error(f"Failed to initialize {provider_type} client: {e}")
            return None

    try:
        if provider == "Ollama":
            ai_client = load_ai_client(provider, model_name, model_base_url=model_base_url)
        else:  # Gemini
            if not model_api_key:
                st.warning("⚠️ Please enter your Gemini API key")
            ai_client = load_ai_client(provider, model_name, api_key=model_api_key)

        if ai_client is None:
            return
            
        # Check model availability
        if ai_client.check_model_availability():
            st.success(f"✅ {provider} {model_name} initialized successfully!")
        else:
            if provider == "Ollama":
                st.error(f"❌ Model '{model_name}' not available")
                st.info(f"Please pull the model: `ollama pull {model_name}`")
            else:
                st.error(f"❌ Gemini API not accessible")
                st.info("Please check your GEMINI_API_KEY in .env file")
            return
            
    except Exception as e:
        st.error(f"❌ Failed to initialize {provider} client: {e}")
        if provider == "Ollama":
            st.info("Make sure Ollama is running: `ollama serve`")
        else:
            st.info("Please check your Gemini API key configuration")
        return

    # Main input section
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("📄 Upload Resume")
        uploaded_file = st.file_uploader(
            "Choose your resume (PDF)", 
            type=["pdf"],
            help="Upload your resume in PDF format"
        )
        
        if uploaded_file:
            st.success(f"✅ {uploaded_file.name} uploaded successfully")
            
    with col2:
        st.subheader("📋 Job Description")
        job_description = st.text_area(
            "Paste the complete job description", 
            height=300,
            placeholder="Copy and paste the full job posting here...\n\nInclude:\n• Job title\n• Company name\n• Requirements\n• Responsibilities",
            help="Include all relevant details for better customization"
        )
        
        if job_description:
            word_count = len(job_description.split())
            st.caption(f"📊 Words: {word_count}")

    # Generation controls
    col3, col4, col5 = st.columns([2, 1, 1])
    
    with col3:
        generate_btn = st.button(
            "🎯 Generate Cover Letter", 
            type="primary",
            use_container_width=True,
            disabled=not (uploaded_file and job_description)
        )
    
    with col4:
        if st.button("🔄 Clear All", use_container_width=True):
            st.rerun()
    
    with col5:
        preview_mode = st.toggle("👁️ Preview Mode", help="Show generation steps")

    if generate_btn:
        if uploaded_file and job_description.strip():
            try:
                # Create progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                async def process_with_enhanced_status():
                    status_text.info("🔍 Analyzing your resume...")
                    progress_bar.progress(25)
                    
                    if preview_mode:
                        st.info("📖 Extracting resume information...")
                    
                    status_text.info("🎯 Processing job requirements...")
                    progress_bar.progress(50)
                    
                    if preview_mode:
                        st.info("🏢 Analyzing job description...")
                    
                    status_text.info("✍️ Crafting your cover letter...")
                    progress_bar.progress(75)
                    
                    cover_letter = await process_cover_letter_request(
                        uploaded_file, job_description.strip(), ai_client
                    )
                    
                    progress_bar.progress(100)
                    return cover_letter
                
                # Run the async process
                cover_letter = asyncio.run(process_with_enhanced_status())
                
                if cover_letter:
                    status_text.empty()
                    progress_bar.empty()
                    
                    st.session_state.generation_count += 1
                    st.success("🎉 Cover letter generated successfully!")

                    # Enhanced display tabs
                    tab1, tab2, tab3 = st.tabs(["📖 Preview", "📝 Edit & Copy", "📊 Analysis"])

                    with tab1:
                        st.markdown("### 📄 Your Generated Cover Letter")
                        st.markdown("---")
                        
                        # Display with better formatting
                        formatted_letter = cover_letter.replace('\n\n', '\n\n> ')
                        st.markdown(formatted_letter)
                        
                        # Quick actions
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("👍 Looks Good!", type="primary"):
                                st.balloons()
                        with col_b:
                            if st.button("🔄 Regenerate"):
                                st.rerun()
                    
                    with tab2:
                        st.markdown("### ✏️ Edit Your Cover Letter")
                        edited_letter = st.text_area(
                            "Make any adjustments:", 
                            value=cover_letter,
                            height=400,
                            help="You can edit the generated content before downloading"
                        )
                        
                        col_download, col_copy = st.columns(2)
                        
                        with col_download:
                            st.download_button(
                                label="📥 Download as TXT",
                                data=edited_letter,
                                file_name="cover_letter.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        
                        with col_copy:
                            st.download_button(
                                label="📄 Download as Markdown",
                                data=edited_letter,
                                file_name="cover_letter.md",
                                mime="text/markdown",
                                use_container_width=True
                            )
                    
                    with tab3:
                        st.markdown("### 📊 Generation Analysis")
                        
                        col_stats1, col_stats2, col_stats3 = st.columns(3)
                        
                        with col_stats1:
                            word_count = len(cover_letter.split())
                            st.metric("Word Count", word_count)
                        
                        with col_stats2:
                            paragraph_count = len([p for p in cover_letter.split('\n\n') if p.strip()])
                            st.metric("Paragraphs", paragraph_count)
                        
                        with col_stats3:
                            st.metric("Provider", f"{provider}")
                            st.caption(f"Model: {model_name}")
                        
                        # Show tips
                        st.info("💡 **Tips for improvement:**\n"
                               "• Customize the greeting with hiring manager's name if available\n"
                               "• Add specific examples from your experience\n"
                               "• Tailor the closing to match company culture")
                        
                else: 
                    st.error("❌ Failed to generate cover letter. Please check your inputs and try again.")
                    
            except Exception as e:
                st.error(f"🚨 An error occurred: {str(e)}")
                st.info("Try refreshing the page or check your AI provider configuration.")
        else:
            st.warning("⚠️ Please upload your resume and paste the job description.")

    # Enhanced help section
    with st.expander("❓ How to Use This Tool", expanded=False):
        st.markdown("""
        ### 🚀 Quick Start Guide
        
        **Prerequisites:**
        
        **For Ollama:**
        1. Install Ollama: [Download here](https://ollama.ai)
        2. Start Ollama service: `ollama serve`
        3. Pull a model: `ollama pull deepseek-r1:latest`

        **For Gemini:**
        1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Add it to your .env file as GEMINI_API_KEY
        3. Install the package: `pip install google-generativeai`

        **Steps:**
        1. **Select Provider** ⚙️ - Choose between Ollama (local) or Gemini (cloud)
        2. **Upload Resume** 📄 - Upload your current resume in PDF format
        3. **Paste Job Description** 📋 - Copy the complete job posting
        4. **Generate** 🎯 - Click generate and wait for AI to craft your letter
        5. **Review & Edit** ✏️ - Review and customize the generated content
        6. **Download** 📥 - Save your personalized cover letter

        ### 💡 Pro Tips
        - Gemini models are faster but require internet connection
        - Ollama models run locally and work offline
        - Different providers may produce varying writing styles
        - Include complete job descriptions for better customization
        """)
        
    # Footer
    st.markdown("---")
    st.markdown(f"*Powered by {provider} AI • Built with Streamlit*")

if __name__ == "__main__":
    main()