# backend/agent/demo_rag.py
"""
Demo script for RAG-enhanced anomaly detection
This script demonstrates the capabilities of the RAG system
"""

import os
import json
from typing import Dict, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from rag.core.quick_rag import setup_quick_knowledge, QuickRAG
from rag.learning.simple_learning import SimpleLearning, get_learned_insights
from rag.tools.rag_tools import search_anomaly_patterns, get_historical_cases

def demo_rag_components():
    """Demo individual RAG components"""
    print("=== RAG Components Demo ===\n")
    
    # 1. Test QuickRAG
    print("1. Testing QuickRAG Knowledge Base:")
    rag = setup_quick_knowledge()
    stats = rag.get_knowledge_stats()
    print(f"   Knowledge base stats: {stats}")
    
    # Test search functionality
    patterns = rag.search_knowledge("missing event", "patterns")
    print(f"   Found {len(patterns)} patterns for 'missing event'")
    for pattern in patterns:
        print(f"   - {pattern['title']} (score: {pattern['relevance_score']})")
    
    print()
    
    # 2. Test Simple Learning
    print("2. Testing Simple Learning System:")
    learning = SimpleLearning()
    insights = learning.get_anomaly_insights("MISSING_STEP")
    print(f"   MISSING_STEP insights:")
    print(f"   - Confidence: {insights['confidence']:.2f}")
    print(f"   - Suggested Fix: {insights['suggested_fix']}")
    print(f"   - Frequency: {insights['frequency']} ({insights['frequency_percentage']:.1f}%)")
    print(f"   - Recommendation: {insights['recommendation']}")
    
    print()
    
    # 3. Test RAG Tools
    print("3. Testing RAG Tools:")
    pattern_result = search_anomaly_patterns.invoke({"anomaly_type": "sequence missing", "context": "waybill analysis"})
    print(f"   Pattern search: {pattern_result['total_found']} items found")
    
    cases_result = get_historical_cases.invoke({"anomaly_type": "sequence"})
    print(f"   Historical cases: {cases_result['count']} cases found")
    
    learning_result = get_learned_insights.invoke({"anomaly_type": "SEQUENCE_ERROR"})
    print(f"   Learning insights: confidence {learning_result['confidence']:.2f}")
    
    print()

def demo_rag_enhanced_analysis():
    """Demo RAG-enhanced analysis workflow"""
    print("=== RAG-Enhanced Analysis Demo ===\n")
    
    # Simulate waybill analysis workflow
    waybill_id = "WB3005"
    print(f"Analyzing waybill {waybill_id} with RAG enhancement...\n")
    
    # Step 1: Search for relevant patterns
    print("Step 1: Searching for relevant anomaly patterns...")
    patterns = search_anomaly_patterns.invoke({"anomaly_type": "sequence missing event", "context": "waybill analysis"})
    print(f"   Found {patterns['total_found']} relevant items")
    for pattern in patterns['patterns']:
        print(f"   - Pattern: {pattern['title']}")
        print(f"     Success Rate: {pattern['metadata'].get('success_rate', 'N/A')}")
    
    print()
    
    # Step 2: Get learned insights
    print("Step 2: Getting learned insights...")
    insights = get_learned_insights.invoke({"anomaly_type": "MISSING_STEP"})
    print(f"   Confidence: {insights['confidence']:.2f}")
    print(f"   Suggested Fix: {insights['suggested_fix']}")
    print(f"   Is Common Pattern: {insights['is_common']}")
    
    print()
    
    # Step 3: Get historical cases
    print("Step 3: Checking historical cases...")
    cases = get_historical_cases.invoke({"anomaly_type": "missing"})
    print(f"   Found {cases['count']} historical cases")
    for case in cases['cases']:
        print(f"   - {case['title']}")
        print(f"     Outcome: {case['metadata'].get('outcome', 'unknown')}")
    
    print()
    
    # Step 4: Simulate enhanced anomaly detection
    print("Step 4: RAG-Enhanced Anomaly Detection Result:")
    enhanced_anomaly = {
        "waybill_id": waybill_id,
        "car_id": "CPKC-1001",
        "csn_id": "CSN-CPKC-1001-202509-A",
        "type": "MISSING_STEP",
        "suggested_fix": {
            "action": "INSERT_EVENT",
            "event_type": "At Border",
            "ts_hint": "2025-09-09T09:55:00"
        },
        "confidence": insights['confidence'],  # Enhanced by learning
        "status": "NEW",
        "rag_enhanced": True,
        "knowledge_sources": ["pattern_001", "case_002"],
        "enhancement_details": {
            "pattern_matches": len(patterns['patterns']),
            "historical_cases": cases['count'],
            "learning_confidence": insights['confidence']
        }
    }
    
    print(json.dumps(enhanced_anomaly, indent=2))
    
    return enhanced_anomaly

def demo_knowledge_base_management():
    """Demo knowledge base management capabilities"""
    print("\n=== Knowledge Base Management Demo ===\n")
    
    rag = QuickRAG()
    
    # Add new knowledge
    print("1. Adding new knowledge...")
    new_pattern_id = rag.add_knowledge(
        "patterns",
        "New Pattern: Duplicate Events",
        "Pattern: Multiple events of same type with identical timestamps. "
        "Resolution: Merge duplicate events, keep most complete record. "
        "Success rate: 92%",
        {"success_rate": 0.92, "frequency": "medium"}
    )
    print(f"   Added pattern with ID: {new_pattern_id}")
    
    # Search for new knowledge
    print("\n2. Searching for new knowledge...")
    results = rag.search_knowledge("duplicate", "patterns")
    print(f"   Found {len(results)} results for 'duplicate'")
    for result in results:
        print(f"   - {result['title']} (score: {result['relevance_score']})")
    
    # Get updated stats
    print("\n3. Updated knowledge base stats:")
    stats = rag.get_knowledge_stats()
    print(f"   {stats}")

def compare_with_without_rag():
    """Compare analysis with and without RAG"""
    print("\n=== RAG vs Non-RAG Comparison ===\n")
    
    # Simulate non-RAG analysis
    print("Without RAG:")
    non_rag_anomaly = {
        "waybill_id": "WB3005",
        "type": "MISSING_STEP",
        "confidence": 0.75,  # Static confidence
        "suggested_fix": "INSERT_EVENT",
        "rag_enhanced": False
    }
    print(json.dumps(non_rag_anomaly, indent=2))
    
    print("\nWith RAG Enhancement:")
    rag_anomaly = {
        "waybill_id": "WB3005",
        "type": "MISSING_STEP",
        "confidence": 0.91,  # Enhanced by historical data
        "suggested_fix": {
            "action": "INSERT_EVENT",
            "event_type": "At Border",
            "ts_hint": "2025-09-09T09:55:00"
        },
        "rag_enhanced": True,
        "knowledge_sources": ["pattern_001", "case_002"],
        "enhancement_benefits": [
            "Higher confidence based on historical success",
            "Specific fix details from proven cases",
            "Timestamp hints from similar resolutions",
            "Reference to successful historical patterns"
        ]
    }
    print(json.dumps(rag_anomaly, indent=2))
    
    print("\nImprovements with RAG:")
    print("- Confidence increased from 0.75 to 0.91")
    print("- More specific suggested fixes")
    print("- Historical context and proven strategies")
    print("- Learning from past successful resolutions")

def main():
    """Run all demos"""
    print("🚀 RAG-Enhanced Anomaly Detection POC Demo\n")
    print("=" * 60)
    
    try:
        # Run individual component demos
        demo_rag_components()
        
        # Run enhanced analysis demo
        demo_rag_enhanced_analysis()
        
        # Run knowledge base management demo
        demo_knowledge_base_management()
        
        # Run comparison demo
        compare_with_without_rag()
        
        print("\n" + "=" * 60)
        print("✅ RAG POC Demo completed successfully!")
        print("\nKey Benefits Demonstrated:")
        print("1. Knowledge retrieval from patterns and rules")
        print("2. Learning from historical anomalies")
        print("3. Enhanced confidence scoring")
        print("4. Specific resolution suggestions")
        print("5. Dynamic knowledge base management")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
