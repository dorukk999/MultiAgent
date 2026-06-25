import json
from langgraph.graph import StateGraph, START, END
from state import ArchitectureState
from agents import ontology_agent, table_analyst_agent, architect_agent, qa_agent
from pypdf import PdfReader

def parse_real_pdf(pdf_path: str):
    """
    PDF dosyasını pypdf ile okur. 
    Not: Bu metod tablo yapısını (HTML/Markdown) otomatik çıkarmaz, 
    ancak sistemin çökmesini engeller.
    """
    print(f"\n📄 '{pdf_path}' metin tabanlı olarak analiz ediliyor...\n")
    
    try:
        reader = PdfReader(pdf_path)
        raw_text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                raw_text += content + "\n"
        
        # Tablolar için gelişmiş ayrıştırma gerekirse burada 
        # pdfplumber gibi alternatifler incelenebilir.
        return raw_text, "Not: Tablolar metin içinden çekilmiştir."
    except Exception as e:
        print(f"[HATA] PDF okuma hatası: {e}")
        return "", ""

def check_approval(state: ArchitectureState):
    if state.get("is_approved", False):
        print("\n" + "="*50)
        print("✅ [SİSTEM] DENETÇİ ONAYLADI! MİMARİ BAŞARIYLA TAMAMLANDI.")
        print("="*50 + "\n")
        return "onaylandi"
    else:
        if state.get("iteration_count", 0) >= 3:
            print("\n" + "="*50)
            print("⚠️ [UYARI] MAKSİMUM DÖNGÜYE ULAŞILDI. SÜREÇ ZORLA SONLANDIRILIYOR.")
            print("="*50 + "\n")
            return "onaylandi" 
        
        print("\n" + "="*50)
        print(f"❌ [SİSTEM] DENETÇİ REDDETTİ! Gerekçe:\n{state.get('qa_feedback')}")
        print("🔄 Mimara (Ajan 3) hataları düzeltmesi için geri dönülüyor...")
        print("="*50 + "\n")
        return "reddedildi"

def main():
    print("🚀 Multi-Agent LangGraph Testi Başlatılıyor...\n")
    
    workflow = StateGraph(ArchitectureState)
    
    workflow.add_node("Ontology_Agent", ontology_agent)
    workflow.add_node("Table_Analyst_Agent", table_analyst_agent)
    workflow.add_node("Architect_Agent", architect_agent)
    workflow.add_node("QA_Agent", qa_agent)
    
    workflow.add_edge(START, "Ontology_Agent")
    workflow.add_edge("Ontology_Agent", "Table_Analyst_Agent")
    workflow.add_edge("Table_Analyst_Agent", "Architect_Agent")
    workflow.add_edge("Architect_Agent", "QA_Agent")
    
    workflow.add_conditional_edges(
        "QA_Agent",
        check_approval,
        {
            "onaylandi": END,
            "reddedildi": "Architect_Agent"
        }
    )
    
    app = workflow.compile()
    
    # PDF Dosya Adı
    pdf_dosya_adi = "Buddy_Rewards_Engine with Financial Tab (1).pdf"
    
    try:
        gercek_metin, gercek_tablolar = parse_real_pdf(pdf_dosya_adi)
    except FileNotFoundError:
        print(f"\n[HATA] '{pdf_dosya_adi}' dosyası bulunamadı!\n")
        return

    initial_state = {
        "raw_pdf_text": gercek_metin,
        "markdown_tables": gercek_tablolar,
        "definitions_dict": {},
        "table_requirements": [],
        "architecture_blueprint": {},
        "qa_feedback": "",
        "is_approved": False,
        "iteration_count": 0
    }
    
    print("-" * 50)
    print("CANLI TEST AKIŞI BAŞLIYOR")
    print("-" * 50 + "\n")
    
    for output in app.stream(initial_state):
        for node_name, node_state in output.items():
            print(f"[{node_name}] tamamlandı.")
            
if __name__ == "__main__":
    main()
