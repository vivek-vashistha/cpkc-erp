# Vector RAG-Enhanced LangGraph agent with OpenAI embeddings and ChromaDB
# Production-grade RAG system for anomaly detection

import os
import sys
import json
from typing import Dict, Any, Optional
from urllib.parse import urlencode

# Add current directory to Python path to allow importing from 'others' module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from dotenv import load_dotenv

# LangGraph / LangChain
from langgraph.graph import StateGraph, END
from langgraph.graph import MessagesState
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

# Vector RAG Integration Imports
from rag.tools.vector_rag_tools import VECTOR_RAG_TOOLS
from rag.learning.vector_learning import get_learned_insights, get_learning_stats

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

# Enhanced Tools with Vector RAG
ENHANCED_TOOLS = {
    "ping_tool": ping_tool,
    "get_events_tool": get_events_tool,
    "get_waybills_tool": get_waybills_tool,
    "match_contract_tool": match_contract_tool,
    "create_invoice_tool": create_invoice_tool,
    "get_invoices_tool": get_invoices_tool,
    "get_customs_tool": get_customs_tool,
    "get_assets_assignments_tool": get_assets_assignments_tool,
    # Add Vector RAG tools
    **VECTOR_RAG_TOOLS,
    "get_learned_insights": get_learned_insights,
    "get_learning_stats": get_learning_stats,
}

from others.prompts.system_prompt_13_09_2025 import SYSTEM_13_09_2025 as SYSTEM

# Vector RAG-Enhanced System Prompt
VECTOR_RAG_ENHANCED_SYSTEM = """
You are a logistics QA assistant with access to a comprehensive vector-based knowledge base of anomaly patterns, 
resolution strategies, and business rules. You have enhanced capabilities through Vector RAG (Retrieval-Augmented Generation) 
using OpenAI embeddings and semantic similarity search.

### TASK
The user provides a waybill ID (e.g., "WB3000", possibly embedded in a sentence).
1) Extract waybill_id (regex: \bWB\d+\b).
2) BEFORE analyzing, ALWAYS call search_anomaly_patterns() to get relevant knowledge using semantic similarity.
3) Call tools as needed to fetch events and waybill metadata.
4) Use get_learned_insights() to get enhanced confidence scores based on vector similarity and historical data.
5) Validate the required sequence (exactly and in order):
   Canonical order (must be chronological):
    Created → Picked Up → In Transit → At Border → Arrived → Delivered → Closed

   Terminal events:
    - Closed (always terminal)
    - Cancelled (terminal; mutually exclusive with Delivered)

   Allowed event types:
    ["Created","Picked Up","In Transit","At Border","Arrived","Delivered","Closed","Cancelled"]

6) Find anomalies using Vector RAG-enhanced analysis:
   - Missing any required step.            // MISSING_STEP
   - Out-of-sequence event types.          // SEQUENCE_ERROR (order vs canonical)
   - Negative time progression.            // NEGATIVE_DURATION (event_ts decreased)
   - Conflicting terminals.                // TERMINAL_CONFLICT (Delivered & Cancelled)
   - Multiple Delivered events.            // MULTI_DELIVERED
   - Activity after a terminal event.      // POST_TERMINAL_ACTIVITY
   - Unknown event types.                  // UNKNOWN_EVENT_TYPE (not in allow-list)
   - CarId rules: if present, all events must share one value. If some missing → "CARID_MISSING". If >1 value → "CARID_INCONSISTENT".
   - CSNId rules: same as CarId, using "CSNID_MISSING"/"CSNID_INCONSISTENT".

7) Suggest fixes when IDs mismatch using priority:
   a) value on the earliest "Created" event (if present), else
   b) majority value across events, else
   c) value from the earliest event that has one.
   Set "needs_confirmation": true whenever "suggested_fix" is not null.

### VECTOR RAG ENHANCEMENT WORKFLOW
1. ALWAYS call search_anomaly_patterns() with semantic queries before analyzing
2. Use get_learned_insights() for each anomaly type you detect to get vector-enhanced confidence
3. Reference retrieved patterns, rules, and historical cases with similarity scores
4. Apply proven resolution strategies from similar cases found via vector similarity
5. Use enhanced confidence scores based on vector similarity and historical success rates
6. Leverage get_similar_anomalies() to find related cases for complex anomalies

### RPA STATUS GUIDE (for "rpa_status")
- Use "Auto Fix" for anomalies the bot can deterministically repair:
  * "MISSING_STEP" (e.g., insert missing "Closed" after "Delivered")
  * "MULTI_DELIVERED" (merge duplicates; keep the most plausible single Delivered)
  * "SEQUENCE_ERROR" (reorder to match canonical sequence when timestamps support it)
- Use "Manual Review Required" for all other anomaly types:
  * "NEGATIVE_DURATION", "TERMINAL_CONFLICT", "POST_TERMINAL_ACTIVITY",
    "UNKNOWN_EVENT_TYPE", "CARID_INCONSISTENT", "CARID_MISSING",
    "CSNID_INCONSISTENT", "CSNID_MISSING"
- Use "Needs Data" only when insufficient information prevents proposing a fix
  (e.g., events not returned, essential timestamps entirely missing, or tool/data fetch errors).

### OUTPUT CONTRACT (STRICT)
- Return ONLY a valid JSON array (UTF-8). No markdown, no backticks, no prose.
- Each element MUST be an object with these keys ONLY (no extras):

{
  "id": string,                           // e.g. anomaly_1757683666935_4c2y5npvm
  "waybill_id": string,                   // e.g. "WB3000"
  "car_id": string|null,                  // chosen canonical CarId or null
  "csn_id": string|null,                  // chosen canonical CSNId or null
  "type": "SEQUENCE_ERROR"|"MISSING_STEP"|"NEGATIVE_DURATION"|"TERMINAL_CONFLICT"|"MULTI_DELIVERED"|"POST_TERMINAL_ACTIVITY"|"UNKNOWN_EVENT_TYPE"|"CARID_INCONSISTENT"|"CARID_MISSING"|"CSNID_INCONSISTENT"|"CSNID_MISSING",
  "confidence": number,                   // 0.0–1.0 (enhanced by Vector RAG similarity)
  "suggested_fix": {
    "actions": [
      {
        "name": "INSERT_EVENT"|"REORDER_EVENTS"|"CORRECT_EVENT_TS"|"REVIEW_TERMINAL_STATE"|
             "MERGE_DUPLICATE_EVENTS"|"TRIM_POST_TERMINAL_EVENTS"|"MAP_EVENT_TYPE"|
             "SET_CARID"|"SET_CSNID"|null,
        "args": [ { "key": string, "value": string } ],
        "rationale": string    // detailed human-friendly description enhanced with Vector RAG context
      }
    ]
  },
  "status": "NEW"|"UNCHANGED",
  "rpa_status": "Auto Fix"|"Manual Review Required"|"Needs Data"|null,
  "created_ts": string,                   // ISO 8601 UTC with trailing "Z"
  "updated_ts": string,                   // same format; for a new record equals created_ts
  "details": string,                     // Detailed human-friendly description enhanced with Vector RAG context
  "needs_confirmation": boolean         // true if human intervention is required
}

- IDs: generate as anomaly_{epochMillis}_{10-char lowercase a-z0-9}.
- Timestamps: generate current UTC as ISO 8601 ending with "Z".
- If there are NO anomalies, return [] exactly.
- Set "needs_confirmation": true when any action is suggested; otherwise false.
- Use double quotes everywhere. No trailing commas. No extra keys.
- ENHANCE confidence scores using Vector RAG similarity and historical data
- ENHANCE suggested fixes with proven strategies from vector-similar cases
- ENHANCE details with context from retrieved knowledge and similarity scores

### VECTOR RAG ENHANCEMENT EXAMPLES
- If you find a MISSING_STEP anomaly, reference similar patterns with high similarity scores
- If confidence is high based on vector similarity, boost the confidence score
- Include specific details from retrieved patterns in the rationale with similarity scores
- Reference business rules from the vector knowledge base in your analysis
- Use get_similar_anomalies() for complex cases to find related resolution strategies

### STYLE
- Do all reasoning internally; OUTPUT MUST BE JSON ARRAY ONLY.
- Do not wrap in markdown backticks. Do not add explanations, headings, or bullets.
- Use Vector RAG knowledge to enhance your analysis but maintain the exact output format.
"""

llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0).bind_tools(list(ENHANCED_TOOLS.values()))

def agent_node(state: MessagesState) -> dict:
    """Agent node: the LLM decides to call a tool (or answer)."""
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=VECTOR_RAG_ENHANCED_SYSTEM)] + messages

    # ---- LOG: agent thought / plan before tools ----
    print("\n[VECTOR-RAG AGENT] ====== Thought / Reply ======")
    if len(messages) > 1 and isinstance(messages[-1], HumanMessage):
        print(f"[VECTOR-RAG AGENT] User: {messages[-1].content}")
    # invoke
    resp = llm.invoke(messages)
    # print assistant content (before tool calls)
    if isinstance(resp, AIMessage):
        print(f"[VECTOR-RAG AGENT] Assistant: {resp.content}")
        if hasattr(resp, 'tool_calls') and resp.tool_calls:
            print(f"[VECTOR-RAG AGENT] Tool calls: {len(resp.tool_calls)}")
        else:
            print("[VECTOR-RAG AGENT] No tool calls - final response")

    return {"messages": [resp]}

def _pretty(data: Any, limit: int = 1200) -> str:
    s = json.dumps(data, indent=2, ensure_ascii=False)
    return s if len(s) <= limit else s[:limit] + "\n... [truncated]"

def tools_node(state: MessagesState) -> dict:
    """
    Custom tool executor with logging:
      - prints each tool call name + args
      - executes the tool
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
        print("\n[VECTOR-RAG TOOL] >>> Call")
        print(f"[VECTOR-RAG TOOL] name: {name}")
        print(f"[VECTOR-RAG TOOL] args: {_pretty(args)}")

        if name not in ENHANCED_TOOLS:
            result = {"error": f"Unknown tool: {name}"}
        else:
            try:
                result = ENHANCED_TOOLS[name].invoke(args)
            except Exception as e:
                result = {"error": str(e)}

        # LOG: tool result
        print("[VECTOR-RAG TOOL] <<< Result")
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
# Graph
# -----------------------------
def build_graph():
    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tools_node)  # custom node with logging
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    graph.add_edge("tools", "agent")
    # return graph.compile(checkpointer=MemorySaver())
    return graph.compile()

graph = build_graph()

# -----------------------------
# Run example
# -----------------------------
if __name__ == "__main__":
    app = graph
    waybill_id = os.getenv("TEST_WAYBILL_ID", "WB3000")
    thread_id = os.getenv("THREAD_ID", "cpkc-vector-rag-demo")

    user_msg = HumanMessage(content=f"Check waybill {waybill_id} for anomalies using Vector RAG-enhanced analysis. Use search_anomaly_patterns() and get_learned_insights() to enhance your analysis with semantic similarity.")

    out = app.invoke({"messages": [user_msg]}, config={"configurable": {"thread_id": thread_id}})

    final = out["messages"][-1]
    print("\n=== FINAL VECTOR RAG-ENHANCED VERDICT ===\n")
    print(final.content if isinstance(final, AIMessage) else getattr(final, "content", ""))
