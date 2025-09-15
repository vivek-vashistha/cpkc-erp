# RAG-Enhanced API Server for CPKC Agent
"""
API server that uses the RAG-enhanced agent for anomaly detection
This maintains compatibility with your existing API while adding RAG capabilities
"""

import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import Query

# LangChain message types
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage

# Import the RAG-enhanced agent
try:
    from agent_waybill_agentic_loggs_rag_enhanced import graph  # type: ignore
    print("✅ Using RAG-enhanced agent")
except ImportError:
    try:
        from agent_waybill_agentic_loggs import graph  # type: ignore
        print("⚠️  Using original agent (RAG-enhanced not available)")
    except Exception as e:
        raise RuntimeError(
            "Failed to import agent graph. "
            "Ensure LOGI_API_URL, LOGI_API_KEY, and OpenAI creds are set."
        ) from e

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(
    title="RAG-Enhanced Waybill Agent API", 
    version="2.0.0",
    description="CPKC Anomaly Detection with RAG (Retrieval-Augmented Generation) capabilities"
)

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
    use_rag: Optional[bool] = True  # Enable/disable RAG enhancement

class CheckResponse(BaseModel):
    waybill_id: str
    result: Any  # whatever the agent returns (usually JSON as a string)
    rag_enhanced: bool = False
    rag_metadata: Optional[Dict[str, Any]] = None

class TraceMessage(BaseModel):
    type: str
    content: Any
    tool_calls: Optional[Any] = None
    name: Optional[str] = None  # for tool messages

class TraceResponse(BaseModel):
    waybill_id: str
    final: Any
    messages: List[TraceMessage]
    rag_enhanced: bool = False
    rag_metadata: Optional[Dict[str, Any]] = None

# -----------------------------
# Helpers
# -----------------------------
def _invoke_agent(waybill_id: str, thread_id: Optional[str], use_rag: bool = True) -> Dict[str, Any]:
    """
    Calls the compiled LangGraph with a single HumanMessage.
    Enhanced with RAG capabilities.
    """
    if use_rag:
        prompt = f"Check waybill {waybill_id} for anomalies using RAG-enhanced analysis. Use search_anomaly_patterns() and get_learned_insights() to enhance your analysis."
    else:
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

def _extract_rag_metadata(out: Dict[str, Any]) -> Dict[str, Any]:
    """Extract RAG-related metadata from the agent response"""
    rag_metadata = {
        "rag_tools_used": [],
        "knowledge_retrieved": False,
        "learning_insights_used": False
    }
    
    # Check if RAG tools were used
    for msg in out.get("messages", []):
        if isinstance(msg, ToolMessage):
            if "search_anomaly_patterns" in msg.name or "get_learned_insights" in msg.name:
                rag_metadata["rag_tools_used"].append(msg.name)
                rag_metadata["knowledge_retrieved"] = True
                if "get_learned_insights" in msg.name:
                    rag_metadata["learning_insights_used"] = True
    
    return rag_metadata

# -----------------------------
# Endpoints
# -----------------------------
@app.post("/api/anomalies", response_model=CheckResponse)
def anomalies(
    req: RunRequest,
    status: str = Query(..., description="Anomaly status filter (e.g. NEW)"),
):
    """
    Runs the RAG-enhanced agent and returns the final model verdict.
    Now mounted at /api/anomalies?status=NEW
    """
    if status.upper() != "NEW":
        raise HTTPException(status_code=400, detail="Only status=NEW is supported right now")

    out = _invoke_agent(req.waybill_id, req.thread_id, req.use_rag)
    final_text = _final_ai_text(out)
    rag_metadata = _extract_rag_metadata(out)
    
    return CheckResponse(
        waybill_id=req.waybill_id, 
        result=final_text,
        rag_enhanced=req.use_rag,
        rag_metadata=rag_metadata
    )

@app.post("/check", response_model=CheckResponse)
def check(req: RunRequest):
    """
    Runs the RAG-enhanced agent and returns only the final model verdict (concise).
    """
    out = _invoke_agent(req.waybill_id, req.thread_id, req.use_rag)
    final_text = _final_ai_text(out)
    rag_metadata = _extract_rag_metadata(out)
    
    return CheckResponse(
        waybill_id=req.waybill_id, 
        result=final_text,
        rag_enhanced=req.use_rag,
        rag_metadata=rag_metadata
    )

@app.post("/trace", response_model=TraceResponse)
def trace(req: RunRequest):
    """
    Runs the RAG-enhanced agent and returns the full trace (all messages + final).
    Useful for debugging/observability.
    """
    out = _invoke_agent(req.waybill_id, req.thread_id, req.use_rag)
    final_text = _final_ai_text(out)
    messages = _serialize_messages(out)
    rag_metadata = _extract_rag_metadata(out)
    
    return TraceResponse(
        waybill_id=req.waybill_id, 
        final=final_text, 
        messages=messages,
        rag_enhanced=req.use_rag,
        rag_metadata=rag_metadata
    )

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "rag_enhanced": True,
        "version": "2.0.0"
    }

@app.get("/rag/status")
def rag_status():
    """RAG system status endpoint"""
    try:
        from rag.core.quick_rag import QuickRAG
        from rag.learning.simple_learning import SimpleLearning
        
        rag = QuickRAG()
        learning = SimpleLearning()
        
        return {
            "rag_available": True,
            "knowledge_base": rag.get_knowledge_stats(),
            "learning_stats": learning.learned_patterns,
            "status": "operational"
        }
    except Exception as e:
        return {
            "rag_available": False,
            "error": str(e),
            "status": "error"
        }

@app.post("/rag/feedback")
def submit_rag_feedback(
    anomaly_id: str,
    anomaly_type: str,
    resolution_success: bool,
    effectiveness_score: float
):
    """Submit feedback to improve RAG learning"""
    try:
        from rag.tools.rag_tools import add_resolution_feedback
        
        result = add_resolution_feedback.invoke({
            "anomaly_id": anomaly_id,
            "anomaly_type": anomaly_type,
            "resolution_success": resolution_success,
            "resolution_time_minutes": 0,
            "effectiveness_score": effectiveness_score
        })
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting RAG-Enhanced Waybill Agent API Server")
    print("📊 RAG capabilities: Enhanced anomaly detection with historical patterns")
    print("🔗 API Documentation: http://localhost:8080/docs")
    uvicorn.run("rag_enhanced_api_server:app", host="localhost", port=8080, reload=True)
