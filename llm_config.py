import google.generativeai as genai

# API anahtarını doğrudan buraya yapıştır (Tırnak işaretlerini silmeden!)
genai.configure(api_key="YOUR_API_KEY_HERE")

def get_json_model():
    return genai.GenerativeModel(
        # Modeli görselindeki en güçlü sürüme güncelledik
        model_name="gemini-2.5-pro", 
        generation_config={"response_mime_type": "application/json"}
    )

llm = get_json_model()