import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import Query

# LangChain message types
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage

# IMPORTANT: we only import the graph; we DO NOT modify the agent file.
# Your agent file must be on PYTHONPATH or in the same directory.
try:
    # file name: agent_waybill_agentic_loggs.py
    # from agent_waybill_agentic_loggs import graph  # type: ignore
    from v2.agent_waybill_agentic import graph  # type: ignore
except Exception as e:
    # Fail fast if the agent (or its env requirements) can't load
    raise RuntimeError(
        "Failed to import agent graph from agent_waybill_agentic_loggs.py. "
        "Ensure LOGI_API_URL, LOGI_API_KEY, and OpenAI creds are set."
    ) from e

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(title="Waybill Agent API", version="1.0.0")

# keep permissive for dev; restrict in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Models
# -----------------------------
class RunRequest(BaseModel):
    waybill_id: str
    thread_id: Optional[str] = None  # defaults to waybill_id if omitted

class CheckResponse(BaseModel):
    waybill_id: str
    result: Any  # whatever the agent returns (usually JSON as a string)

class TraceMessage(BaseModel):
    type: str
    content: Any
    tool_calls: Optional[Any] = None
    name: Optional[str] = None  # for tool messages

class TraceResponse(BaseModel):
    waybill_id: str
    final: Any
    messages: List[TraceMessage]

# -----------------------------
# Helpers
# -----------------------------
def _invoke_agent(waybill_id: str, thread_id: Optional[str]) -> Dict[str, Any]:
    """
    Calls the compiled LangGraph with a single HumanMessage.
    We do not alter the agent; we only send a user request.
    """
    prompt = f"Check waybill {waybill_id} for anomalies and explain briefly."
    cfg = {"configurable": {"thread_id": thread_id or waybill_id}}

    out = graph.invoke({"messages": [HumanMessage(content=prompt)]}, config=cfg)
    if not out or "messages" not in out or not out["messages"]:
        raise HTTPException(status_code=500, detail="Agent returned no messages.")

    return out

def _final_ai_text(out: Dict[str, Any]) -> str:
    # last message should be the model's final AIMessage
    for msg in reversed(out["messages"]):
        if isinstance(msg, AIMessage):
            return msg.content or ""
    # fallback: nothing AI in the chain
    raise HTTPException(status_code=500, detail="No AI response was generated.")

def _serialize_messages(out: Dict[str, Any]) -> List[TraceMessage]:
    ser: List[TraceMessage] = []
    for m in out["messages"]:
        if isinstance(m, HumanMessage):
            ser.append(TraceMessage(type="human", content=m.content))
        elif isinstance(m, SystemMessage):
            ser.append(TraceMessage(type="system", content=m.content))
        elif isinstance(m, AIMessage):
            ser.append(
                TraceMessage(
                    type="ai",
                    content=m.content,
                    tool_calls=getattr(m, "tool_calls", None),
                )
            )
        elif isinstance(m, ToolMessage):
            ser.append(
                TraceMessage(
                    type="tool",
                    name=m.name,
                    content=m.content,  # tool result (JSON string from the agent)
                )
            )
        else:
            ser.append(TraceMessage(type=type(m).__name__, content=getattr(m, "content", None)))
    return ser

# -----------------------------
# Endpoints
# -----------------------------
@app.post("/api/anomalies", response_model=CheckResponse)
def anomalies(
    req: RunRequest,
    status: str = Query(..., description="Anomaly status filter (e.g. NEW)"),
):
    """
    Runs the agent and returns the final model verdict.
    Now mounted at /api/anomalies?status=NEW
    """
    if status.upper() != "NEW":
        raise HTTPException(status_code=400, detail="Only status=NEW is supported right now")

    out = _invoke_agent(req.waybill_id, req.thread_id)
    final_text = _final_ai_text(out)
    return CheckResponse(waybill_id=req.waybill_id, result=final_text)


@app.post("/check", response_model=CheckResponse)
def check(req: RunRequest):
    """
    Runs the agent and returns only the final model verdict (concise).
    """
    out = _invoke_agent(req.waybill_id, req.thread_id)
    final_text = _final_ai_text(out)
    return CheckResponse(waybill_id=req.waybill_id, result=final_text)

@app.post("/trace", response_model=TraceResponse)
def trace(req: RunRequest):
    """
    Runs the agent and returns the full trace (all messages + final).
    Useful for debugging/observability.
    """
    out = _invoke_agent(req.waybill_id, req.thread_id)
    final_text = _final_ai_text(out)
    messages = _serialize_messages(out)
    return TraceResponse(waybill_id=req.waybill_id, final=final_text, messages=messages)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("new_waybill_api_server:app", host="localhost", port=8080, reload=True)
