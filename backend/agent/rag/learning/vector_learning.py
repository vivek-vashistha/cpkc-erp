# Vector-based learning system for anomaly detection
import json
import os
from collections import Counter
from typing import Dict, List, Any, Optional
from datetime import datetime
import numpy as np
from ..core.vector_rag import VectorRAG

class VectorLearning:
    """
    Advanced learning system that analyzes historical anomalies and provides insights
    using vector-based similarity and pattern recognition
    """
    
    def __init__(self, 
                 anomalies_file: str = "cpkc-erp-portal/data/anomalies.json",
                 vector_rag: Optional[VectorRAG] = None):
        
        self.anomalies_file = os.path.join(os.path.dirname(__file__), "..", "..", "..", anomalies_file)
        self.vector_rag = vector_rag or VectorRAG()
        self.learned_patterns = self._analyze_historical_anomalies()
    
    def _analyze_historical_anomalies(self) -> Dict[str, Any]:
        """Analyze existing anomalies to learn patterns"""
        try:
            if not os.path.exists(self.anomalies_file):
                print(f"Warning: Anomaly file not found at {self.anomalies_file}. Starting with empty learning.")
                return self._get_empty_patterns()
            
            with open(self.anomalies_file, 'r') as f:
                anomalies = json.load(f)
            
            if not anomalies:
                return self._get_empty_patterns()
            
            # Count anomaly types
            type_counts = Counter(a.get('type', 'UNKNOWN') for a in anomalies)
            
            # Count resolution success rates
            resolved = [a for a in anomalies if a.get('status') == 'RESOLVED']
            new = [a for a in anomalies if a.get('status') == 'NEW']
            ignored = [a for a in anomalies if a.get('status') == 'IGNORED']
            
            resolution_success = len(resolved) / len(anomalies) if anomalies else 0
            
            # Find common fix patterns
            fix_patterns = Counter()
            for a in anomalies:
                suggested_fix = a.get('suggested_fix', {})
                if isinstance(suggested_fix, dict) and 'actions' in suggested_fix:
                    for action in suggested_fix['actions']:
                        if isinstance(action, dict) and 'name' in action:
                            fix_patterns[action['name']] += 1
                elif isinstance(suggested_fix, str):
                    fix_patterns[suggested_fix] += 1
            
            # Average confidence
            confidences = [a.get('confidence', 0.0) for a in anomalies if isinstance(a.get('confidence'), (int, float))]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Waybill patterns (e.g., which waybill prefixes have more anomalies)
            waybill_prefixes = Counter()
            for a in anomalies:
                waybill_id = a.get('waybill_id', '')
                if waybill_id and len(waybill_id) >= 3:
                    waybill_prefixes[waybill_id[:3]] += 1
            
            # Analyze confidence by anomaly type
            confidence_by_type = {}
            for anomaly_type in type_counts.keys():
                type_anomalies = [a for a in anomalies if a.get('type') == anomaly_type]
                type_confidences = [a.get('confidence', 0.0) for a in type_anomalies if isinstance(a.get('confidence'), (int, float))]
                if type_confidences:
                    confidence_by_type[anomaly_type] = {
                        "avg_confidence": sum(type_confidences) / len(type_confidences),
                        "min_confidence": min(type_confidences),
                        "max_confidence": max(type_confidences),
                        "count": len(type_confidences)
                    }
            
            return {
                "common_types": dict(type_counts.most_common(10)),
                "resolution_success_rate": resolution_success,
                "common_fixes": dict(fix_patterns.most_common(10)),
                "total_anomalies": len(anomalies),
                "avg_confidence": avg_confidence,
                "confidence_by_type": confidence_by_type,
                "waybill_patterns": dict(waybill_prefixes.most_common(5)),
                "resolved_count": len(resolved),
                "new_count": len(new),
                "ignored_count": len(ignored),
                "last_analyzed": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error analyzing historical anomalies: {e}")
            return self._get_empty_patterns()
    
    def _get_empty_patterns(self) -> Dict[str, Any]:
        """Return empty patterns structure"""
        return {
            "common_types": {},
            "resolution_success_rate": 0,
            "common_fixes": {},
            "total_anomalies": 0,
            "avg_confidence": 0.0,
            "confidence_by_type": {},
            "waybill_patterns": {},
            "resolved_count": 0,
            "new_count": 0,
            "ignored_count": 0,
            "last_analyzed": datetime.now().isoformat()
        }
    
    def get_anomaly_insights(self, anomaly_type: str) -> Dict[str, Any]:
        """Get comprehensive insights about an anomaly type using vector similarity"""
        
        # Get basic insights from historical data
        basic_insights = self._get_basic_insights(anomaly_type)
        
        # Get vector-based insights
        vector_insights = self._get_vector_insights(anomaly_type)
        
        # Combine insights
        combined_insights = {
            **basic_insights,
            "vector_insights": vector_insights,
            "learning_method": "vector_enhanced"
        }
        
        return combined_insights
    
    def _get_basic_insights(self, anomaly_type: str) -> Dict[str, Any]:
        """Get basic insights from historical data"""
        
        if anomaly_type in self.learned_patterns["common_types"]:
            frequency = self.learned_patterns["common_types"][anomaly_type]
            total = self.learned_patterns["total_anomalies"]
            
            # Base confidence on frequency and historical success
            base_confidence = min(0.95, 0.7 + (frequency / total) * 0.25) if total else 0.7
            
            # Adjust based on overall resolution success rate
            if self.learned_patterns["resolution_success_rate"] > 0.7:
                base_confidence = min(0.99, base_confidence * 1.05)
            
            # Get confidence stats for this type
            confidence_stats = self.learned_patterns["confidence_by_type"].get(anomaly_type, {})
            
            return {
                "anomaly_type": anomaly_type,
                "confidence": base_confidence,
                "frequency": frequency,
                "frequency_percentage": (frequency / total) * 100 if total else 0,
                "is_common": frequency > (total / 10) if total else False,
                "confidence_stats": confidence_stats,
                "suggested_fix": self._get_suggested_fix(anomaly_type),
                "recommendation": self._get_recommendation(base_confidence, frequency, total)
            }
        else:
            return {
                "anomaly_type": anomaly_type,
                "confidence": 0.6,  # Default confidence for new types
                "frequency": 0,
                "frequency_percentage": 0,
                "is_common": False,
                "confidence_stats": {},
                "suggested_fix": "Manual review required",
                "recommendation": "New anomaly type - requires manual review and validation"
            }
    
    def _get_vector_insights(self, anomaly_type: str) -> Dict[str, Any]:
        """Get insights using vector similarity from knowledge base"""
        
        # Search for similar patterns in vector database
        similar_patterns = self.vector_rag.search_knowledge(
            f"{anomaly_type} pattern resolution", 
            category="patterns", 
            top_k=3
        )
        
        # Search for similar cases
        similar_cases = self.vector_rag.search_knowledge(
            f"{anomaly_type} case resolution", 
            category="cases", 
            top_k=3
        )
        
        # Search for relevant rules
        relevant_rules = self.vector_rag.search_knowledge(
            f"{anomaly_type} rules validation", 
            category="rules", 
            top_k=2
        )
        
        # Calculate vector-based confidence
        vector_confidence = self._calculate_vector_confidence(similar_patterns, similar_cases)
        
        # Get vector-based suggested fix
        vector_suggested_fix = self._get_vector_suggested_fix(similar_patterns, similar_cases)
        
        return {
            "similar_patterns": similar_patterns,
            "similar_cases": similar_cases,
            "relevant_rules": relevant_rules,
            "vector_confidence": vector_confidence,
            "vector_suggested_fix": vector_suggested_fix,
            "pattern_matches": len(similar_patterns),
            "case_matches": len(similar_cases),
            "rule_matches": len(relevant_rules)
        }
    
    def _calculate_vector_confidence(self, patterns: List[Dict], cases: List[Dict]) -> float:
        """Calculate confidence based on vector similarity results"""
        
        if not patterns and not cases:
            return 0.6  # Default confidence
        
        # Calculate weighted confidence based on similarity scores
        total_confidence = 0.0
        total_weight = 0.0
        
        # Weight patterns more heavily
        for pattern in patterns:
            similarity = pattern.get("similarity_score", 0.0)
            success_rate = pattern.get("metadata", {}).get("success_rate", 0.8)
            weight = similarity * 2.0  # Higher weight for patterns
            total_confidence += similarity * success_rate * weight
            total_weight += weight
        
        # Weight cases moderately
        for case in cases:
            similarity = case.get("similarity_score", 0.0)
            outcome = case.get("metadata", {}).get("outcome", "success")
            success_rate = 0.9 if outcome == "success" else 0.3
            weight = similarity * 1.0  # Lower weight for cases
            total_confidence += similarity * success_rate * weight
            total_weight += weight
        
        if total_weight > 0:
            return min(0.95, total_confidence / total_weight)
        else:
            return 0.6
    
    def _get_vector_suggested_fix(self, patterns: List[Dict], cases: List[Dict]) -> str:
        """Get suggested fix based on vector similarity results"""
        
        # Look for common fix patterns in similar cases
        fix_suggestions = []
        
        for case in cases:
            metadata = case.get("metadata", {})
            suggested_fix = metadata.get("suggested_fix", "")
            if suggested_fix:
                fix_suggestions.append(suggested_fix)
        
        # Look for resolution strategies in patterns
        for pattern in patterns:
            content = pattern.get("content", "")
            if "resolution" in content.lower():
                # Extract resolution strategy
                if "insert" in content.lower():
                    fix_suggestions.append("INSERT_EVENT")
                elif "reorder" in content.lower():
                    fix_suggestions.append("REORDER_EVENTS")
                elif "set" in content.lower():
                    fix_suggestions.append("SET_CARID")
        
        # Return most common suggestion
        if fix_suggestions:
            return Counter(fix_suggestions).most_common(1)[0][0]
        else:
            return "Manual review required"
    
    def _get_suggested_fix(self, anomaly_type: str) -> str:
        """Get most common fix for anomaly type from historical data"""
        common_fixes = self.learned_patterns["common_fixes"]
        if common_fixes:
            # Find the most common fix that is not "Manual review required"
            for fix, _ in Counter(common_fixes).most_common():
                if fix != "Manual review required":
                    return fix
            return "Manual review required"
        return "Manual review required"
    
    def _get_recommendation(self, confidence: float, frequency: int, total: int) -> str:
        """Get recommendation based on confidence and frequency"""
        if confidence > 0.8 and frequency > (total / 20):
            return "High confidence - frequently observed and resolved pattern"
        elif confidence > 0.7:
            return "Moderate confidence - pattern seen before but needs validation"
        elif frequency > 0:
            return "Low confidence - pattern observed but resolution uncertain"
        else:
            return "New pattern - requires manual review and validation"
    
    def update_learning_from_feedback(self, anomaly_type: str, success: bool, effectiveness_score: float = 0.0):
        """Update learning based on new feedback"""
        # In a real implementation, this would update the vector database
        # and re-analyze patterns. For now, we'll simulate the update.
        print(f"Learning update: {anomaly_type} - success: {success}, effectiveness: {effectiveness_score}")
        
        # Update the learned patterns (simplified)
        if anomaly_type in self.learned_patterns["common_types"]:
            # Adjust confidence based on feedback
            current_confidence = self.learned_patterns["confidence_by_type"].get(anomaly_type, {}).get("avg_confidence", 0.7)
            if success:
                new_confidence = min(0.95, current_confidence + 0.05)
            else:
                new_confidence = max(0.3, current_confidence - 0.1)
            
            # Update confidence stats
            if anomaly_type not in self.learned_patterns["confidence_by_type"]:
                self.learned_patterns["confidence_by_type"][anomaly_type] = {
                    "avg_confidence": new_confidence,
                    "min_confidence": new_confidence,
                    "max_confidence": new_confidence,
                    "count": 1
                }
            else:
                stats = self.learned_patterns["confidence_by_type"][anomaly_type]
                stats["avg_confidence"] = new_confidence
                stats["count"] += 1
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics"""
        return {
            "learned_patterns": self.learned_patterns,
            "vector_knowledge_stats": self.vector_rag.get_knowledge_stats(),
            "learning_method": "vector_enhanced",
            "last_updated": datetime.now().isoformat()
        }

# LangChain tools for the learning system
from langchain_core.tools import tool

@tool
def get_learned_insights(anomaly_type: str) -> Dict[str, Any]:
    """Get learned insights about anomaly patterns from historical data using vector similarity"""
    learning = VectorLearning()
    return learning.get_anomaly_insights(anomaly_type)

@tool
def get_learning_stats() -> Dict[str, Any]:
    """Get overall learning statistics including vector knowledge base stats"""
    learning = VectorLearning()
    return learning.get_learning_stats()

if __name__ == "__main__":
    # Test the vector learning system
    print("🧪 Testing Vector Learning System...")
    
    learning = VectorLearning()
    
    # Test anomaly insights
    test_anomaly_types = ["MISSING_STEP", "SEQUENCE_ERROR", "CARID_INCONSISTENT", "UNKNOWN_TYPE"]
    
    for anomaly_type in test_anomaly_types:
        print(f"\n--- Insights for {anomaly_type} ---")
        insights = learning.get_anomaly_insights(anomaly_type)
        print(f"Confidence: {insights['confidence']:.3f}")
        print(f"Frequency: {insights['frequency']} ({insights['frequency_percentage']:.1f}%)")
        print(f"Suggested Fix: {insights['suggested_fix']}")
        print(f"Recommendation: {insights['recommendation']}")
        
        vector_insights = insights.get('vector_insights', {})
        print(f"Vector Confidence: {vector_insights.get('vector_confidence', 0):.3f}")
        print(f"Pattern Matches: {vector_insights.get('pattern_matches', 0)}")
        print(f"Case Matches: {vector_insights.get('case_matches', 0)}")
    
    # Test learning stats
    print(f"\n--- Learning Stats ---")
    stats = learning.get_learning_stats()
    print(f"Total Anomalies: {stats['learned_patterns']['total_anomalies']}")
    print(f"Resolution Success Rate: {stats['learned_patterns']['resolution_success_rate']:.2%}")
    print(f"Vector Knowledge Items: {stats['vector_knowledge_stats']['total_items']}")
    
    print("\n✅ Vector Learning System testing complete!")
