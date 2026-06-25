import streamlit as st
import time
import tempfile
import os
import json
from langgraph.graph import StateGraph, START, END
from state import ArchitectureState
from agents import ontology_agent, table_analyst_agent, architect_agent, qa_agent
from unstructured.partition.pdf import partition_pdf

st.set_page_config(page_title="AI Architecture Generator", page_icon="🤖", layout="wide")

# --- YARDIMCI FONKSİYONLAR ---
def check_approval(state: ArchitectureState):
    if state.get("is_approved", False):
        return "onaylandi"
    else:
        if state.get("iteration_count", 0) >= 3:
            return "onaylandi"
        return "reddedildi"

def parse_uploaded_pdf(uploaded_file):
    # Streamlit'e yüklenen dosyayı ajanların okuyabilmesi için geçici olarak kaydet
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    # PDF'i fast modda oku
    elements = partition_pdf(filename=tmp_path, strategy="fast")
    
    raw_text = ""
    markdown_tables = ""
    for el in elements:
        if el.category == "Table":
            if hasattr(el.metadata, 'text_as_html') and el.metadata.text_as_html:
                markdown_tables += f"\n{el.metadata.text_as_html}\n"
        else:
            raw_text += f"{el.text}\n"
            
    os.unlink(tmp_path) # Geçici dosyayı sil
    return raw_text, markdown_tables

# --- ARAYÜZ (DASHBOARD) ---
st.title("🤖 Multi-Agent Architecture Blueprint Generator")
st.markdown("Bu sistem, karmaşık proje gereksinimlerini (PDF) okuyup, birbirini denetleyen 4 farklı yapay zeka ajanı ile **kurumsal seviyede bir sistem mimarisi (JSON)** üretir.")

with st.sidebar:
    st.header("📄 Belge Yükle")
    uploaded_file = st.file_uploader("Proje Gereksinimleri (PDF)", type=["pdf"])
    st.markdown("---")
    st.markdown("**Ajanlar:**\n1. Derin Analist\n2. Sistem Kuralları Analisti\n3. Mimar\n4. QA Denetçisi")

if uploaded_file is not None:
    st.success(f"{uploaded_file.name} başarıyla yüklendi!")
    
    if st.button("🚀 Mimariyi Oluştur (Ajanları Başlat)"):
        
        # LangGraph İş Akışını (Workflow) Kur
        workflow = StateGraph(ArchitectureState)
        workflow.add_node("Ontology_Agent", ontology_agent)
        workflow.add_node("Table_Analyst_Agent", table_analyst_agent)
        workflow.add_node("Architect_Agent", architect_agent)
        workflow.add_node("QA_Agent", qa_agent)
        
        workflow.add_edge(START, "Ontology_Agent")
        workflow.add_edge("Ontology_Agent", "Table_Analyst_Agent")
        workflow.add_edge("Table_Analyst_Agent", "Architect_Agent")
        workflow.add_edge("Architect_Agent", "QA_Agent")
        workflow.add_conditional_edges("QA_Agent", check_approval, {"onaylandi": END, "reddedildi": "Architect_Agent"})
        
        app_workflow = workflow.compile()

        # Ekranda canlı durum bildirimleri
        with st.status("Sistem başlatılıyor, lütfen bekleyin...", expanded=True) as status:
            st.write("📄 PDF analiz ediliyor (Bu işlem belge boyutuna göre biraz sürebilir)...")
            raw_text, markdown_tables = parse_uploaded_pdf(uploaded_file)
            
            initial_state = {
                "raw_pdf_text": raw_text,
                "markdown_tables": markdown_tables,
                "definitions_dict": {},
                "table_requirements": [],
                "architecture_blueprint": {},
                "qa_feedback": "",
                "is_approved": False,
                "iteration_count": 0
            }
            
            st.write("🧠 Yapay Zeka Ajanları devreye giriyor...")
            
            final_state = None
            # Ajanlar arası veri akışını Streamlit ekranına yansıt
            for output in app_workflow.stream(initial_state):
                for node_name, node_state in output.items():
                    if node_name == "Ontology_Agent":
                        st.write("✅ Ajan 1 (Derin Analist): İş kuralları başarıyla çıkarıldı.")
                    elif node_name == "Table_Analyst_Agent":
                        st.write("✅ Ajan 2 (Kural Çıkarıcı): Tablolar ve finansal kısıtlamalar analiz edildi.")
                    elif node_name == "Architect_Agent":
                        st.write(f"🏗️ Ajan 3 (Mimar): Mimari taslak oluşturuluyor (İterasyon: {node_state.get('iteration_count')})...")
                    elif node_name == "QA_Agent":
                        if node_state.get('is_approved'):
                            st.write("✅ Ajan 4 (Denetçi): QA Denetimi BAŞARILI. Mimari onaylandı!")
                        else:
                            st.write(f"❌ Ajan 4 (Denetçi): QA REDDETTİ. Gerekçe: {node_state.get('qa_feedback')}")
                            st.write("🔄 Ajan 3'e hataları düzeltmesi için geri dönülüyor...")
                    final_state = node_state
            
            status.update(label="Sistem Mimarisi Başarıyla Üretildi!", state="complete", expanded=False)
            
        # Nihai Çıktıyı Ekrana Bas
        st.subheader("✅ Üretilen Mimari (Blueprint)")
        if final_state and "architecture_blueprint" in final_state:
            st.json(final_state["architecture_blueprint"])
        else:
            st.error("Mimari üretilirken bir hata oluştu.")
else:
    st.info("Lütfen başlamak için sol menüden bir PDF belgesi yükleyin.")
