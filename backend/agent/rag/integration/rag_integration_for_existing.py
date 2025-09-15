# RAG Integration for Existing CPKC Agent
"""
Seamless integration of RAG capabilities into the existing agent_waybill_agentic_loggs.py
This maintains compatibility with the current system while adding RAG enhancements.
"""

import os
import sys
import json
from typing import Dict, Any, Optional
from datetime import datetime
import random
import string

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from rag.core.quick_rag import QuickRAG, setup_quick_knowledge
from rag.learning.simple_learning import SimpleLearning
from rag.tools.rag_tools import RAG_TOOLS

def generate_anomaly_id() -> str:
    """Generate anomaly ID in the format: anomaly_{epochMillis}_{10-char lowercase a-z0-9}"""
    epoch_millis = int(datetime.now().timestamp() * 1000)
    random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"anomaly_{epoch_millis}_{random_chars}"

def get_current_timestamp() -> str:
    """Get current UTC timestamp in ISO 8601 format with Z suffix"""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

class RAGEnhancedAnomalyDetector:
    """
    RAG-enhanced anomaly detector that integrates with existing system
    """
    
    def __init__(self):
        self.rag = setup_quick_knowledge()
        self.learning = SimpleLearning()
        self.anomaly_types = [
            "SEQUENCE_ERROR", "MISSING_STEP", "NEGATIVE_DURATION", "TERMINAL_CONFLICT",
            "MULTI_DELIVERED", "POST_TERMINAL_ACTIVITY", "UNKNOWN_EVENT_TYPE",
            "CARID_INCONSISTENT", "CARID_MISSING", "CSNID_INCONSISTENT", "CSNID_MISSING"
        ]
        
    def enhance_anomaly_detection(self, waybill_id: str, events_data: Dict[str, Any], 
                                waybill_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Enhance anomaly detection using RAG capabilities
        Returns enhanced anomalies that match the existing schema
        """
        
        # Search for relevant patterns and rules
        patterns = self.rag.search_knowledge("anomaly detection", "patterns")
        rules = self.rag.search_knowledge("event sequence validation", "rules")
        historical_cases = self.rag.search_knowledge(waybill_id[:3], "cases")  # Search by waybill prefix
        
        # Get learned insights for common anomaly types
        learned_insights = {}
        for anomaly_type in self.anomaly_types:
            insights = self.learning.get_anomaly_insights(anomaly_type)
            learned_insights[anomaly_type] = insights
        
        return {
            "rag_enhanced": True,
            "patterns_consulted": len(patterns),
            "rules_applied": len(rules),
            "historical_cases": len(historical_cases),
            "learned_insights": learned_insights,
            "knowledge_sources": {
                "patterns": [p['id'] for p in patterns],
                "rules": [r['id'] for r in rules],
                "cases": [c['id'] for c in historical_cases]
            }
        }
    
    def enhance_anomaly_confidence(self, anomaly_type: str, base_confidence: float) -> float:
        """
        Enhance confidence score using RAG insights
        """
        insights = self.learning.get_anomaly_insights(anomaly_type)
        
        # Boost confidence based on historical frequency and success
        if insights['is_common']:
            confidence_boost = 0.1
        else:
            confidence_boost = 0.05
            
        # Adjust based on resolution success rate
        success_rate = insights['historical_patterns']['resolution_success_rate']
        success_boost = success_rate * 0.1
        
        enhanced_confidence = min(1.0, base_confidence + confidence_boost + success_boost)
        return enhanced_confidence
    
    def enhance_suggested_fix(self, anomaly_type: str, base_fix: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance suggested fix using RAG knowledge
        """
        # Get learned insights
        insights = self.learning.get_anomaly_insights(anomaly_type)
        
        # Search for relevant patterns
        patterns = self.rag.search_knowledge(anomaly_type.lower(), "patterns")
        
        # Enhance the fix with RAG knowledge
        enhanced_fix = base_fix.copy()
        
        # Add rationale based on historical patterns
        if patterns:
            pattern = patterns[0]  # Use the most relevant pattern
            success_rate = pattern['metadata'].get('success_rate', 0.8)
            
            # Enhance rationale with historical context
            if 'rationale' in enhanced_fix.get('actions', [{}])[0]:
                original_rationale = enhanced_fix['actions'][0]['rationale']
                enhanced_fix['actions'][0]['rationale'] = (
                    f"{original_rationale} "
                    f"Historical data shows {success_rate:.0%} success rate for similar cases. "
                    f"Pattern: {pattern['title']}"
                )
        
        return enhanced_fix
    
    def get_rag_enhanced_anomaly(self, waybill_id: str, anomaly_type: str, 
                                car_id: str = None, csn_id: str = None,
                                base_confidence: float = 0.8, 
                                base_details: str = "",
                                base_suggested_fix: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a RAG-enhanced anomaly that matches the existing schema
        """
        
        # Enhance confidence using RAG
        enhanced_confidence = self.enhance_anomaly_confidence(anomaly_type, base_confidence)
        
        # Enhance suggested fix using RAG
        enhanced_fix = self.enhance_suggested_fix(anomaly_type, base_suggested_fix or {})
        
        # Determine RPA status based on anomaly type and RAG insights
        rpa_status = self._determine_rpa_status(anomaly_type, enhanced_confidence)
        
        # Create anomaly matching existing schema
        anomaly = {
            "id": generate_anomaly_id(),
            "waybill_id": waybill_id,
            "car_id": car_id,
            "csn_id": csn_id,
            "type": anomaly_type,
            "confidence": enhanced_confidence,
            "suggested_fix": enhanced_fix,
            "status": "NEW",
            "rpa_status": rpa_status,
            "created_ts": get_current_timestamp(),
            "updated_ts": get_current_timestamp(),
            "details": self._enhance_details(base_details, anomaly_type),
            "needs_confirmation": enhanced_fix is not None and len(enhanced_fix.get('actions', [])) > 0
        }
        
        return anomaly
    
    def _determine_rpa_status(self, anomaly_type: str, confidence: float) -> str:
        """
        Determine RPA status based on anomaly type and confidence
        """
        auto_fix_types = ["MISSING_STEP", "MULTI_DELIVERED", "SEQUENCE_ERROR"]
        manual_review_types = [
            "NEGATIVE_DURATION", "TERMINAL_CONFLICT", "POST_TERMINAL_ACTIVITY",
            "UNKNOWN_EVENT_TYPE", "CARID_INCONSISTENT", "CARID_MISSING",
            "CSNID_INCONSISTENT", "CSNID_MISSING"
        ]
        
        if anomaly_type in auto_fix_types and confidence > 0.8:
            return "Auto Fix"
        elif anomaly_type in manual_review_types:
            return "Manual Review Required"
        else:
            return "Needs Data"
    
    def _enhance_details(self, base_details: str, anomaly_type: str) -> str:
        """
        Enhance details with RAG context
        """
        insights = self.learning.get_anomaly_insights(anomaly_type)
        
        if insights['is_common']:
            frequency_info = f" This is a common pattern (seen {insights['frequency']} times, {insights['frequency_percentage']:.1f}% of cases)."
        else:
            frequency_info = " This is a less common pattern that may require special attention."
        
        return base_details + frequency_info

# RAG Tools for Integration
def get_rag_enhanced_anomaly_detector():
    """Get RAG-enhanced anomaly detector instance"""
    return RAGEnhancedAnomalyDetector()

def enhance_anomalies_with_rag(anomalies: list, waybill_id: str) -> list:
    """
    Enhance a list of anomalies with RAG capabilities
    """
    detector = get_rag_enhanced_anomaly_detector()
    enhanced_anomalies = []
    
    for anomaly in anomalies:
        # Enhance existing anomaly
        enhanced_anomaly = anomaly.copy()
        
        # Enhance confidence
        if 'type' in anomaly and 'confidence' in anomaly:
            enhanced_anomaly['confidence'] = detector.enhance_anomaly_confidence(
                anomaly['type'], anomaly['confidence']
            )
        
        # Enhance suggested fix
        if 'suggested_fix' in anomaly:
            enhanced_anomaly['suggested_fix'] = detector.enhance_suggested_fix(
                anomaly['type'], anomaly['suggested_fix']
            )
        
        # Enhance details
        if 'details' in anomaly:
            enhanced_anomaly['details'] = detector._enhance_details(
                anomaly['details'], anomaly['type']
            )
        
        # Add RAG metadata
        enhanced_anomaly['rag_enhanced'] = True
        enhanced_anomalies.append(enhanced_anomaly)
    
    return enhanced_anomalies

# Integration helper functions
def get_rag_context_for_waybill(waybill_id: str) -> Dict[str, Any]:
    """
    Get RAG context for a waybill analysis
    """
    rag = setup_quick_knowledge()
    learning = SimpleLearning()
    
    # Search for relevant knowledge
    patterns = rag.search_knowledge("waybill analysis", "patterns")
    rules = rag.search_knowledge("event sequence", "rules")
    cases = rag.search_knowledge(waybill_id[:3], "cases")
    
    return {
        "patterns": patterns,
        "rules": rules,
        "historical_cases": cases,
        "learning_stats": learning.learned_patterns
    }

def add_resolution_feedback_to_rag(anomaly_id: str, anomaly_type: str, 
                                 resolution_success: bool, effectiveness_score: float):
    """
    Add resolution feedback to RAG system for learning
    """
    from rag.tools.rag_tools import add_resolution_feedback
    
    result = add_resolution_feedback.invoke({
        "anomaly_id": anomaly_id,
        "anomaly_type": anomaly_type,
        "resolution_success": resolution_success,
        "resolution_time_minutes": 0,  # Could be passed as parameter
        "effectiveness_score": effectiveness_score
    })
    
    return result

if __name__ == "__main__":
    # Test the integration
    detector = RAGEnhancedAnomalyDetector()
    
    # Test anomaly creation
    test_anomaly = detector.get_rag_enhanced_anomaly(
        waybill_id="WB3005",
        anomaly_type="MISSING_STEP",
        car_id="CPKC-1001",
        csn_id="CSN-CPKC-1001-202509-A",
        base_confidence=0.8,
        base_details="Missing 'Closed' event after 'Delivered'",
        base_suggested_fix={
            "actions": [
                {
                    "name": "INSERT_EVENT",
                    "args": [{"key": "event_type", "value": "Closed"}],
                    "rationale": "Insert missing 'Closed' event to complete the sequence"
                }
            ]
        }
    )
    
    print("RAG-Enhanced Anomaly:")
    print(json.dumps(test_anomaly, indent=2))
