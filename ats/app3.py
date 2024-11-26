# Import required libraries
from dotenv import load_dotenv 
import base64 
import streamlit as st
import os
import io
import fitz  
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini's LLM
genai.configure(api_key=os.getenv("AIzaSyDihPPXSbQZnb9Je8Mtu3ogt7lE4cuFjJU"))

# Function for generating response from LLM
def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')  
    response = model.generate_content([input, pdf_content, prompt])
    return response.text

# Function to post-process and refine the response
def refine_response(response_text):
    # Replace informal phrases with more formal equivalents based on common issues
    response_text = response_text.replace("ways to improve", "strategies to enhance")
    response_text = response_text.replace("you should", "it is recommended to")
    response_text = response_text.replace("might help", "could improve")
    # Add more replacements based on actual responses
    return response_text

# fitz function for handling and processing the PDF
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        first_page_text = pdf_document.load_page(0).get_text()
        pdf_document.close()
        return first_page_text
    else:
        raise FileNotFoundError("No file uploaded")

# Function to handle file download
def download_report(content, filename="resume_evaluation.txt"):
    b64 = base64.b64encode(content.encode()).decode()  # Encode the content
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">📥 Download Evaluation</a>'
    return href

# Streamlit configuration
st.set_page_config(page_title="HireWire Solutions", layout="wide")

# Header
st.title("🚀 HIREWIRE")

# Split layout: two columns for job description and PDF upload
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Job Description")
    input_text = st.text_area("Paste the job description here:", key="input", height=200)

with col2:
    st.subheader("📁 Upload Your Resume")
    uploaded_files = st.file_uploader("Upload multiple resumes", type=["pdf"], accept_multiple_files=True)
    if len(uploaded_files) > 0:
        st.success("✅ PDF(s) Uploaded Successfully")

# Spacer for clarity
st.markdown("<br>", unsafe_allow_html=True)

# Create a horizontal set of buttons
col3, col4 = st.columns([1, 1])
with col3:
    submit1 = st.button("🔍 Tell Me About the Resume")

with col4:
    submit2 = st.button("🧮 Percentage Match")

# Input prompts for the language model
input_prompt1 = """
You are an expert in career development and resume evaluation. Assess the provided resume in the context of the given job description. 
Offer a detailed evaluation, focusing on how well the resume meets the job requirements. Emphasize the strengths and areas for improvement in a professional manner. A
Also recommend courses for relevant skill gaps, and recommend the most suitable jobs for the resume(not taking the job description into consideration here)
"""

input_prompt2 = """
You are a professional ATS (Applicant Tracking System) specialist. Evaluate the resume based on the provided job description and calculate the match percentage. 
Present the results in a formal tone, including the percentage of match, any missing keywords, and a concise analysis of how the resume aligns with the job requirements.
"""

# Function to display progress bar
def show_progress_bar():
    with st.spinner("Processing..."):
        # Simulate processing time
        import time
        time.sleep(2)

# Show the response in the layout
if submit1 or submit2:
    if len(uploaded_files) > 0:
        for idx, uploaded_file in enumerate(uploaded_files):
            try:
                show_progress_bar()
                pdf_content = input_pdf_setup(uploaded_file)
                prompt = input_prompt1 if submit1 else input_prompt2
                response = get_gemini_response(prompt, pdf_content, input_text)
                
                # Refine the response for professionalism
                refined_response = refine_response(response)
                
                # Display results
                st.subheader(f"Resume {idx + 1} Evaluation")
                st.write(refined_response)
                
                # Provide download link
                st.markdown(download_report(refined_response, f"resume_{idx + 1}_evaluation.txt"), unsafe_allow_html=True)

            except Exception as e:
                st.error(f"⚠️ Error processing resume {idx + 1}: {str(e)}")
    else:
        st.error("⚠️ Please upload at least one resume!")

