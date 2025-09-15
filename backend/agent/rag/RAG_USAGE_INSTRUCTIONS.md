
# RAG Integration Usage Instructions

## Files Created:
1. `quick_rag.py` - File-based knowledge storage system
2. `rag_tools.py` - RAG tools for knowledge retrieval
3. `simple_learning.py` - Learning from historical anomalies
4. `rag_enhanced_agent.py` - Complete RAG-enhanced agent
5. `demo_rag.py` - Demo script showing RAG capabilities
6. `integrate_rag.py` - This integration script

## How to Use:

### Option 1: Use the Complete RAG-Enhanced Agent
```python
from rag_enhanced_agent import enhanced_graph

# Use the enhanced graph instead of the original
app = enhanced_graph
waybill_id = "WB3005"
user_msg = HumanMessage(content=f"Check waybill {waybill_id} for anomalies using RAG-enhanced analysis.")
out = app.invoke({"messages": [user_msg]})
```

### Option 2: Integrate RAG into Existing Agent
1. Backup your original agent file
2. Add the imports from `rag_integration_patch.py`
3. Replace the SYSTEM prompt with ENHANCED_SYSTEM
4. Add RAG tools to your TOOLS dict
5. Use enhanced_agent_node and enhanced_tools_node

### Option 3: Test Individual Components
```python
# Test RAG components individually
from demo_rag import demo_rag_components
demo_rag_components()

# Test enhanced analysis
from demo_rag import demo_rag_enhanced_analysis
result = demo_rag_enhanced_analysis()
```

## Key Benefits:
1. **Knowledge Retrieval**: Access to patterns, rules, and historical cases
2. **Learning**: Confidence scores based on historical data
3. **Enhanced Fixes**: Specific resolution strategies from proven cases
4. **Dynamic Knowledge**: Easy to add new patterns and rules
5. **Backward Compatible**: Works with existing waybill data

## Next Steps:
1. Run the demo to see RAG in action
2. Test with your actual waybill data
3. Add more knowledge to the knowledge base
4. Integrate with your existing workflow
5. Monitor and improve based on results

## Environment Variables:
Make sure you have these set in your .env file:
- OPENAI_MODEL (default: gpt-4o-mini)
- LOGI_API_URL
- LOGI_API_KEY
- LOGI_TIMEOUT (default: 30)
- LOGI_DEFAULT_LIMIT (default: 50)
- LOGI_DEBUG (default: false)
