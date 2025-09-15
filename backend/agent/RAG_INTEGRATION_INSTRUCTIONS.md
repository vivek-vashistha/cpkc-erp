
# RAG Integration Instructions for Existing CPKC Agent

## Files Created:
1. `agent_waybill_agentic_loggs_rag_enhanced.py` - RAG-integrated version of your agent
2. `rag_enhanced_system_prompt.py` - RAG-enhanced system prompt
3. `rag_integration_for_existing.py` - RAG integration utilities

## Integration Options:

### Option 1: Use RAG-Enhanced Agent (Recommended)
```python
# Replace the import in your API server
from agent_waybill_agentic_loggs_rag_enhanced import graph

# The rest of your code remains the same
```

### Option 2: Manual Integration
1. Add RAG imports to your existing agent:
```python
from rag.tools.rag_tools import RAG_TOOLS
from rag.learning.simple_learning import get_learned_insights, get_learning_stats
```

2. Update your TOOLS dictionary:
```python
ENHANCED_TOOLS = {
    **TOOLS,  # Include existing tools
    **RAG_TOOLS,  # Add RAG tools
    "get_learned_insights": get_learned_insights,
    "get_learning_stats": get_learning_stats,
}
```

3. Update your LLM binding:
```python
llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0).bind_tools(list(ENHANCED_TOOLS.values()))
```

4. Update your tools_node to use ENHANCED_TOOLS instead of TOOLS

### Option 3: Use RAG-Enhanced System Prompt
Replace your system prompt with the RAG-enhanced version:
```python
from rag_enhanced_system_prompt import RAG_ENHANCED_SYSTEM
# Use RAG_ENHANCED_SYSTEM instead of SYSTEM_13_09_2025
```

## Testing the Integration:

### Test 1: Basic RAG Functionality
```python
from rag.integration.rag_integration_for_existing import get_rag_enhanced_anomaly_detector

detector = get_rag_enhanced_anomaly_detector()
anomaly = detector.get_rag_enhanced_anomaly(
    waybill_id="WB3005",
    anomaly_type="MISSING_STEP",
    base_confidence=0.8,
    base_details="Missing 'Closed' event"
)
print(anomaly)
```

### Test 2: Enhanced Anomaly Detection
```python
from rag.integration.rag_integration_for_existing import enhance_anomalies_with_rag

# Your existing anomalies
existing_anomalies = [
    {
        "id": "anomaly_123",
        "waybill_id": "WB3005",
        "type": "MISSING_STEP",
        "confidence": 0.8,
        "details": "Missing 'Closed' event"
    }
]

# Enhance with RAG
enhanced_anomalies = enhance_anomalies_with_rag(existing_anomalies, "WB3005")
print(enhanced_anomalies)
```

### Test 3: API Server Integration
```python
# In your new_waybill_api_server.py, change the import:
from agent_waybill_agentic_loggs_rag_enhanced import graph

# Everything else remains the same
```

## Key Benefits:
1. **Enhanced Confidence**: RAG provides confidence scores based on historical data
2. **Better Fixes**: Suggested fixes include proven strategies from historical cases
3. **Context-Aware**: Analysis considers similar past anomalies
4. **Learning**: System learns from new resolutions and feedback
5. **Backward Compatible**: Works with existing API and data structures

## Next Steps:
1. Test the RAG-enhanced agent with your existing waybill data
2. Monitor the enhanced confidence scores and fix suggestions
3. Add more domain-specific knowledge to the RAG system
4. Collect feedback from resolutions to improve learning

## Troubleshooting:
- If you get import errors, ensure the `rag` package is in your Python path
- If tools don't work, check that ENHANCED_TOOLS is properly defined
- If confidence scores seem off, verify the learning system has historical data
- If fixes aren't enhanced, check that the knowledge base has relevant patterns

## Support:
- Check the demo scripts in `rag/demos/` for examples
- Review the integration utilities in `rag/integration/`
- Read the comprehensive documentation in `rag/README.md`
