import streamlit as st  # type: ignore
import os
import re
from dotenv import load_dotenv  # type: ignore
import google.generativeai as genai  # type: ignore

# Load API Key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get AI detection response
def get_ai_detection_response(content):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = "Detect how much percentage of the given text is AI-generated. Provide a numeric value."
    response = model.generate_content([content, prompt])
    return response.text

# Function to extract percentage from response
def extract_percentage_from_result(result):
    match = re.search(r'\d+', result)
    return int(match.group(0)) if match else None

# Streamlit UI
st.set_page_config(page_title="AI Detection Meter", page_icon="🤖", layout="wide")
st.title("AI Detection Meter 📊")
st.write("Evaluate how much of your content is AI-generated.")

input_text = st.text_area("Enter Text for AI Detection", height=150)
if st.button("🔍 Detect AI in Text"):
    if input_text:
        with st.spinner("Analyzing text... ⏳"):
            result = get_ai_detection_response(input_text)
        st.success("✅ Analysis Complete!")
        
        percentage = extract_percentage_from_result(result)
        if percentage is not None:
            st.subheader("🧠 AI Detection Score")
            st.metric(label="AI-Generated Percentage", value=f"{percentage}%")
            st.progress(percentage / 100)
        else:
            st.write("❌ The content is not AI-generated.")
    else:
        st.error("⚠️ Please enter some text.")
