# backend/agent/simple_learning.py
import json
import os
from collections import Counter
from typing import Dict, List, Any

class SimpleLearning:
    def __init__(self, anomalies_file: str = None):
        # Try to find the anomalies file in different locations
        if anomalies_file is None:
            possible_paths = [
                "cpkc-erp-portal/data/anomalies.json",
                "../cpkc-erp-portal/data/anomalies.json",
                "../../cpkc-erp-portal/data/anomalies.json",
                "/Users/vivekvashistha/Projects/Clients/Turing/Projects/CPKC_Projects/cpkc-erp/cpkc-erp-portal/data/anomalies.json"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    anomalies_file = path
                    break
        
        self.anomalies_file = anomalies_file
        self.learned_patterns = self._analyze_historical_anomalies()
    
    def _analyze_historical_anomalies(self) -> Dict[str, Any]:
        """Analyze existing anomalies to learn patterns"""
        try:
            if not self.anomalies_file or not os.path.exists(self.anomalies_file):
                print(f"Warning: Anomalies file not found at {self.anomalies_file}")
                return self._get_default_patterns()
            
            with open(self.anomalies_file, 'r') as f:
                anomalies = json.load(f)
            
            if not anomalies:
                return self._get_default_patterns()
            
            # Count anomaly types
            type_counts = Counter(a['type'] for a in anomalies)
            
            # Count resolution success rates
            resolved = [a for a in anomalies if a['status'] == 'RESOLVED']
            resolution_success = len(resolved) / len(anomalies) if anomalies else 0
            
            # Find common fix patterns
            fix_patterns = Counter(a['suggested_fix'] for a in anomalies)
            
            # Analyze confidence patterns
            confidence_scores = [a.get('confidence', 0.5) for a in anomalies]
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
            
            # Analyze by waybill patterns
            waybill_patterns = Counter(a.get('waybill_id', 'unknown')[:3] for a in anomalies)  # First 3 chars
            
            return {
                "common_types": dict(type_counts.most_common(10)),
                "resolution_success_rate": resolution_success,
                "common_fixes": dict(fix_patterns.most_common(10)),
                "total_anomalies": len(anomalies),
                "avg_confidence": avg_confidence,
                "waybill_patterns": dict(waybill_patterns.most_common(5)),
                "resolved_count": len(resolved),
                "new_count": len([a for a in anomalies if a['status'] == 'NEW']),
                "ignored_count": len([a for a in anomalies if a['status'] == 'IGNORED'])
            }
        except Exception as e:
            print(f"Error analyzing anomalies: {e}")
            return self._get_default_patterns()
    
    def _get_default_patterns(self) -> Dict[str, Any]:
        """Return default patterns when no data is available"""
        return {
            "common_types": {
                "MISSING_STEP": 3,
                "SEQUENCE_ERROR": 2,
                "CARID_INCONSISTENT": 1
            },
            "resolution_success_rate": 0.75,
            "common_fixes": {
                "INSERT_EVENT": 2,
                "REORDER_EVENTS": 1,
                "SET_CARID": 1
            },
            "total_anomalies": 6,
            "avg_confidence": 0.85,
            "waybill_patterns": {"WB3": 3, "WB4": 3},
            "resolved_count": 2,
            "new_count": 3,
            "ignored_count": 1
        }
    
    def get_confidence_for_anomaly(self, anomaly_type: str) -> float:
        """Get confidence score based on historical frequency and success rate"""
        if anomaly_type in self.learned_patterns["common_types"]:
            frequency = self.learned_patterns["common_types"][anomaly_type]
            total = self.learned_patterns["total_anomalies"]
            
            # Base confidence from frequency
            frequency_confidence = min(0.95, 0.7 + (frequency / total) * 0.25)
            
            # Adjust based on resolution success rate
            success_rate = self.learned_patterns["resolution_success_rate"]
            adjusted_confidence = frequency_confidence * (0.8 + 0.2 * success_rate)
            
            return min(0.95, adjusted_confidence)
        
        # For new anomaly types, use average confidence with slight penalty
        return max(0.6, self.learned_patterns["avg_confidence"] - 0.1)
    
    def get_suggested_fix(self, anomaly_type: str) -> str:
        """Get most common fix for anomaly type"""
        # Map anomaly types to common fixes
        type_to_fix_mapping = {
            "MISSING_STEP": "INSERT_EVENT",
            "SEQUENCE_ERROR": "REORDER_EVENTS", 
            "CARID_INCONSISTENT": "SET_CARID",
            "CSNID_INCONSISTENT": "SET_CSNID",
            "TERMINAL_CONFLICT": "REVIEW_TERMINAL_STATE",
            "MULTI_DELIVERED": "MERGE_DUPLICATE_EVENTS",
            "POST_TERMINAL_ACTIVITY": "TRIM_POST_TERMINAL_EVENTS",
            "UNKNOWN_EVENT_TYPE": "MAP_EVENT_TYPE"
        }
        
        # First try direct mapping
        if anomaly_type in type_to_fix_mapping:
            return type_to_fix_mapping[anomaly_type]
        
        # Then try to find in common fixes
        common_fixes = self.learned_patterns["common_fixes"]
        if common_fixes:
            return list(common_fixes.keys())[0]
        
        return "Manual review required"
    
    def get_anomaly_insights(self, anomaly_type: str) -> Dict[str, Any]:
        """Get comprehensive insights about an anomaly type"""
        confidence = self.get_confidence_for_anomaly(anomaly_type)
        suggested_fix = self.get_suggested_fix(anomaly_type)
        
        # Get frequency info
        frequency = self.learned_patterns["common_types"].get(anomaly_type, 0)
        total = self.learned_patterns["total_anomalies"]
        frequency_pct = (frequency / total * 100) if total > 0 else 0
        
        return {
            "anomaly_type": anomaly_type,
            "confidence": confidence,
            "suggested_fix": suggested_fix,
            "frequency": frequency,
            "frequency_percentage": frequency_pct,
            "is_common": frequency >= 2,
            "historical_patterns": self.learned_patterns,
            "recommendation": self._get_recommendation(anomaly_type, confidence, frequency)
        }
    
    def _get_recommendation(self, anomaly_type: str, confidence: float, frequency: int) -> str:
        """Get recommendation based on anomaly analysis"""
        if confidence > 0.9 and frequency >= 3:
            return "High confidence - this is a well-known pattern with proven resolution"
        elif confidence > 0.8:
            return "Good confidence - similar patterns have been resolved successfully"
        elif frequency >= 2:
            return "Moderate confidence - pattern seen before but needs validation"
        else:
            return "Low confidence - new or rare pattern, manual review recommended"
    
    def update_learning_from_resolution(self, anomaly_id: str, anomaly_type: str, 
                                      resolution_success: bool, effectiveness_score: float):
        """Update learning patterns based on new resolution feedback"""
        # This would update the internal patterns
        # For now, we'll just log the feedback
        print(f"Learning update: {anomaly_type} resolution {'successful' if resolution_success else 'failed'} "
              f"with effectiveness {effectiveness_score}")

# Add to your agent
from langchain_core.tools import tool

@tool
def get_learned_insights(anomaly_type: str) -> Dict[str, Any]:
    """Get learned insights about anomaly patterns from historical data"""
    learning = SimpleLearning()
    return learning.get_anomaly_insights(anomaly_type)

@tool
def get_learning_stats() -> Dict[str, Any]:
    """Get overall learning statistics"""
    learning = SimpleLearning()
    return learning.learned_patterns

if __name__ == "__main__":
    # Test the learning system
    print("=== Testing Simple Learning System ===")
    
    learning = SimpleLearning()
    
    # Test with different anomaly types
    test_types = ["MISSING_STEP", "SEQUENCE_ERROR", "CARID_INCONSISTENT", "NEW_TYPE"]
    
    for anomaly_type in test_types:
        insights = learning.get_anomaly_insights(anomaly_type)
        print(f"\n{anomaly_type}:")
        print(f"  Confidence: {insights['confidence']:.2f}")
        print(f"  Suggested Fix: {insights['suggested_fix']}")
        print(f"  Frequency: {insights['frequency']} ({insights['frequency_percentage']:.1f}%)")
        print(f"  Recommendation: {insights['recommendation']}")
    
    print(f"\nOverall Stats: {learning.learned_patterns}")
