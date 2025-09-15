# RAG Main Entry Point
"""
Main entry point for RAG-enhanced anomaly detection system
"""

import sys
import os
from typing import Dict, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from rag.core.quick_rag import setup_quick_knowledge, QuickRAG
from rag.learning.simple_learning import SimpleLearning
from rag.tools.rag_tools import RAG_TOOLS

def main():
    """Main entry point for RAG system"""
    print("🚀 RAG-Enhanced Anomaly Detection System")
    print("=" * 50)
    
    # Initialize RAG components
    print("Initializing RAG components...")
    rag = setup_quick_knowledge()
    learning = SimpleLearning()
    
    # Show system status
    stats = rag.get_knowledge_stats()
    print(f"Knowledge Base Status:")
    print(f"  - Patterns: {stats['total_patterns']}")
    print(f"  - Rules: {stats['total_rules']}")
    print(f"  - Cases: {stats['total_cases']}")
    
    learning_stats = learning.learned_patterns
    print(f"Learning Status:")
    print(f"  - Total Anomalies Analyzed: {learning_stats['total_anomalies']}")
    print(f"  - Resolution Success Rate: {learning_stats['resolution_success_rate']:.2%}")
    print(f"  - Average Confidence: {learning_stats['avg_confidence']:.2f}")
    
    print(f"\nAvailable RAG Tools: {len(RAG_TOOLS)}")
    for tool_name in RAG_TOOLS.keys():
        print(f"  - {tool_name}")
    
    print(f"\n✅ RAG System Ready!")
    print(f"Run demos:")
    print(f"  python rag/demos/rag_simple_demo.py")
    print(f"  python rag/demos/demo_rag.py")

if __name__ == "__main__":
    main()
