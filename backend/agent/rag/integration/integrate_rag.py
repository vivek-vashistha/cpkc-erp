# backend/agent/integrate_rag.py
"""
Integration script to add RAG capabilities to existing agent
This script modifies the existing agent_waybill_agentic_loggs.py to include RAG
"""

import os
import shutil
from datetime import datetime

def backup_original_agent():
    """Create backup of original agent file"""
    original_file = "others/agent_waybill_agentic_loggs.py"
    backup_file = f"others/agent_waybill_agentic_loggs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    if os.path.exists(original_file):
        shutil.copy2(original_file, backup_file)
        print(f"✅ Backup created: {backup_file}")
        return backup_file
    else:
        print(f"⚠️  Original file not found: {original_file}")
        return None

def create_rag_integration_patch():
    """Create a patch to integrate RAG into existing agent"""
    
    patch_content = '''
# RAG Integration Patch for agent_waybill_agentic_loggs.py
# Add these imports at the top of the file (after existing imports)

# RAG Integration Imports
from rag.tools.rag_tools import RAG_TOOLS
from rag.learning.simple_learning import get_learned_insights, get_learning_stats

# Enhanced System Prompt with RAG
ENHANCED_SYSTEM = """
You are a logistics QA assistant with access to a comprehensive knowledge base of anomaly patterns, 
resolution strategies, and business rules. You have enhanced capabilities through RAG (Retrieval-Augmented Generation).

ENHANCED WORKFLOW:
1. Extract waybill_id from user input
2. ALWAYS call search_anomaly_patterns() to get relevant knowledge about anomaly types you're checking for
3. Use get_learned_insights() to get confidence scores based on historical data
4. Call get_events_tool() to fetch waybill events
5. Analyze events using retrieved knowledge and historical patterns
6. Apply proven resolution strategies from historical cases
7. Return anomalies with enhanced confidence scores

REQUIRED TOOL USAGE:
- Before analyzing any waybill, call search_anomaly_patterns("sequence missing event", "waybill analysis")
- Use get_learned_insights() for each anomaly type you detect
- Reference retrieved patterns, rules, and historical cases in your analysis

ANOMALY DETECTION WITH RAG:
- Use retrieved patterns to improve detection accuracy
- Apply proven fixes from historical cases
- Provide confidence scores based on historical success rates
- Reference specific business rules and SOPs
- Learn from similar past anomalies

EVENT SEQUENCE VALIDATION:
Created → Picked Up → In Transit → At Border → Arrived → Delivered → Closed
- Each event must exist and occur in chronological order
- Use retrieved business rules for exceptions (terminal shipments, cross-border, etc.)

ID CONSISTENCY CHECKS:
- CarId: All events should share single CarId, use 'Created' event priority
- CSNId: All events should share single CSNId, use 'Created' event priority
- Reference equipment ID rules from knowledge base

OUTPUT FORMAT:
Return only a JSON object with a single key "anomalies" whose value is an array of anomaly objects.
Include confidence scores enhanced by retrieved knowledge and historical patterns.

Example anomaly object:
{
  "waybill_id": "WB3000",
  "car_id": "CPKC-1001", 
  "csn_id": "CSN-CPKC-1001-202509-A",
  "type": "MISSING_STEP",
  "suggested_fix": {"action": "INSERT_EVENT", "event_type": "At Border", "ts_hint": "2025-09-09T09:55:00"},
  "confidence": 0.91,
  "status": "NEW",
  "rag_enhanced": true,
  "knowledge_sources": ["pattern_001", "case_002"]
}
"""

# Enhanced Tools (add to existing TOOLS dict)
ENHANCED_TOOLS = {
    **TOOLS,  # Include existing tools
    **RAG_TOOLS,  # Add RAG tools
    "get_learned_insights": get_learned_insights,
    "get_learning_stats": get_learning_stats,
}

# Enhanced LLM with RAG tools
enhanced_llm = ChatOpenAI(model=OPENAI_MODEL, 
                temperature=0,
                response_format={"type": "json_schema", "json_schema": ANOMALY_SCHEMA},
                ).bind_tools(list(ENHANCED_TOOLS.values()))

def enhanced_agent_node(state: MessagesState) -> dict:
    """Enhanced agent node with RAG capabilities"""
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=ENHANCED_SYSTEM)] + messages

    # ---- LOG: agent thought / plan before tools ----
    print("\\n[ENHANCED AGENT] ====== RAG-Enhanced Analysis =====")
    if len(messages) > 1 and isinstance(messages[-1], HumanMessage):
        print(f"[ENHANCED AGENT] User: {messages[-1].content}")
    
    # invoke with enhanced tools
    resp = enhanced_llm.invoke(messages)
    
    # print assistant content (before tool calls)
    if isinstance(resp, AIMessage) and resp.content:
        print(f"[ENHANCED AGENT] Assistant: {resp.content}")

    return {"messages": [resp]}

def enhanced_tools_node(state: MessagesState) -> dict:
    """
    Enhanced tool executor with RAG capabilities and logging
    """
    last = state["messages"][-1]
    tool_messages = []

    if not (isinstance(last, AIMessage) and getattr(last, "tool_calls", None)):
        return {"messages": []}

    for call in last.tool_calls:
        name = call["name"]
        args = call.get("args") or call.get("arguments") or {}
        call_id = call.get("id", "")

        # LOG: tool call
        print("\\n[ENHANCED TOOL] >>> Call")
        print(f"[ENHANCED TOOL] name: {name}")
        print(f"[ENHANCED TOOL] args: {_pretty(args)}")

        if name not in ENHANCED_TOOLS:
            result = {"error": f"Unknown tool: {name}"}
        else:
            try:
                result = ENHANCED_TOOLS[name].invoke(args)
            except Exception as e:
                result = {"error": str(e)}

        # LOG: tool result
        print("[ENHANCED TOOL] <<< Result")
        print(_pretty(result))

        # Return result to the agent as a ToolMessage
        tool_messages.append(
            ToolMessage(tool_call_id=call_id, name=name, content=json.dumps(result))
        )

    return {"messages": tool_messages}

# Enhanced Graph
def build_enhanced_graph():
    graph = StateGraph(MessagesState)
    graph.add_node("agent", enhanced_agent_node)
    graph.add_node("tools", enhanced_tools_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    graph.add_edge("tools", "agent")
    return graph.compile()

# Create enhanced graph instance
enhanced_graph = build_enhanced_graph()
'''
    
    with open("rag_integration_patch.py", "w") as f:
        f.write(patch_content)
    
    print("✅ RAG integration patch created: rag_integration_patch.py")

def create_usage_instructions():
    """Create usage instructions for the RAG integration"""
    
    instructions = """
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
"""
    
    with open("RAG_USAGE_INSTRUCTIONS.md", "w") as f:
        f.write(instructions)
    
    print("✅ Usage instructions created: RAG_USAGE_INSTRUCTIONS.md")

def main():
    """Main integration function"""
    print("🔧 RAG Integration Script")
    print("=" * 50)
    
    # Create backup
    backup_file = backup_original_agent()
    
    # Create integration patch
    create_rag_integration_patch()
    
    # Create usage instructions
    create_usage_instructions()
    
    print("\n" + "=" * 50)
    print("✅ RAG Integration Setup Complete!")
    print("\nNext Steps:")
    print("1. Run: python demo_rag.py")
    print("2. Test: python rag_enhanced_agent.py")
    print("3. Read: RAG_USAGE_INSTRUCTIONS.md")
    print("4. Integrate with your existing workflow")
    
    if backup_file:
        print(f"\n📁 Original agent backed up to: {backup_file}")

if __name__ == "__main__":
    main()
