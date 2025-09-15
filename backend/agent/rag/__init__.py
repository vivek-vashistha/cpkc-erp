# RAG Package for CPKC Anomaly Detection
"""
RAG (Retrieval-Augmented Generation) system for enhanced anomaly detection
in CPKC freight forwarding operations.

This package provides:
- Knowledge base management
- Pattern learning from historical data
- RAG tools for knowledge retrieval
- Enhanced anomaly detection capabilities
"""

__version__ = "1.0.0"
__author__ = "CPKC ERP Team"

# Core imports
from .core.quick_rag import QuickRAG, setup_quick_knowledge
from .learning.simple_learning import SimpleLearning, get_learned_insights, get_learning_stats
from .tools.rag_tools import RAG_TOOLS

__all__ = [
    "QuickRAG",
    "setup_quick_knowledge", 
    "SimpleLearning",
    "get_learned_insights",
    "get_learning_stats",
    "RAG_TOOLS"
]
