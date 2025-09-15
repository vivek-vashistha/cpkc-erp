# backend/agent/quick_rag.py
import json
import os
from typing import Dict, List, Any
from datetime import datetime

class QuickRAG:
    def __init__(self, knowledge_file: str = "knowledge_base.json"):
        self.knowledge_file = knowledge_file
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict[str, Any]:
        """Load knowledge from JSON file"""
        if os.path.exists(self.knowledge_file):
            try:
                with open(self.knowledge_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                print(f"Warning: Could not load {self.knowledge_file}, starting with empty knowledge base")
        
        return {"patterns": [], "rules": [], "cases": []}
    
    def search_knowledge(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """Simple text-based search (no embeddings needed)"""
        results = []
        query_lower = query.lower()
        
        for category_name, items in self.knowledge.items():
            if category and category_name != category:
                continue
                
            for item in items:
                # Search in title and content
                title_match = query_lower in item.get('title', '').lower()
                content_match = query_lower in item.get('content', '').lower()
                
                if title_match or content_match:
                    # Add relevance score based on matches
                    relevance_score = 0
                    if title_match:
                        relevance_score += 2  # Title matches are more relevant
                    if content_match:
                        relevance_score += 1
                    
                    item_with_score = item.copy()
                    item_with_score['relevance_score'] = relevance_score
                    results.append(item_with_score)
        
        # Sort by relevance score and return top matches
        results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return results[:3]  # Return top 3 matches
    
    def add_knowledge(self, category: str, title: str, content: str, metadata: Dict = None):
        """Add new knowledge"""
        if category not in self.knowledge:
            self.knowledge[category] = []
        
        knowledge_item = {
            "title": title,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "id": f"{category}_{len(self.knowledge[category]) + 1}"
        }
        
        self.knowledge[category].append(knowledge_item)
        self._save_knowledge()
        return knowledge_item["id"]
    
    def _save_knowledge(self):
        """Save knowledge to file"""
        try:
            with open(self.knowledge_file, 'w') as f:
                json.dump(self.knowledge, f, indent=2)
        except Exception as e:
            print(f"Error saving knowledge: {e}")
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        return {
            "total_patterns": len(self.knowledge.get("patterns", [])),
            "total_rules": len(self.knowledge.get("rules", [])),
            "total_cases": len(self.knowledge.get("cases", [])),
            "last_updated": datetime.now().isoformat()
        }

# Initialize with sample data
def setup_quick_knowledge():
    """Setup the knowledge base with initial sample data"""
    rag = QuickRAG()
    
    # Add sample patterns
    rag.add_knowledge("patterns", "Missing Event Sequence Pattern", 
        "Common pattern: Missing 'At Border' event for cross-border shipments. "
        "Resolution: Check customs docs, insert event with customs timestamp. "
        "Success rate: 91%", {"success_rate": 0.91, "frequency": "high"})
    
    rag.add_knowledge("patterns", "ID Inconsistency Pattern",
        "Pattern: Multiple CarId values across events. Resolution: Use CarId from 'Created' event. "
        "Success rate: 87%", {"success_rate": 0.87, "frequency": "medium"})
    
    rag.add_knowledge("patterns", "Sequence Error Pattern",
        "Pattern: Events out of chronological order. Common causes: system delays, manual entry errors. "
        "Resolution: Reorder events based on timestamps. Success rate: 89%", 
        {"success_rate": 0.89, "frequency": "high"})
    
    rag.add_knowledge("patterns", "Terminal Conflict Pattern",
        "Pattern: Both 'Delivered' and 'Cancelled' events present. "
        "Resolution: Review terminal state, determine correct final status. Success rate: 85%",
        {"success_rate": 0.85, "frequency": "low"})
    
    # Add sample rules
    rag.add_knowledge("rules", "CPKC Event Sequence Standard",
        "Required sequence: Created → Picked Up → In Transit → At Border → Arrived → Delivered → Closed. "
        "Exceptions: Terminal shipments may skip 'Picked Up', cross-border MUST have 'At Border'",
        {"version": "2.1", "effective_date": "2025-01-01"})
    
    rag.add_knowledge("rules", "Equipment ID Consistency Rules",
        "CarId: Must be unique per shipment, format CPKC-XXXX. "
        "CSNId: Must be consistent across all events, format CSN-CPKC-XXXX-YYYY-MM-A. "
        "If multiple values detected, flag as anomaly requiring manual review",
        {"version": "1.8", "effective_date": "2024-12-01"})
    
    rag.add_knowledge("rules", "Cross-Border Shipment Rules",
        "All cross-border shipments MUST have 'At Border' event. "
        "Missing 'At Border' indicates data quality issue or customs processing delay. "
        "Check customs documentation for border crossing timestamps",
        {"version": "1.5", "effective_date": "2024-11-01"})
    
    # Add sample historical cases
    rag.add_knowledge("cases", "WB3005 Resolution Case",
        "Anomaly: Missing 'Arrived' and 'Delivered' events. "
        "Resolution: Added events based on terminal records. "
        "Outcome: Successfully resolved, customer confirmed delivery. "
        "Resolution time: 12 minutes", 
        {"waybill_id": "WB3005", "outcome": "success", "resolution_time": 12})
    
    rag.add_knowledge("cases", "WB4001 CarId Inconsistency",
        "Anomaly: Multiple CarId values (CPKC-1001, CPKC-2001). "
        "Resolution: Used CarId from 'Created' event (CPKC-1001). "
        "Outcome: Successfully standardized, no customer impact. "
        "Resolution time: 8 minutes",
        {"waybill_id": "WB4001", "outcome": "success", "resolution_time": 8})
    
    print(f"Knowledge base initialized with {rag.get_knowledge_stats()}")
    return rag

if __name__ == "__main__":
    # Test the knowledge base
    rag = setup_quick_knowledge()
    
    # Test search functionality
    print("\n=== Testing Search Functionality ===")
    patterns = rag.search_knowledge("missing event", "patterns")
    print(f"Found {len(patterns)} patterns for 'missing event'")
    for pattern in patterns:
        print(f"- {pattern['title']} (score: {pattern['relevance_score']})")
    
    rules = rag.search_knowledge("sequence", "rules")
    print(f"\nFound {len(rules)} rules for 'sequence'")
    for rule in rules:
        print(f"- {rule['title']} (score: {rule['relevance_score']})")
