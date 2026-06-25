import json
from state import ArchitectureState
from llm_config import llm

def parse_json_response(response_text: str) -> dict:
    try:
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"[HATA] JSON Parse edilemedi: {e}")
        return {}

def ontology_agent(state: ArchitectureState):
    print("-> Ajan 1 (Derin Analist) Kuralları ve Durumları Çıkarıyor...")
    
    prompt = f"""
    Sen bir Baş İş Analistisin. Aşağıdaki metni oku ve bir kod üretici yapay zekanın (AI Coder) ihtiyaç duyacağı tüm kuralları atomik (tekil) olarak çıkar.
    Sadece basit tanımları değil, özellikle şunları ara:
    - State Machines (Durum geçişleri, örn: Pending -> Settled olurken ne tetiklenir?)
    - Edge Cases (Sınır durumlar, limitler, kısıtlamalar, süre aşımları)
    - Finansal veya Matematiksel Formüller (Puanlama, kesintiler, iadeler)
    
    Çıktını SADECE aşağıdaki JSON formatında ver:
    {{
        "business_rules": [
            {{"rule_id": "BR_01", "category": "State/Finance/Limit", "description": "Kuralın çok detaylı açıklaması", "source": "Metindeki yeri"}}
        ]
    }}
    
    İncelenecek Metin:
    {state.get('raw_pdf_text')}
    """
    
    response = llm.generate_content(prompt)
    result = parse_json_response(response.text)
    return {"definitions_dict": result}

def table_analyst_agent(state: ArchitectureState):
    print("-> Ajan 2 (Sistem Kuralları Analisti) Tabloları Çözümlüyor...")
    
    prompt = f"""
    Aşağıdaki metinlerdeki tabloları incele. 
    KESİN EMİR: EĞER METİNDE 'SİPARİŞ', 'ÜRÜN', 'MÜŞTERİ' GİBİ KELİMELER YOKSA ASLA KENDİNDEN VERİTABANI TABLOSU UYDURMA!
    Senin tek görevin PDF'teki 'Action Registry' tablolarından H01, TR02, C01 gibi 'Action Code'ları, Puanları, Limitleri ve Finansal tabloları bulmaktır. 
    
    Her bir tablodan şu bilgileri çıkar:
    1. Aktörler ve yapabilecekleri spesifik aksiyonlar (Örn: TR01, H01, CT01) ve bunların puan/limit değerleri.
    2. Finansal bütçe seviyeleri (Tiers) ve stratejiler (Conservative, Growth vb.).
    3. Olay zinciri (Event chain) bağımlılıkları ve dolandırıcılık (fraud) engelleme kuralları.
    
    Çıktını SADECE JSON formatında ver. Eğer uyan bir tablo bulamazsan listeleri boş bırak ([]), asla uydurma yapma:
    {{
        "action_registry_and_limits": [
            {{"actor": "Aktör Adı", "action_code": "Kod (Örn: TR02)", "points": "Puan", "limit_and_cooldown": "Kısıtlamalar", "validation": "Doğrulama kuralı"}}
        ],
        "financial_and_tier_rules": [
            {{"tier_or_strategy": "Seviye/Strateji Adı", "description": "Detaylar"}}
        ],
        "fraud_and_chain_safeguards": [
            {{"rule_name": "Kural/Zincir Adı", "action_to_take": "Alınacak aksiyon veya kısıtlama"}}
        ]
    }}
    
    İncelenecek Tablolar:
    {state.get('markdown_tables')}
    """
    
    response = llm.generate_content(prompt)
    result = parse_json_response(response.text)
    return {"table_requirements": result}

def architect_agent(state: ArchitectureState):
    print("-> Ajan 3 (Mimar) AI-Ready Blueprint'i Tasarlıyor...")
    
    current_iter = state.get("iteration_count", 0)
    qa_feedback_text = state.get('qa_feedback', '')
    
    feedback_section = f"\nDİKKAT! DENETÇİDEN GERİ BİLDİRİM GELDİ. ŞU EKSİKLERİ KESİNLİKLE GİDER:\n{qa_feedback_text}\n" if qa_feedback_text else ""
    
    prompt = f"""
    Sen bir Software Architect'sin. Görevin, bir 'Yapay Zeka Kodlama Asistanının (Cursor/Copilot)' alıp doğrudan kod yazmaya başlayabileceği, %100 eksiksiz bir mimari taslak (Blueprint) oluşturmaktır.
    
    Aşağıdaki iş kurallarını (Ajan 1) ve Aksiyon/Finans Kısıtlamalarını (Ajan 2) KULLANARAK sistemi tasarla.
    {feedback_section}
    
    KRİTİK KURALLAR:
    1. ASLA ÖZETLEME YAPMA. Tüm aktör aksiyonlarını (H01, TR02 vb.), olay zincirlerini ve finansal katmanları tek tek yaz.
    2. 'state_machines_and_lifecycles' bölümü çok kritiktir. Bir objenin durumları arasındaki geçişleri ve o geçişte hangi fonksiyonların çalışması gerektiğini detaylıca yaz.
    3. GÜVENLİK AĞI: Eğer Ajan 2'den gelen verilerde uydurma tablolar (Sipariş, Ürün, Müşteri vb.) varsa ONLARI KESİNLİKLE GÖRMEZDEN GEL. Sadece Ajan 1'in kurallarına ve PDF'in gerçek içeriğine odaklan.
    
    Çıktını KESİNLİKLE VE SADECE aşağıdaki JSON formatında ver:
    {{
      "system_architecture_blueprint": {{
        "database_models": [
          {{
            "model_name": "Model Adi",
            "fields": [{{"name": "isim", "type": "tip", "rules": ["kural1"]}}]
          }}
        ],
        "api_endpoints_and_services": [
          {{
            "endpoint": "/api/... veya ServiceMethodName",
            "method": "POST/GET vb",
            "logic_steps": ["Adım 1: Doğrulama", "Adım 2: Hesaplama... HER DETAYI YAZ"]
          }}
        ],
        "actor_action_registry": [
          {{"actor": "Aktör", "action_code": "Kod", "description": "Açıklama", "points": "Puan", "validation_rules": ["kural 1"]}}
        ],
        "event_chain_safeguards": [
          {{"chain_name": "Zincir Adı (Örn: Backhaul Chain)", "required_sequence": ["TR02", "TR03"], "reversal_conditions": "İptal şartları"}}
        ],
        "financial_distribution_strategies": [
          {{"strategy": "Strateji Adı", "tier_allocations": ["Tier detayları"]}}
        ],
        "state_machines_and_lifecycles": [
          {{
            "entity": "Hangi obje (Örn: RewardEvent)",
            "transitions": [
              {{"from": "STATE_A", "to": "STATE_B", "trigger": "Ne tetikler?", "actions_to_execute": ["Puanı ekle"]}}
            ]
          }}
        ],
        "background_jobs_and_crons": [
          {{
            "job_name": "Örn: Aylık Puan Sıfırlama",
            "frequency": "Çalışma sıklığı",
            "execution_logic": ["Kimin puanı silinecek", "Hangi kurallar geçerli"]
          }}
        ],
        "unmapped_or_complex_rules": [
          "Mimaride tam oturtamadığın ama kod yazıcının bilmesi gereken ekstra notlar"
        ]
      }}
    }}
    
    Ajan 1 (İş Kuralları):
    {json.dumps(state.get('definitions_dict'), ensure_ascii=False)}
    
    Ajan 2 (Veri ve Aksiyon Kuralları):
    {json.dumps(state.get('table_requirements'), ensure_ascii=False)}
    """
    
    response = llm.generate_content(prompt)
    result = parse_json_response(response.text)
    return {"architecture_blueprint": result, "iteration_count": current_iter + 1}

def qa_agent(state: ArchitectureState):
    print("-> Ajan 4 (Sert Denetçi) Mimariyi Kod Üretilebilirliği Açısından Doğruluyor...")
    
    prompt = f"""
    Sen acımasız bir Kalite Kontrol (QA) Denetçisisin. 
    Aşağıda üretilen 'Mimari Blueprint', bir AI kod yazıcısına verilecek. Eğer orijinal kurallarda olan bir 'Sınır Durum (Edge case)', 'Aksiyon Kodu (TR01 vb)', 'Zincirleme Kural' veya 'Finansal Strateji' mimarinin ilgili kısımlarına YAZILMAMIŞSA, bu kod hatalı üretilecek demektir.
    
    Orijinal kurallar ile Blueprint'i karşılaştır. Atlanan en ufak bir detay var mı?
    
    Çıktını SADECE aşağıdaki JSON formatında ver:
    {{
        "is_approved": true veya false,
        "feedback": "Eğer false ise, SADECE EKSİK OLAN KURALLARI MİMARA SÖYLE (Örn: 'TR02 aksiyon kodu atlanmış' veya 'Balanced finansal stratejisi eksik'). True ise 'Eksik yok' yaz."
    }}
    
    Orijinal Kurallar: {json.dumps(state.get('definitions_dict'), ensure_ascii=False)}
    Veri Kısıtlamaları: {json.dumps(state.get('table_requirements'), ensure_ascii=False)}
    Üretilen Blueprint: {json.dumps(state.get('architecture_blueprint'), ensure_ascii=False)}
    """
    
    response = llm.generate_content(prompt)
    result = parse_json_response(response.text)
    
    is_approved = result.get("is_approved", False)
    feedback = result.get("feedback", "Geri bildirim okunamadı.")
    
    return {"is_approved": is_approved, "qa_feedback": feedback}