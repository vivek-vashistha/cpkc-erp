# agent_waybill_agentic.py
# Fully agentic LangGraph agent (LLM decides tools) with verbose, step-by-step logging.
#
# Requirements:
#   pip install langgraph langchain-core langchain-openai openai python-dotenv requests

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

TOOLS = {
    "ping_tool": ping_tool,
    "get_events_tool": get_events_tool,
    "get_waybills_tool": get_waybills_tool,
    "match_contract_tool": match_contract_tool,
    "create_invoice_tool": create_invoice_tool,
    "get_invoices_tool": get_invoices_tool,
    "get_customs_tool": get_customs_tool,
    "get_assets_assignments_tool": get_assets_assignments_tool,
}

# -----------------------------
# Model with tool binding (ChatOpenAI)
# -----------------------------
# SYSTEM = (
#     "You are a logistics QA agent. "
#     "Given a waybill_id from the user, decide which tools to call to determine if the shipment has anomalies. "
#     "Examples: missing event fields, out-of-order timestamps, invalid location codes, or origin/destination conflicts. "
#     "Only rely on tool outputs. When finished, return a concise JSON object with keys: "
#     "`anomaly_found` (true/false), `reasons` (list of strings), and `supporting_evidence` "
#     "(list of {event_id, note})."
# )

# Updated system prompt to ensure sequence checking
SYSTEM = """
You are a logistics QA assistant. The user provides a waybill ID, either directly e.g., "WB3005" or in a sentence.
Your tasks:
1. Extract the waybill_id (pattern: WB followed by digits).
2. Call tools in order to fetch events and waybill metadata.
3. Validate the event sequence follows exactly:
   Created → Picked Up → In Transit → At Border → Arrived → Delivered → Closed
   Each event must exist and occur in that chronological order.
4. Identify anomalies:
   - Missing any step.
   - Out-of-sequence timestamps.
   - CarId: If present, all events should share a single CarId. If some are missing CarId, flag “missing CarId”. If multiple CarId values occur, this is an anomaly.
   - CSNId: If present, all events should share a single CSNId. If some are missing CSNId, flag “missing CSNId”. If multiple CSNId values occur, this is an anomaly.
5. SUGGESTED FIXES (WHEN IDs MISMATCH)
    - If multiple CarId or CSNId values occur, choose a suggested CarId or CSNId using this priority:
        (a) the CarId on the earliest “Created” event if present; else
        (b) the majority CarId or CSNId across events; else
        (c) the CarId or CSNId from the earliest event that has a CarId or CSNId.
    - If multiple CSNId values occur, suggest a CSNId using the same priority rule.
    - Always ask the user to validate/confirm the suggested CarId/CSNId.
6. Return final JSON:
{
  "anomaly_found": true|false,
  "reasons": [...],
  "supporting_evidence": [{"event_id": "...", "note": "..."}]
}
"""

llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0).bind_tools(list(TOOLS.values()))

def agent_node(state: MessagesState) -> dict:
    """Agent node: the LLM decides to call a tool (or answer)."""
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM)] + messages

    # ---- LOG: agent thought / plan before tools ----
    print("\n[AGENT] ====== Thought / Reply ======")
    if len(messages) > 1 and isinstance(messages[-1], HumanMessage):
        print(f"[AGENT] User: {messages[-1].content}")
    # invoke
    resp = llm.invoke(messages)
    # print assistant content (before tool calls)
    if isinstance(resp, AIMessage) and resp.content:
        print(f"[AGENT] Assistant: {resp.content}")

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
        print("\n[TOOL] >>> Call")
        print(f"[TOOL] name: {name}")
        print(f"[TOOL] args: {_pretty(args)}")

        if name not in TOOLS:
            result = {"error": f"Unknown tool: {name}"}
        else:
            try:
                result = TOOLS[name].invoke(args)
            except Exception as e:
                result = {"error": str(e)}

        # LOG: tool result
        print("[TOOL] <<< Result")
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
    waybill_id = os.getenv("TEST_WAYBILL_ID", "WB3005")
    thread_id = os.getenv("THREAD_ID", "cpkc-demo")

    user_msg = HumanMessage(content=f"Check waybill {waybill_id} for anomalies and explain briefly.")

    out = app.invoke({"messages": [user_msg]}, config={"configurable": {"thread_id": thread_id}})

    final = out["messages"][-1]
    print("\n=== FINAL VERDICT ===\n")
    print(final.content if isinstance(final, AIMessage) else getattr(final, "content", ""))
