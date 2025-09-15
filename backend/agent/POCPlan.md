[1 tool called]

For a **2-hour POC**, the full RAG implementation I suggested would be too complex. Let me give you **quick shortcuts** that can be implemented rapidly while still demonstrating the core value:

## **�� 2-Hour POC: Quick RAG Implementation**

### **Option 1: File-Based RAG (Fastest - 30 mins)**

Instead of a vector database, use simple file-based knowledge storage:

```python
# backend/agent/quick_rag.py
import json
import os
from typing import Dict, List, Any
from langchain_core.tools import tool

class QuickRAG:
    def __init__(self, knowledge_file: str = "knowledge_base.json"):
        self.knowledge_file = knowledge_file
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict[str, Any]:
        """Load knowledge from JSON file"""
        if os.path.exists(self.knowledge_file):
            with open(self.knowledge_file, 'r') as f:
                return json.load(f)
        return {"patterns": [], "rules": [], "cases": []}
    
    def search_knowledge(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """Simple text-based search (no embeddings needed)"""
        results = []
        query_lower = query.lower()
        
        for category_name, items in self.knowledge.items():
            if category and category_name != category:
                continue
                
            for item in items:
                if (query_lower in item.get('title', '').lower() or 
                    query_lower in item.get('content', '').lower()):
                    results.append(item)
        
        return results[:3]  # Return top 3 matches
    
    def add_knowledge(self, category: str, title: str, content: str, metadata: Dict = None):
        """Add new knowledge"""
        if category not in self.knowledge:
            self.knowledge[category] = []
        
        self.knowledge[category].append({
            "title": title,
            "content": content,
            "metadata": metadata or {}
        })
        
        self._save_knowledge()
    
    def _save_knowledge(self):
        """Save knowledge to file"""
        with open(self.knowledge_file, 'w') as f:
            json.dump(self.knowledge, f, indent=2)

# Initialize with sample data
def setup_quick_knowledge():
    rag = QuickRAG()
    
    # Add sample patterns
    rag.add_knowledge("patterns", "Missing Event Pattern", 
        "Common pattern: Missing 'At Border' event for cross-border shipments. "
        "Resolution: Check customs docs, insert event with customs timestamp. "
        "Success rate: 91%", {"success_rate": 0.91})
    
    rag.add_knowledge("patterns", "ID Inconsistency Pattern",
        "Pattern: Multiple CarId values. Resolution: Use CarId from 'Created' event. "
        "Success rate: 87%", {"success_rate": 0.87})
    
    # Add sample rules
    rag.add_knowledge("rules", "CPKC Event Sequence",
        "Required: Created → Picked Up → In Transit → At Border → Arrived → Delivered → Closed. "
        "Exceptions: Terminal shipments may skip 'Picked Up'")
    
    return rag
```

### **Option 2: Enhanced Agent with Quick RAG (1 hour)**

Modify your existing agent to include RAG tools:

```python
# backend/agent/quick_rag_agent.py
from langchain_core.tools import tool
from quick_rag import QuickRAG

# Add these tools to your existing TOOLS dict
@tool
def search_anomaly_patterns(anomaly_type: str, context: str = "") -> Dict[str, Any]:
    """Search for relevant anomaly patterns and resolutions"""
    rag = QuickRAG()
    query = f"{anomaly_type} {context}"
    
    patterns = rag.search_knowledge(query, "patterns")
    rules = rag.search_knowledge(query, "rules")
    
    return {
        "patterns": patterns,
        "rules": rules,
        "query": query
    }

@tool
def get_historical_cases(anomaly_type: str) -> Dict[str, Any]:
    """Get historical cases for similar anomalies"""
    rag = QuickRAG()
    cases = rag.search_knowledge(anomaly_type, "cases")
    
    return {
        "cases": cases,
        "count": len(cases)
    }

# Add to your existing TOOLS
TOOLS.update({
    "search_anomaly_patterns": search_anomaly_patterns,
    "get_historical_cases": get_historical_cases,
})
```

### **Option 3: Enhanced System Prompt (15 mins)**

Simply enhance your existing system prompt to include knowledge retrieval:

```python
# Modify your existing SYSTEM prompt
ENHANCED_SYSTEM = """
You are a logistics QA assistant with access to a knowledge base of anomaly patterns and resolutions.

BEFORE analyzing any waybill, ALWAYS call search_anomaly_patterns() to get relevant knowledge about:
- Similar anomaly patterns and their success rates
- Proven resolution strategies
- Business rules and exceptions

Your enhanced workflow:
1. Extract waybill_id
2. Call search_anomaly_patterns() with the anomaly types you're checking for
3. Use the retrieved knowledge to inform your analysis
4. Apply proven resolution strategies from historical cases
5. Return anomalies with confidence scores based on historical success rates

Example: If checking for sequence issues, call:
search_anomaly_patterns("sequence missing event", "waybill analysis")

Use the retrieved patterns to:
- Improve detection accuracy
- Suggest proven fixes
- Provide confidence scores based on historical success rates
- Reference specific business rules

Return only a JSON object with anomalies array. Include confidence scores based on retrieved knowledge.
"""
```

### **Option 4: Simple Learning from Anomalies (30 mins)**

Add basic learning by analyzing your existing anomalies.json:

```python
# backend/agent/simple_learning.py
import json
from collections import Counter
from typing import Dict, List, Any

class SimpleLearning:
    def __init__(self, anomalies_file: str = "cpkc-erp-portal/data/anomalies.json"):
        self.anomalies_file = anomalies_file
        self.learned_patterns = self._analyze_historical_anomalies()
    
    def _analyze_historical_anomalies(self) -> Dict[str, Any]:
        """Analyze existing anomalies to learn patterns"""
        try:
            with open(self.anomalies_file, 'r') as f:
                anomalies = json.load(f)
            
            # Count anomaly types
            type_counts = Counter(a['type'] for a in anomalies)
            
            # Count resolution success rates
            resolved = [a for a in anomalies if a['status'] == 'RESOLVED']
            resolution_success = len(resolved) / len(anomalies) if anomalies else 0
            
            # Find common fix patterns
            fix_patterns = Counter(a['suggested_fix'] for a in anomalies)
            
            return {
                "common_types": dict(type_counts.most_common(5)),
                "resolution_success_rate": resolution_success,
                "common_fixes": dict(fix_patterns.most_common(5)),
                "total_anomalies": len(anomalies)
            }
        except:
            return {"common_types": {}, "resolution_success_rate": 0, "common_fixes": {}}
    
    def get_confidence_for_anomaly(self, anomaly_type: str) -> float:
        """Get confidence score based on historical frequency"""
        if anomaly_type in self.learned_patterns["common_types"]:
            frequency = self.learned_patterns["common_types"][anomaly_type]
            total = self.learned_patterns["total_anomalies"]
            # Higher frequency = higher confidence (up to 0.95)
            return min(0.95, 0.7 + (frequency / total) * 0.25)
        return 0.7  # Default confidence for new types
    
    def get_suggested_fix(self, anomaly_type: str) -> str:
        """Get most common fix for anomaly type"""
        # This is simplified - in real implementation, you'd match by type
        common_fixes = self.learned_patterns["common_fixes"]
        if common_fixes:
            return list(common_fixes.keys())[0]
        return "Manual review required"

# Add to your agent
@tool
def get_learned_insights(anomaly_type: str) -> Dict[str, Any]:
    """Get learned insights about anomaly patterns"""
    learning = SimpleLearning()
    
    return {
        "confidence": learning.get_confidence_for_anomaly(anomaly_type),
        "suggested_fix": learning.get_suggested_fix(anomaly_type),
        "historical_patterns": learning.learned_patterns
    }
```

## **🎯 2-Hour Implementation Plan**

### **Hour 1: Core RAG Setup**
1. **15 mins**: Create `quick_rag.py` with file-based knowledge storage
2. **15 mins**: Add sample knowledge (patterns, rules, cases)
3. **15 mins**: Create RAG tools (`search_anomaly_patterns`, `get_historical_cases`)
4. **15 mins**: Integrate tools into your existing agent

### **Hour 2: Learning & Enhancement**
1. **30 mins**: Implement `simple_learning.py` to analyze existing anomalies
2. **15 mins**: Add learning tool to agent
3. **15 mins**: Update system prompt to use RAG tools
4. **15 mins**: Test with sample waybills and refine

## **🚀 Quick Demo Script**

```python
# backend/agent/demo_rag.py
def demo_rag_enhancement():
    """Quick demo of RAG-enhanced anomaly detection"""
    
    # Setup
    rag = setup_quick_knowledge()
    learning = SimpleLearning()
    
    # Simulate waybill analysis
    waybill_id = "WB3005"
    
    print(f"Analyzing {waybill_id} with RAG enhancement...")
    
    # Search for relevant patterns
    patterns = rag.search_knowledge("sequence missing", "patterns")
    print(f"Found {len(patterns)} relevant patterns")
    
    # Get learned insights
    insights = learning.get_confidence_for_anomaly("MISSING_STEP")
    print(f"Confidence based on history: {insights}")
    
    # This would be integrated into your existing agent
    return {
        "waybill_id": waybill_id,
        "rag_enhanced": True,
        "patterns_found": len(patterns),
        "confidence": insights
    }

if __name__ == "__main__":
    demo_rag_enhancement()
```

## **✅ What You'll Have After 2 Hours**

1. **File-based knowledge base** with patterns and rules
2. **RAG tools** integrated into your existing agent
3. **Simple learning** from historical anomalies
4. **Enhanced confidence scoring** based on patterns
5. **Working demo** showing RAG-enhanced anomaly detection

This gives you a **functional POC** that demonstrates the core RAG concepts without the complexity of vector databases, embeddings, or complex infrastructure. You can always upgrade to the full implementation later!

Would you like me to help you implement any of these quick options?