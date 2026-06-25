from typing import List, Dict, TypedDict

class ArchitectureState(TypedDict):
    # Girdi Verileri
    raw_pdf_text: str             
    markdown_tables: str          
    
    # Ajanların Ürettiği Veriler
    definitions_dict: Dict        
    table_requirements: List[Dict]
    architecture_blueprint: Dict  
    
    # Denetim ve Döngü Kontrolü
    qa_feedback: str              
    is_approved: bool             
    iteration_count: int