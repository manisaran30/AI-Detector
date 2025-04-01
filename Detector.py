import streamlit as st # type: ignore
import os
import io
import base64
from dotenv import load_dotenv # type: ignore
import pdf2image # type: ignore
from docx import Document # type: ignore
import google.generativeai as genai # type: ignore
import re

# Load API Key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get AI detection response
def get_ai_detection_response(content):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = "Detect how much percentage of the given text is AI-generated. Provide a numeric value."
    response = model.generate_content([content, prompt])
    return response.text

# Function to process uploaded files
def process_uploaded_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        pdf_parts = [{"mime_type": "image/jpeg", "data": base64.b64encode(img_byte_arr).decode()}]
        return pdf_parts
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    else:
        return None

# Function to extract percentage or handle non-AI content
def extract_percentage_from_result(result):
    match = re.search(r'\d+', result)
    if match:
        return int(match.group(0))
    else:
        return None

# Streamlit UI
st.set_page_config(page_title="AI Detection Meter", page_icon="🤖", layout="wide")
st.title("AI Detection Meter 📊")
st.write("Evaluate how much of your content is AI-generated.")

# Input Options
tab1, tab2 = st.tabs(["📝 Detect by Text", "📂 Detect by File"])

with tab1:
    input_text = st.text_area("Enter Text for AI Detection", height=150)
    if st.button("🔍 Detect AI in Text"):
        if input_text:
            with st.spinner("Analyzing text... ⏳"):
                result = get_ai_detection_response(input_text)
            st.success("✅ Analysis Complete!")
            st.subheader("🧠 AI Detection Score")
            percentage = extract_percentage_from_result(result)
            if percentage is not None:
                st.metric(label="AI-Generated Percentage", value=f"{percentage}%")
                st.progress(percentage / 100)
            else:
                st.write("❌ The content is not AI-generated.")

        else:
            st.error("⚠️ Please enter some text.")

with tab2:
    uploaded_file = st.file_uploader("Upload a Word/PDF file", type=["pdf", "docx"])
    if st.button("📑 Detect AI in File"):
        if uploaded_file:
            with st.spinner("Processing file... ⏳"):
                file_content = process_uploaded_file(uploaded_file)
                if file_content:
                    result = get_ai_detection_response(file_content)
                    st.success("✅ Analysis Complete!")
                    st.subheader("🧠 AI Detection Score")
                    percentage = extract_percentage_from_result(result)
                    if percentage is not None:
                        st.metric(label="AI-Generated Percentage", value=f"{percentage}%")
                        st.progress(percentage / 100)
                    else:
                        st.write("❌ The content is not AI-generated.")
                else:
                    st.error("⚠️ Unsupported file format.")
        else:
            st.error("⚠️ Please upload a file.")
