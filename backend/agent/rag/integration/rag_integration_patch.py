
# RAG Integration Patch for agent_waybill_agentic_loggs.py
# Add these imports at the top of the file (after existing imports)

# RAG Integration Imports
from rag_tools import RAG_TOOLS
from simple_learning import get_learned_insights, get_learning_stats

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
    print("\n[ENHANCED AGENT] ====== RAG-Enhanced Analysis =====")
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
        print("\n[ENHANCED TOOL] >>> Call")
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
