# Vector-based RAG tools using OpenAI embeddings and ChromaDB
from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
from ..core.vector_rag import VectorRAG, setup_vector_knowledge_base

# Global vector RAG instance
_vector_rag_instance = None

def get_vector_rag_instance():
    """Get or create vector RAG instance"""
    global _vector_rag_instance
    if _vector_rag_instance is None:
        _vector_rag_instance = VectorRAG()
        # Initialize with sample data if knowledge base is empty
        stats = _vector_rag_instance.get_knowledge_stats()
        if stats.get("total_items", 0) == 0:
            print("Initializing vector knowledge base with sample data...")
            _vector_rag_instance = setup_vector_knowledge_base()
    return _vector_rag_instance

@tool
def search_anomaly_patterns(query: str, category: Optional[str] = None, top_k: int = 5) -> Dict[str, Any]:
    """
    Search for relevant anomaly patterns and resolutions using semantic similarity.
    Use this tool to find patterns, rules, and cases related to specific anomaly types or general waybill analysis.
    
    Args:
        query: The search query (e.g., "missing event sequence", "carid inconsistency", "anomaly detection")
        category: Optional filter by category ("patterns", "rules", "cases")
        top_k: Number of results to return (default: 5)
    """
    rag = get_vector_rag_instance()
    
    # Search for patterns and rules
    patterns = rag.search_knowledge(query, category="patterns", top_k=top_k)
    rules = rag.search_knowledge(query, category="rules", top_k=top_k)
    
    # If category is specified, only return that category
    if category == "patterns":
        return {
            "patterns": patterns,
            "rules": [],
            "query": query,
            "total_found": len(patterns),
            "search_type": "semantic_vector"
        }
    elif category == "rules":
        return {
            "patterns": [],
            "rules": rules,
            "query": query,
            "total_found": len(rules),
            "search_type": "semantic_vector"
        }
    else:
        return {
            "patterns": patterns,
            "rules": rules,
            "query": query,
            "total_found": len(patterns) + len(rules),
            "search_type": "semantic_vector"
        }

@tool
def get_historical_cases(anomaly_type: str, waybill_id: Optional[str] = None, top_k: int = 3) -> Dict[str, Any]:
    """
    Get historical cases for similar anomalies using semantic search.
    Use this to learn from past successful (or unsuccessful) resolutions.
    
    Args:
        anomaly_type: The type of anomaly to search for (e.g., "MISSING_STEP", "SEQUENCE_ERROR")
        waybill_id: Optional waybill ID to find related cases
        top_k: Number of cases to return (default: 3)
    """
    rag = get_vector_rag_instance()
    
    # Build search query
    search_query = f"{anomaly_type} resolution case"
    if waybill_id:
        search_query += f" {waybill_id}"
    
    cases = rag.search_knowledge(search_query, category="cases", top_k=top_k)
    
    return {
        "cases": cases,
        "count": len(cases),
        "anomaly_type": anomaly_type,
        "waybill_id": waybill_id,
        "search_type": "semantic_vector"
    }

@tool
def get_business_rules(rule_category: Optional[str] = None, query: str = "") -> Dict[str, Any]:
    """
    Retrieve business rules and Standard Operating Procedures (SOPs) using semantic search.
    Use this to understand CPKC's official guidelines for operations and anomaly handling.
    
    Args:
        rule_category: Optional category of rules to retrieve (e.g., "sequence", "equipment", "border")
        query: Optional specific query to search within rules
    """
    rag = get_vector_rag_instance()
    
    # Build search query
    search_query = query if query else rule_category if rule_category else "business rules"
    
    rules = rag.search_knowledge(search_query, category="rules", top_k=5)
    
    return {
        "rules": rules,
        "total_found": len(rules),
        "rule_category": rule_category,
        "query": search_query,
        "search_type": "semantic_vector"
    }

@tool
def get_similar_anomalies(anomaly_description: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Find similar anomalies based on description using semantic similarity.
    Use this to find patterns and cases similar to a specific anomaly description.
    
    Args:
        anomaly_description: Description of the anomaly to find similar cases for
        top_k: Number of similar cases to return (default: 5)
    """
    rag = get_vector_rag_instance()
    
    # Search across all categories for similar content
    all_results = rag.search_knowledge(anomaly_description, top_k=top_k)
    
    # Separate by category
    patterns = [r for r in all_results if r["category"] == "patterns"]
    cases = [r for r in all_results if r["category"] == "cases"]
    rules = [r for r in all_results if r["category"] == "rules"]
    
    return {
        "similar_patterns": patterns,
        "similar_cases": cases,
        "similar_rules": rules,
        "total_found": len(all_results),
        "query": anomaly_description,
        "search_type": "semantic_vector"
    }

@tool
def add_resolution_feedback(anomaly_id: str, 
                          anomaly_type: str, 
                          suggested_fix: str, 
                          success: bool, 
                          feedback_notes: Optional[str] = None,
                          resolution_time_minutes: int = 0) -> Dict[str, Any]:
    """
    Add feedback about the resolution of an anomaly to the knowledge base.
    This helps the system learn and improve future suggestions.
    
    Args:
        anomaly_id: The ID of the anomaly that was resolved
        anomaly_type: The type of the anomaly
        suggested_fix: The fix that was applied or suggested
        success: Boolean indicating if the resolution was successful
        feedback_notes: Optional notes about the resolution
        resolution_time_minutes: Time taken to resolve in minutes
    """
    rag = get_vector_rag_instance()
    
    outcome = "success" if success else "failure"
    title = f"Resolution Feedback: {anomaly_id}"
    content = f"Anomaly {anomaly_id} ({anomaly_type}) was resolved with fix: {suggested_fix}. Outcome: {outcome}. Resolution time: {resolution_time_minutes} minutes. Notes: {feedback_notes or 'N/A'}"
    
    metadata = {
        "anomaly_id": anomaly_id,
        "anomaly_type": anomaly_type,
        "suggested_fix": suggested_fix,
        "success": success,
        "outcome": outcome,
        "resolution_time_minutes": resolution_time_minutes,
        "feedback_notes": feedback_notes,
        "feedback_type": "resolution"
    }
    
    item_id = rag.add_knowledge("cases", title, content, metadata)
    
    return {
        "status": "success" if item_id else "failed",
        "message": f"Feedback recorded for anomaly {anomaly_id}",
        "item_id": item_id,
        "search_type": "semantic_vector"
    }

@tool
def get_knowledge_base_stats() -> Dict[str, Any]:
    """
    Get statistics about the vector knowledge base.
    Use this to understand the current state of the knowledge base.
    """
    rag = get_vector_rag_instance()
    stats = rag.get_knowledge_stats()
    
    return {
        "stats": stats,
        "search_type": "semantic_vector"
    }

# Export all tools
VECTOR_RAG_TOOLS = {
    "search_anomaly_patterns": search_anomaly_patterns,
    "get_historical_cases": get_historical_cases,
    "get_business_rules": get_business_rules,
    "get_similar_anomalies": get_similar_anomalies,
    "add_resolution_feedback": add_resolution_feedback,
    "get_knowledge_base_stats": get_knowledge_base_stats,
}

if __name__ == "__main__":
    # Test the vector RAG tools
    print("🧪 Testing Vector RAG Tools...")
    
    # Test search_anomaly_patterns
    print("\n1. Testing search_anomaly_patterns...")
    result = search_anomaly_patterns.invoke({
        "query": "missing event sequence",
        "top_k": 3
    })
    print(f"Found {result['total_found']} results")
    for pattern in result['patterns']:
        print(f"  - {pattern['title']} (similarity: {pattern['similarity_score']:.3f})")
    
    # Test get_historical_cases
    print("\n2. Testing get_historical_cases...")
    result = get_historical_cases.invoke({
        "anomaly_type": "MISSING_STEP",
        "top_k": 2
    })
    print(f"Found {result['count']} cases")
    for case in result['cases']:
        print(f"  - {case['title']} (similarity: {case['similarity_score']:.3f})")
    
    # Test get_business_rules
    print("\n3. Testing get_business_rules...")
    result = get_business_rules.invoke({
        "rule_category": "sequence",
        "query": "event sequence validation"
    })
    print(f"Found {result['total_found']} rules")
    for rule in result['rules']:
        print(f"  - {rule['title']} (similarity: {rule['similarity_score']:.3f})")
    
    # Test get_similar_anomalies
    print("\n4. Testing get_similar_anomalies...")
    result = get_similar_anomalies.invoke({
        "anomaly_description": "waybill missing closed event after delivered",
        "top_k": 3
    })
    print(f"Found {result['total_found']} similar items")
    print(f"  Patterns: {len(result['similar_patterns'])}")
    print(f"  Cases: {len(result['similar_cases'])}")
    print(f"  Rules: {len(result['similar_rules'])}")
    
    print("\n✅ Vector RAG Tools testing complete!")
