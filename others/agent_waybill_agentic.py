# agent_waybill_agentic.py
# Fully agentic LangGraph agent that decides which logistics tools to call.
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
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

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

TOOLS = [
    ping_tool,
    get_events_tool,
    get_waybills_tool,
    match_contract_tool,
    create_invoice_tool,
    get_invoices_tool,
    get_customs_tool,
    get_assets_assignments_tool,
]

tool_node = ToolNode(TOOLS)

# -----------------------------
# Model with tool binding (ChatOpenAI)
# -----------------------------
SYSTEM = (
    "You are a logistics QA agent. "
    "Given a waybill_id from the user, decide which tools to call to determine if the shipment has anomalies. "
    "Examples: missing event fields, out-of-order timestamps, invalid location codes, or origin/destination conflicts. "
    "Only rely on tool outputs. When finished, return a concise JSON object with keys: "
    "`anomaly_found` (true/false), `reasons` (list of strings), and `supporting_evidence` "
    "(list of {event_id, note})."
)

llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0).bind_tools(TOOLS)

def agent_node(state: MessagesState) -> dict:
    """Agent node: the LLM decides to call a tool (or answer)."""
    messages = state["messages"]
    # Ensure the first message is a SystemMessage; don't treat messages like dicts
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM)] + messages
    resp = llm.invoke(messages)
    return {"messages": [resp]}

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
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    graph.add_edge("tools", "agent")
    return graph.compile(checkpointer=MemorySaver())

# -----------------------------
# Run example
# -----------------------------
if __name__ == "__main__":
    app = build_graph()
    waybill_id = os.getenv("TEST_WAYBILL_ID", "WB3005")
    thread_id = os.getenv("THREAD_ID", "cpkc-demo")  # required with MemorySaver

    user_msg = HumanMessage(content=f"Check waybill {waybill_id} for anomalies and explain briefly.")

    out = app.invoke({"messages": [user_msg]}, config={"configurable": {"thread_id": thread_id}})

    final = out["messages"][-1]
    print("\n=== FINAL VERDICT ===\n")
    print(final.content if isinstance(final, AIMessage) else getattr(final, "content", ""))
