import google.generativeai as genai
import streamlit as st

# API Anahtarını Streamlit'in güvenli kasasından çekiyoruz
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def get_json_model():
    return genai.GenerativeModel(
        model_name="gemini-2.5-pro", 
        generation_config={"response_mime_type": "application/json"}
    )

llm = get_json_model()
