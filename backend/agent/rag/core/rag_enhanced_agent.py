# backend/agent/rag_enhanced_agent.py
# Enhanced version of your existing agent with RAG capabilities

import os
import json
from typing import Dict, Any, Optional
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

# LangGraph / LangChain
from langgraph.graph import StateGraph, END
from langgraph.graph import MessagesState
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

# Import our RAG components
from ..tools.rag_tools import RAG_TOOLS
from ..learning.simple_learning import get_learned_insights, get_learning_stats

# -----------------------------
# Env
# -----------------------------
load_dotenv()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# -----------------------------
# Simple stateless HTTP helpers (your API)
# -----------------------------
BASE_URL = os.getenv("LOGI_API_URL", "").rstrip("/")
API_KEY = os.getenv("LOGI_API_KEY", "")
TIMEOUT = float(os.getenv("LOGI_TIMEOUT", "30"))
DEFAULT_LIMIT = int(os.getenv("LOGI_DEFAULT_LIMIT", "50"))
DEBUG = os.getenv("LOGI_DEBUG", "false").lower() == "true"

if not BASE_URL or not API_KEY:
    raise RuntimeError("Missing LOGI_API_URL or LOGI_API_KEY in .env")

def _request(method: str, path: str,
             params: Optional[Dict[str, Any]] = None,
             json_body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    params = dict(params or {})
    params.setdefault("path", path)
    params.setdefault("key", API_KEY)

    if DEBUG:
        print(f"[LOGI] {method} {BASE_URL}?{urlencode(params)}")
        if json_body:
            print(f"[LOGI] payload: {json.dumps(json_body, indent=2)}")

    resp = requests.request(
        method=method.upper(),
        url=BASE_URL,
        params=params,
        json=json_body,
        timeout=TIMEOUT,
        headers={"x-api-key": API_KEY, "Content-Type": "application/json"} if json_body else {"x-api-key": API_KEY},
    )
    try:
        data = resp.json()
    except ValueError:
        data = {"raw": resp.text}
    resp.raise_for_status()
    return data

# -----------------------------
# Your HTTP functions (stateless)
# -----------------------------
def ping() -> Dict[str, Any]:
    return _request("GET", "ping")

def get_waybills(*, id: Optional[str] = None, customer_id: Optional[str] = None,
                 status: Optional[str] = None, origin: Optional[str] = None,
                 dest: Optional[str] = None, commodity: Optional[str] = None,
                 since: Optional[str] = None, limit: Optional[int] = None,
                 pageToken: Optional[str] = None) -> Dict[str, Any]:
    params = {k: v for k, v in dict(
        id=id, customer_id=customer_id, status=status, origin=origin, dest=dest,
        commodity=commodity, since=since, limit=limit or DEFAULT_LIMIT, pageToken=pageToken
    ).items() if v is not None}
    return _request("GET", "waybills", params=params)

def match_contract(waybill_id: str) -> Dict[str, Any]:
    return _request("GET", "contract/match", params={"waybill_id": waybill_id})

def create_invoice(waybill_id: str, currency: str = "CAD") -> Dict[str, Any]:
    return _request("POST", "invoices", json_body={"waybill_id": waybill_id, "currency": currency})

def get_invoices(*, id: Optional[str] = None, status: Optional[str] = None,
                 due_before: Optional[str] = None, customer_id: Optional[str] = None,
                 waybill_id: Optional[str] = None) -> Dict[str, Any]:
    params = {k: v for k, v in dict(
        id=id, status=status, due_before=due_before, customer_id=customer_id, waybill_id=waybill_id
    ).items() if v is not None}
    return _request("GET", "invoices", params=params)

def get_events(waybill_id: str) -> Dict[str, Any]:
    return _request("GET", "events", params={"waybill_id": waybill_id})

def get_customs(waybill_id: str) -> Dict[str, Any]:
    return _request("GET", "customs", params={"waybill_id": waybill_id})

def get_assets_assignments(waybill_id: str) -> Dict[str, Any]:
    return _request("GET", "assets/assignments", params={"waybill_id": waybill_id})

# -----------------------------
# Wrap as LangChain Tools using @tool (no kwargs).
# Names from function names; descriptions from docstrings.
# -----------------------------
@tool
def ping_tool() -> Dict[str, Any]:
    """Health check for the logistics API."""
    return ping()

@tool
def get_events_tool(waybill_id: str) -> Dict[str, Any]:
    """Fetch shipment events (logs) for a waybill."""
    return get_events(waybill_id=waybill_id)

@tool
def get_waybills_tool(id: Optional[str] = None, customer_id: Optional[str] = None,
                      status: Optional[str] = None, origin: Optional[str] = None,
                      dest: Optional[str] = None, commodity: Optional[str] = None,
                      since: Optional[str] = None, limit: Optional[int] = None,
                      pageToken: Optional[str] = None) -> Dict[str, Any]:
    """Fetch waybills; optionally filter by id/status/origin/dest/etc."""
    return get_waybills(id=id, customer_id=customer_id, status=status, origin=origin, dest=dest,
                        commodity=commodity, since=since, limit=limit, pageToken=pageToken)

@tool
def match_contract_tool(waybill_id: str) -> Dict[str, Any]:
    """Find best contract for a given waybill id."""
    return match_contract(waybill_id=waybill_id)

@tool
def create_invoice_tool(waybill_id: str, currency: str = "CAD") -> Dict[str, Any]:
    """Create invoice for a waybill (auto-match contract)."""
    return create_invoice(waybill_id=waybill_id, currency=currency)

@tool
def get_invoices_tool(id: Optional[str] = None, status: Optional[str] = None,
                      due_before: Optional[str] = None, customer_id: Optional[str] = None,
                      waybill_id: Optional[str] = None) -> Dict[str, Any]:
    """Fetch invoices; filter by id, status, due_before, customer_id, waybill_id."""
    return get_invoices(id=id, status=status, due_before=due_before, customer_id=customer_id, waybill_id=waybill_id)

@tool
def get_customs_tool(waybill_id: str) -> Dict[str, Any]:
    """Fetch customs document for a waybill."""
    return get_customs(waybill_id=waybill_id)

@tool
def get_assets_assignments_tool(waybill_id: str) -> Dict[str, Any]:
    """Fetch assets assigned to a waybill."""
    return get_assets_assignments(waybill_id=waybill_id)

# -----------------------------
# Enhanced System Prompt with RAG
# -----------------------------
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

ANOMALY_SCHEMA = {
    "name": "anomaly_list",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "anomalies": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "waybill_id": {"type": "string"},
                        "car_id": {"type": "string"},
                        "csn_id": {"type": "string"},
                        "type": {"type": "string"},
                        "suggested_fix": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "action": {"type": "string"},
                                "event_type": {"type": "string"},
                                "ts_hint": {"type": "string", "format": "date-time"}
                            },
                            "required": ["action"]
                        },
                        "confidence": {"type": "number"},
                        "status": {"type": "string"},
                        "rag_enhanced": {"type": "boolean"},
                        "knowledge_sources": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["waybill_id", "type", "suggested_fix", "confidence", "status"]
                }
            }
        },
        "required": ["anomalies"]
    }
}

# -----------------------------
# Enhanced Tools with RAG
# -----------------------------
# Combine original tools with RAG tools
ENHANCED_TOOLS = {
    "ping_tool": ping_tool,
    "get_events_tool": get_events_tool,
    "get_waybills_tool": get_waybills_tool,
    "match_contract_tool": match_contract_tool,
    "create_invoice_tool": create_invoice_tool,
    "get_invoices_tool": get_invoices_tool,
    "get_customs_tool": get_customs_tool,
    "get_assets_assignments_tool": get_assets_assignments_tool,
    # Add RAG tools
    **RAG_TOOLS,
    "get_learned_insights": get_learned_insights,
    "get_learning_stats": get_learning_stats,
}

# -----------------------------
# Enhanced Model with RAG tools
# -----------------------------
llm = ChatOpenAI(model=OPENAI_MODEL, 
                temperature=0,
                response_format={"type": "json_schema", "json_schema": ANOMALY_SCHEMA},
                ).bind_tools(list(ENHANCED_TOOLS.values()))

def enhanced_agent_node(state: MessagesState) -> dict:
    """Enhanced agent node with RAG capabilities"""
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=ENHANCED_SYSTEM)] + messages

    # ---- LOG: agent thought / plan before tools ----
    print("\n[ENHANCED AGENT] ====== RAG-Enhanced Analysis ======")
    if len(messages) > 1 and isinstance(messages[-1], HumanMessage):
        print(f"[ENHANCED AGENT] User: {messages[-1].content}")
    
    # invoke with enhanced tools
    resp = llm.invoke(messages)
    
    # print assistant content (before tool calls)
    if isinstance(resp, AIMessage) and resp.content:
        print(f"[ENHANCED AGENT] Assistant: {resp.content}")

    return {"messages": [resp]}

def _pretty(data: Any, limit: int = 1200) -> str:
    s = json.dumps(data, indent=2, ensure_ascii=False)
    return s if len(s) <= limit else s[:limit] + "\n... [truncated]"

def enhanced_tools_node(state: MessagesState) -> dict:
    """
    Enhanced tool executor with RAG capabilities and logging:
      - prints each tool call name + args
      - executes the tool (including RAG tools)
      - prints tool response (truncated)
      - appends ToolMessage back to state for the agent loop
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

def should_continue(state: MessagesState):
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
        return "tools"
    return "end"

# -----------------------------
# Enhanced Graph
# -----------------------------
def build_enhanced_graph():
    graph = StateGraph(MessagesState)
    graph.add_node("agent", enhanced_agent_node)
    graph.add_node("tools", enhanced_tools_node)  # enhanced node with RAG tools
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    graph.add_edge("tools", "agent")
    return graph.compile()

enhanced_graph = build_enhanced_graph()

# -----------------------------
# Run example
# -----------------------------
if __name__ == "__main__":
    app = enhanced_graph
    waybill_id = os.getenv("TEST_WAYBILL_ID", "WB3005")
    thread_id = os.getenv("THREAD_ID", "cpkc-rag-demo")

    user_msg = HumanMessage(content=f"Check waybill {waybill_id} for anomalies using RAG-enhanced analysis.")

    print(f"\n=== RAG-Enhanced Anomaly Detection Demo ===")
    print(f"Waybill ID: {waybill_id}")
    print(f"Thread ID: {thread_id}")
    
    out = app.invoke({"messages": [user_msg]}, config={"configurable": {"thread_id": thread_id}})

    final = out["messages"][-1]
    print("\n=== FINAL RAG-ENHANCED VERDICT ===\n")
    print(final.content if isinstance(final, AIMessage) else getattr(final, "content", ""))
