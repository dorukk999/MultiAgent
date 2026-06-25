import streamlit as st
import os
from MultiAgent import run_workflow

st.set_page_config(page_title="AI Architecture Generator", layout="wide")
st.title("🤖 Multi-Agent Architecture Blueprint Generator")

uploaded_file = st.file_uploader("Proje Gereksinimleri (PDF)", type=["pdf"])

if uploaded_file is not None:
    # Geçici dosyayı kaydet
    temp_path = f"temp_{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("🚀 Mimariyi Oluştur"):
        with st.status("Ajanlar çalışıyor, lütfen bekleyin...", expanded=True) as status:
            try:
                # İş akışını başlat
                result = run_workflow(temp_path)
                st.success("Sistem Mimarisi Başarıyla Üretildi!")
                
                # Sonucu JSON formatında göster
                st.subheader("✅ Üretilen Mimari (Blueprint)")
                st.json(result)
                
            except Exception as e:
                st.error(f"Hata oluştu: {e}")
            finally:
                # Geçici dosyayı temizle
                if os.path.exists(temp_path):
                    os.remove(temp_path)
else:
    st.info("Lütfen başlamak için bir PDF belgesi yükleyin.")
