# agent_waybill_agentic.py
# Fully agentic LangGraph agent (LLM decides tools) with verbose, step-by-step logging.
# Adds: propose_ranked_fixes_tool, record_feedback_tool, record_outcome_tool, bandit + retrieval wiring.
#
# Requirements:
#   pip install langgraph langchain-core langchain-openai openai python-dotenv requests
#
import os
import sys
import json
import time
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode

# Add current directory to Python path to allow importing local modules
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

# ---- Local learning modules ----
from actions import canonicalize
from bandit import FixBandit
from learn_io import log_anomaly, log_feedback, log_outcome
from retrieve import retrieve_similar

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
# Feature builder (deterministic)
# -----------------------------

def _ts_of(events: List[dict], etype: str) -> Optional[int]:
    for e in events:
        if e.get("type") == etype:
            return e.get("ts")
    return None

def _minutes(a: Optional[int], b: Optional[int]) -> Optional[int]:
    if a is None or b is None:
        return None
    return int((b - a) / 60_000)


def build_features(events: List[dict]) -> Dict[str, Any]:
    """Convert raw events to engineered features. Keep stable & versioned."""
    feats = {
        "dep_delay_min": _minutes(_ts_of(events, "SCHEDULED_DEPART"), _ts_of(events, "ACTUAL_DEPART")),
        "arr_delay_min": _minutes(_ts_of(events, "SCHEDULED_ARRIVE"), _ts_of(events, "ACTUAL_ARRIVE")),
        "handoff_count": sum(1 for e in events if str(e.get("type", "")).startswith("HANDOFF_")),
        "customs_flag": any(e.get("type") == "CUSTOMS_HOLD" for e in events),
        "reassign_cnt": sum(1 for e in events if e.get("type") == "CAR_REASSIGNED"),
        "_features_version": "v1.0.0",
    }
    return feats

# -----------------------------
# Learning: Bandit instance & new tools
# -----------------------------
bandit = FixBandit()

@tool
def propose_ranked_fixes_tool(waybill_id: str, anomaly_type: str, lane_key: str, commodity: str,
                              llm_suggestions: Optional[List[str]] = None) -> Dict[str, Any]:
    """Rank LLM-suggested fixes using learned bandit + return few similar past cases.
    Provide llm_suggestions as a short list of strings (e.g., ["Request B13A", "Escalate to yard ops"]).
    Returns: {anomaly_id, ranked, few_shots}
    """
    # 1) fetch events & derive context/features
    ev_resp = get_events(waybill_id)
    events = ev_resp.get("events") or ev_resp.get("data") or ev_resp
    if not isinstance(events, list):
        events = events.get("items", []) if isinstance(events, dict) else []

    ctx = {"anomaly_type": anomaly_type, "lane_key": lane_key, "commodity": commodity}
    feats = build_features(events)

    # 2) retrieve a few similar cases for the LLM to show as examples
    shots = retrieve_similar(ctx, feats, k=4)

    # 3) canonicalize and rank (require some suggestions)
    suggestions = llm_suggestions or []
    arms = canonicalize(suggestions)
    if not arms:
        # if LLM passed nothing, fallback to a minimal heuristic menu
        arms = canonicalize(["Escalate to yard ops", "Request B13A", "Notify customer via portal"])

    ranked = bandit.select(ctx, arms)

    # 4) persist a compact anomaly hypothesis so it can learn later
    anomaly_id = f"A-{int(time.time()*1000)}"
    log_anomaly({
        "anomaly_id": anomaly_id,
        "bucket": f'{ctx["anomaly_type"]}|{ctx["lane_key"]}|{ctx["commodity"]}',
        "ctx": ctx,
        "features": feats,
        "proposed_arms": ranked[:3]
    })

    return {"anomaly_id": anomaly_id, "ranked": ranked, "few_shots": shots}


@tool
def record_feedback_tool(anomaly_id: str, label: str, reason: str = "",
                         chosen_arm: Optional[dict] = None, ctx: Optional[dict] = None) -> Dict[str, Any]:
    """Record human feedback: label in {'accepted','rejected','modified'}. Updates learner immediately."""
    log_feedback({"anomaly_id": anomaly_id, "label": label, "reason": reason, "chosen_arm": chosen_arm, "ctx": ctx})
    # quick reward
    reward = 0.6 if label == "accepted" else 0.3 if label == "modified" else -0.6
    if chosen_arm and ctx:
        bandit.update(ctx, chosen_arm, reward)
    return {"ok": True, "anomaly_id": anomaly_id}


@tool
def record_outcome_tool(anomaly_id: str, resolved: bool,
                        resolution_time_minutes: Optional[int] = None,
                        downstream_cost: Optional[float] = None,
                        sla_minutes: Optional[int] = None,
                        chosen_arm: Optional[dict] = None,
                        ctx: Optional[dict] = None) -> Dict[str, Any]:
    """Record shipment outcome; computes additional reward and updates the learner."""
    log_outcome({
        "anomaly_id": anomaly_id,
        "resolved": resolved,
        "res_min": resolution_time_minutes,
        "cost": downstream_cost,
        "sla": sla_minutes,
        "chosen_arm": chosen_arm,
        "ctx": ctx,
    })
    extra = 0.0
    if resolved and resolution_time_minutes is not None and sla_minutes:
        extra += max(-0.6, min(0.6, 0.6 - (resolution_time_minutes / max(1, sla_minutes))))
    if downstream_cost is not None:
        extra += 0.1 if downstream_cost < 0 else -0.1
    if chosen_arm and ctx:
        bandit.update(ctx, chosen_arm, extra)
    return {"ok": True}

# Expose the new tools
TOOLS = {
    "ping_tool": ping_tool,
    "get_events_tool": get_events_tool,
    "get_waybills_tool": get_waybills_tool,
    "match_contract_tool": match_contract_tool,
    "create_invoice_tool": create_invoice_tool,
    "get_invoices_tool": get_invoices_tool,
    "get_customs_tool": get_customs_tool,
    "get_assets_assignments_tool": get_assets_assignments_tool,
    # new learning tools
    "propose_ranked_fixes_tool": propose_ranked_fixes_tool,
    "record_feedback_tool": record_feedback_tool,
    "record_outcome_tool": record_outcome_tool,
}

# -----------------------------
# System prompt & agent
# -----------------------------
from others.prompts.system_prompt_13_09_2025 import SYSTEM_13_09_2025 as SYSTEM

llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0).bind_tools(list(TOOLS.values()))


def agent_node(state: MessagesState) -> dict:
    """Agent node: the LLM decides to call a tool (or answer)."""
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM)] + messages

    print("\n[AGENT] ====== Thought / Reply ======")
    if len(messages) > 1 and isinstance(messages[-1], HumanMessage):
        print(f"[AGENT] User: {messages[-1].content}")

    resp = llm.invoke(messages)

    if isinstance(resp, AIMessage):
        print(f"[AGENT] Assistant: {resp.content}")
        if hasattr(resp, 'tool_calls') and resp.tool_calls:
            print(f"[AGENT] Tool calls: {len(resp.tool_calls)}")
        else:
            print("[AGENT] No tool calls - final response")

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

        print("[TOOL] <<< Result")
        print(_pretty(result))

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
    graph.add_node("tools", tools_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    graph.add_edge("tools", "agent")
    return graph.compile()


graph = build_graph()

# -----------------------------
# Run example
# -----------------------------
if __name__ == "__main__":
    app = graph
    waybill_id = os.getenv("TEST_WAYBILL_ID", "WB3005")
    thread_id = os.getenv("THREAD_ID", "cpkc-demo")

    user_msg = HumanMessage(content=f"Check waybill {waybill_id} for anomalies and propose fixes.\n"
                                       "If you detect an anomaly, call propose_ranked_fixes_tool with a short list of candidate fixes.")

    out = app.invoke({"messages": [user_msg]}, config={"configurable": {"thread_id": thread_id}})

    final = out["messages"][-1]
    print("\n=== FINAL VERDICT ===\n")
    print(final.content if isinstance(final, AIMessage) else getattr(final, "content", ""))