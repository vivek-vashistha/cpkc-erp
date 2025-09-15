# backend/agent/rag_tools.py
from typing import Dict, List, Any
from langchain_core.tools import tool
from ..core.quick_rag import QuickRAG

# Global RAG instance
_rag_instance = None

def get_rag_instance():
    """Get or create RAG instance"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = QuickRAG()
        # Initialize with sample data if knowledge base is empty
        if _rag_instance.get_knowledge_stats()["total_patterns"] == 0:
            from ..core.quick_rag import setup_quick_knowledge
            _rag_instance = setup_quick_knowledge()
    return _rag_instance

@tool
def search_anomaly_patterns(anomaly_type: str, context: str = "") -> Dict[str, Any]:
    """Search for relevant anomaly patterns and resolutions from knowledge base"""
    rag = get_rag_instance()
    query = f"{anomaly_type} {context}"
    
    patterns = rag.search_knowledge(query, "patterns")
    rules = rag.search_knowledge(query, "rules")
    
    return {
        "patterns": patterns,
        "rules": rules,
        "query": query,
        "total_found": len(patterns) + len(rules)
    }

@tool
def get_historical_cases(anomaly_type: str) -> Dict[str, Any]:
    """Get historical cases for similar anomalies"""
    rag = get_rag_instance()
    cases = rag.search_knowledge(anomaly_type, "cases")
    
    return {
        "cases": cases,
        "count": len(cases),
        "anomaly_type": anomaly_type
    }

@tool
def get_business_rules(rule_category: str) -> Dict[str, Any]:
    """Get business rules and SOPs for specific categories"""
    rag = get_rag_instance()
    rules = rag.search_knowledge(rule_category, "rules")
    
    return {
        "rules": rules,
        "category": rule_category,
        "count": len(rules)
    }

@tool
def add_resolution_feedback(anomaly_id: str, anomaly_type: str, resolution_success: bool, 
                          resolution_time_minutes: int, effectiveness_score: float) -> Dict[str, Any]:
    """Add feedback about anomaly resolution to improve future suggestions"""
    rag = get_rag_instance()
    
    # Create a case entry from this resolution
    case_title = f"Resolution Case: {anomaly_type} - {anomaly_id}"
    case_content = f"""
    Anomaly ID: {anomaly_id}
    Anomaly Type: {anomaly_type}
    Resolution Success: {resolution_success}
    Resolution Time: {resolution_time_minutes} minutes
    Effectiveness Score: {effectiveness_score}
    
    This case can be used to improve future anomaly detection and resolution suggestions.
    """
    
    case_id = rag.add_knowledge(
        "cases", 
        case_title, 
        case_content,
        {
            "anomaly_id": anomaly_id,
            "anomaly_type": anomaly_type,
            "success": resolution_success,
            "resolution_time": resolution_time_minutes,
            "effectiveness": effectiveness_score,
            "feedback_type": "resolution"
        }
    )
    
    return {
        "case_id": case_id,
        "status": "added",
        "message": f"Resolution feedback added for {anomaly_type}"
    }

@tool
def get_knowledge_base_stats() -> Dict[str, Any]:
    """Get statistics about the knowledge base"""
    rag = get_rag_instance()
    return rag.get_knowledge_stats()

# Export tools for easy import
RAG_TOOLS = {
    "search_anomaly_patterns": search_anomaly_patterns,
    "get_historical_cases": get_historical_cases,
    "get_business_rules": get_business_rules,
    "add_resolution_feedback": add_resolution_feedback,
    "get_knowledge_base_stats": get_knowledge_base_stats,
}

if __name__ == "__main__":
    # Test the RAG tools
    print("=== Testing RAG Tools ===")
    
    # Test pattern search
    result = search_anomaly_patterns("missing event", "sequence analysis")
    print(f"Pattern search result: {result['total_found']} items found")
    
    # Test historical cases
    cases = get_historical_cases("sequence")
    print(f"Historical cases: {cases['count']} cases found")
    
    # Test business rules
    rules = get_business_rules("sequence")
    print(f"Business rules: {rules['count']} rules found")
    
    # Test stats
    stats = get_knowledge_base_stats()
    print(f"Knowledge base stats: {stats}")
