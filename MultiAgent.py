import time
from langgraph.graph import StateGraph, START, END
from state import ArchitectureState
from agents import ontology_agent, table_analyst_agent, architect_agent, qa_agent
from pypdf import PdfReader

def parse_real_pdf(pdf_path: str):
    try:
        reader = PdfReader(pdf_path)
        raw_text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                raw_text += content + "\n"
        return raw_text, "Not: Tablolar metin içinden çekilmiştir."
    except Exception as e:
        return "", ""

def check_approval(state: ArchitectureState):
    return "onaylandi" if state.get("is_approved", False) or state.get("iteration_count", 0) >= 3 else "reddedildi"

def run_workflow(pdf_file_path):
    raw_text, markdown_tables = parse_real_pdf(pdf_file_path)
    
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
    
    app = workflow.compile()
    
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
    
    final_state = None
    for output in app.stream(initial_state):
        time.sleep(1) # API limitleri için bekleme
        final_state = output
        
    return final_state
