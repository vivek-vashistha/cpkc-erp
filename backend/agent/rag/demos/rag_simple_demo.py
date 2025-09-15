# backend/agent/rag_simple_demo.py
"""
Simple RAG demo that works with your existing agent
This demonstrates RAG capabilities without modifying the existing agent
"""

import os
import json
import sys
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from rag.core.quick_rag import setup_quick_knowledge, QuickRAG
from rag.learning.simple_learning import SimpleLearning

def simulate_rag_enhanced_analysis(waybill_id: str = "WB3005") -> Dict[str, Any]:
    """Simulate RAG-enhanced analysis workflow"""
    
    print(f"🔍 RAG-Enhanced Analysis for {waybill_id}")
    print("=" * 50)
    
    # Initialize RAG components
    rag = setup_quick_knowledge()
    learning = SimpleLearning()
    
    # Step 1: Search for relevant patterns
    print("\n1. 🔎 Searching for relevant anomaly patterns...")
    patterns = rag.search_knowledge("missing event sequence", "patterns")
    rules = rag.search_knowledge("event sequence", "rules")
    
    print(f"   Found {len(patterns)} patterns and {len(rules)} rules")
    for pattern in patterns:
        print(f"   📋 Pattern: {pattern['title']}")
        print(f"      Success Rate: {pattern['metadata'].get('success_rate', 'N/A')}")
    
    # Step 2: Get learned insights
    print("\n2. 🧠 Getting learned insights...")
    insights = learning.get_anomaly_insights("MISSING_STEP")
    print(f"   Confidence: {insights['confidence']:.2f}")
    print(f"   Suggested Fix: {insights['suggested_fix']}")
    print(f"   Frequency: {insights['frequency']} ({insights['frequency_percentage']:.1f}%)")
    
    # Step 3: Get historical cases
    print("\n3. 📚 Checking historical cases...")
    cases = rag.search_knowledge("resolution", "cases")
    print(f"   Found {len(cases)} historical cases")
    for case in cases:
        print(f"   📖 Case: {case['title']}")
        print(f"      Outcome: {case['metadata'].get('outcome', 'unknown')}")
    
    # Step 4: Simulate enhanced anomaly detection
    print("\n4. 🎯 RAG-Enhanced Anomaly Detection Result:")
    
    # Simulate finding anomalies with RAG enhancement
    enhanced_anomalies = []
    
    # Example: Missing Step anomaly
    missing_step_anomaly = {
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
        "knowledge_sources": [p['id'] for p in patterns[:2]],
        "enhancement_details": {
            "pattern_matches": len(patterns),
            "historical_cases": len(cases),
            "learning_confidence": insights['confidence'],
            "applied_rules": [r['title'] for r in rules[:2]]
        }
    }
    
    enhanced_anomalies.append(missing_step_anomaly)
    
    # Example: ID Inconsistency anomaly
    if len(patterns) > 1:
        id_anomaly = {
            "waybill_id": waybill_id,
            "car_id": "CPKC-1001",
            "csn_id": "CSN-CPKC-1001-202509-A",
            "type": "CARID_INCONSISTENT",
            "suggested_fix": {
                "action": "SET_CARID",
                "car_id": "CPKC-1001",
                "reasoning": "Use CarId from 'Created' event (highest priority)"
            },
            "confidence": 0.87,  # From pattern metadata
            "status": "NEW",
            "rag_enhanced": True,
            "knowledge_sources": [p['id'] for p in patterns if 'ID' in p['title']],
            "enhancement_details": {
                "pattern_matches": len([p for p in patterns if 'ID' in p['title']]),
                "applied_rule": "Equipment ID Consistency Rules"
            }
        }
        enhanced_anomalies.append(id_anomaly)
    
    result = {
        "waybill_id": waybill_id,
        "anomalies": enhanced_anomalies,
        "analysis_metadata": {
            "rag_enhanced": True,
            "patterns_consulted": len(patterns),
            "rules_applied": len(rules),
            "historical_cases": len(cases),
            "learning_insights": insights,
            "knowledge_base_stats": rag.get_knowledge_stats()
        }
    }
    
    print(json.dumps(result, indent=2))
    
    return result

def compare_analysis_methods(waybill_id: str = "WB3005"):
    """Compare traditional vs RAG-enhanced analysis"""
    
    print(f"\n🔄 Analysis Comparison for {waybill_id}")
    print("=" * 50)
    
    # Traditional analysis (simulated)
    traditional_result = {
        "waybill_id": waybill_id,
        "anomalies": [
            {
                "waybill_id": waybill_id,
                "type": "MISSING_STEP",
                "confidence": 0.75,  # Static confidence
                "suggested_fix": "INSERT_EVENT",
                "rag_enhanced": False
            }
        ],
        "analysis_metadata": {
            "rag_enhanced": False,
            "static_rules_only": True
        }
    }
    
    # RAG-enhanced analysis
    rag_result = simulate_rag_enhanced_analysis(waybill_id)
    
    print("\n📊 Comparison Summary:")
    print("-" * 30)
    print(f"Traditional Analysis:")
    print(f"  - Anomalies found: {len(traditional_result['anomalies'])}")
    print(f"  - Average confidence: 0.75")
    print(f"  - Fix specificity: Basic")
    print(f"  - Historical context: None")
    
    print(f"\nRAG-Enhanced Analysis:")
    print(f"  - Anomalies found: {len(rag_result['anomalies'])}")
    avg_confidence = sum(a['confidence'] for a in rag_result['anomalies']) / len(rag_result['anomalies'])
    print(f"  - Average confidence: {avg_confidence:.2f}")
    print(f"  - Fix specificity: Detailed with timestamps")
    print(f"  - Historical context: {rag_result['analysis_metadata']['historical_cases']} cases")
    print(f"  - Patterns consulted: {rag_result['analysis_metadata']['patterns_consulted']}")
    print(f"  - Rules applied: {rag_result['analysis_metadata']['rules_applied']}")
    
    print(f"\n✨ Improvements with RAG:")
    print(f"  - Confidence increase: {avg_confidence - 0.75:.2f}")
    print(f"  - More specific fixes with timestamps")
    print(f"  - Historical context and proven strategies")
    print(f"  - Learning from past successful resolutions")
    print(f"  - Dynamic knowledge base with {rag_result['analysis_metadata']['knowledge_base_stats']['total_patterns']} patterns")

def demo_knowledge_management():
    """Demo knowledge base management capabilities"""
    
    print(f"\n📚 Knowledge Base Management Demo")
    print("=" * 50)
    
    rag = QuickRAG()
    
    # Show current stats
    stats = rag.get_knowledge_stats()
    print(f"Current knowledge base:")
    print(f"  - Patterns: {stats['total_patterns']}")
    print(f"  - Rules: {stats['total_rules']}")
    print(f"  - Cases: {stats['total_cases']}")
    
    # Add new knowledge
    print(f"\n➕ Adding new knowledge...")
    new_pattern_id = rag.add_knowledge(
        "patterns",
        "Weather Delay Pattern",
        "Pattern: Events delayed due to weather conditions. "
        "Common in winter months. Resolution: Adjust timestamps based on weather reports. "
        "Success rate: 88%",
        {"success_rate": 0.88, "frequency": "seasonal", "season": "winter"}
    )
    print(f"   Added pattern: {new_pattern_id}")
    
    # Search for new knowledge
    print(f"\n🔍 Searching for weather-related patterns...")
    weather_patterns = rag.search_knowledge("weather", "patterns")
    print(f"   Found {len(weather_patterns)} weather-related patterns")
    for pattern in weather_patterns:
        print(f"   - {pattern['title']} (score: {pattern['relevance_score']})")
    
    # Updated stats
    updated_stats = rag.get_knowledge_stats()
    print(f"\n📈 Updated knowledge base:")
    print(f"  - Patterns: {updated_stats['total_patterns']} (+1)")
    print(f"  - Rules: {updated_stats['total_rules']}")
    print(f"  - Cases: {updated_stats['total_cases']}")

def main():
    """Run the complete RAG demo"""
    
    print("🚀 RAG-Enhanced Anomaly Detection POC")
    print("=" * 60)
    print("This demo shows how RAG enhances anomaly detection with:")
    print("• Knowledge retrieval from patterns and rules")
    print("• Learning from historical anomalies")
    print("• Enhanced confidence scoring")
    print("• Specific resolution suggestions")
    print("• Dynamic knowledge base management")
    print("=" * 60)
    
    try:
        # Run RAG-enhanced analysis
        rag_result = simulate_rag_enhanced_analysis("WB3005")
        
        # Compare with traditional analysis
        compare_analysis_methods("WB3005")
        
        # Demo knowledge management
        demo_knowledge_management()
        
        print(f"\n✅ RAG POC Demo completed successfully!")
        print(f"\n🎯 Key Takeaways:")
        print(f"1. RAG provides context-aware anomaly detection")
        print(f"2. Historical patterns improve confidence scores")
        print(f"3. Specific fixes with timestamps and reasoning")
        print(f"4. Dynamic knowledge base grows with experience")
        print(f"5. Easy integration with existing systems")
        
        print(f"\n📋 Next Steps:")
        print(f"1. Integrate with your existing agent")
        print(f"2. Add more domain-specific knowledge")
        print(f"3. Test with real waybill data")
        print(f"4. Monitor and improve based on results")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
