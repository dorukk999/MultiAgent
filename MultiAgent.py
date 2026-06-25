import json
from langgraph.graph import StateGraph, START, END
from state import ArchitectureState
from agents import ontology_agent, table_analyst_agent, architect_agent, qa_agent

# YENİ EKLENEN: PDF Ayrıştırma Kütüphanesi
from unstructured.partition.pdf import partition_pdf

def parse_real_pdf(pdf_path: str):
    print(f"\n📄 '{pdf_path}' analiz ediliyor... (Bu işlem PDF'in uzunluğuna göre biraz sürebilir, lütfen bekle)\n")
    
    # PDF'i OCR kullanmadan doğrudan hızlı (fast) strateji ile okuyoruz
    elements = partition_pdf(
        filename=pdf_path,
        strategy="fast" 
    )
    
    raw_text = ""
    markdown_tables = ""
    
    for el in elements:
        if el.category == "Table":
            if hasattr(el.metadata, 'text_as_html') and el.metadata.text_as_html:
                markdown_tables += f"\n{el.metadata.text_as_html}\n"
        else:
            raw_text += f"{el.text}\n"
            
    return raw_text, markdown_tables

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
    
    # ---------------------------------------------------------
    # GERÇEK PDF TESTİ
    # ---------------------------------------------------------
    pdf_dosya_adi = "Buddy_Rewards_Engine with Financial Tab (1).pdf"
    
    try:
        gercek_metin, gercek_tablolar = parse_real_pdf(pdf_dosya_adi)
    except FileNotFoundError:
        print(f"\n[HATA] '{pdf_dosya_adi}' dosyası bulunamadı! Lütfen test edeceğin PDF'i MultiAgent.py ile aynı klasöre koy.\n")
        return
    except Exception as e:
        print(f"\n[HATA] PDF okunurken bir sorun oluştu: {e}\n")
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
            print(f"[{node_name}] tamamlandı. Çıktı Özeti:")
            
            if node_name == "Ontology_Agent":
                print(json.dumps(node_state.get("definitions_dict"), indent=2, ensure_ascii=False))
            elif node_name == "Table_Analyst_Agent":
                print(json.dumps(node_state.get("table_requirements"), indent=2, ensure_ascii=False))
            elif node_name == "Architect_Agent":
                print(json.dumps(node_state.get("architecture_blueprint"), indent=2, ensure_ascii=False))
            elif node_name == "QA_Agent":
                print(f"Onay Durumu: {node_state.get('is_approved')}")
                print(f"Geri Bildirim: {node_state.get('qa_feedback')}")
            
            print("\n" + "-" * 30 + "\n")

if __name__ == "__main__":
    main()