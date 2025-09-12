# CPKC ERP System

A comprehensive Enterprise Resource Planning system with a LangGraph-based waybill QA agent backend and a modern Next.js frontend portal.

## Project Structure

This repository contains two main components:

- **Backend**: LangGraph-based agent for waybill anomaly detection (located in `backend/agent/`)
- **Frontend**: Next.js ERP portal for CPKC operations (located in `cpkc-erp-portal/`)

## Backend Setup (Waybill QA Agent)

The backend agent analyzes waybill shipments for anomalies and validates event sequences.

### 1. Navigate to Backend Directory

```bash
cd backend/agent
```

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install langgraph langchain-core langchain-openai openai python-dotenv requests fastapi pydantic python-multipart uvicorn[standard]
```
```bash
pip install -U "langgraph-cli[inmem]"
```

### 4. Environment Configuration

Create a `.env` file in the `backend/agent/` directory with the following variables:
```
OPENAI_API_KEY='sk-proj-0lxv78RPiB....'
OPENAI_MODEL = 'gpt-4o'
LANGSMITH_API_KEY ='lsv2_pt_fd8e...'
LOGI_API_URL=https://script.google.com/macros/s/AKfycbwc7rrc....JKJS/exec
LOGI_API_KEY=s....y
LOGI_TIMEOUT=30            # seconds per request (default 30)
LOGI_DEFAULT_LIMIT=50      # default pagination size for list endpoints (e.g., waybills)
LOGI_DEBUG=false           # "true" to print request/response summaries
TEST_WAYBILL_ID=WB3005
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=CPKC-ERP-waybill-dev
```

## Running the Backend Agent

Make sure you're in the `backend/agent/` directory and have activated the virtual environment.

### Option 1: Direct Python Execution
```bash
python agent_waybill_agentic_loggs.py
```

### Option 2: Using LangGraph Dev Server
```bash
langgraph dev
```

### Option 3: FastAPI Server
```bash
python new_waybill_api_server.py
```

The API server will start on `http://localhost:8080` with the following endpoints:

- **POST** `/api/anomalies?status=NEW` - Check waybill for anomalies (requires status parameter)
- **POST** `/check` - Simple waybill check endpoint
- **POST** `/trace` - Full trace with all messages (useful for debugging)
- **GET** `/health` - Health check endpoint

#### API Usage Examples

**Check for anomalies:**
```bash
curl -X POST "http://localhost:8080/api/anomalies?status=NEW" \
  -H "Content-Type: application/json" \
  -d '{"waybill_id": "WB3005"}'
```

**Simple check:**
```bash
curl -X POST "http://localhost:8080/check" \
  -H "Content-Type: application/json" \
  -d '{"waybill_id": "WB3005"}'
```

**Get full trace:**
```bash
curl -X POST "http://localhost:8080/trace" \
  -H "Content-Type: application/json" \
  -d '{"waybill_id": "WB3005"}'
```

**Health check:**
```bash
curl http://localhost:8080/health
```

#### API Response Format

All endpoints return JSON responses:

```json
{
  "waybill_id": "WB3005",
  "result": "Agent analysis result as string"
}
```

The `/trace` endpoint additionally includes a `messages` array with the full conversation history.

## Frontend Setup (CPKC ERP Portal)

The frontend is a modern Next.js application for managing CPKC rail operations.

### 1. Navigate to Frontend Directory

```bash
cd cpkc-erp-portal
```

### 2. Follow Frontend Setup Instructions

Please refer to the detailed setup instructions in the frontend README file:

📖 **[Frontend Setup Guide](./cpkc-erp-portal/README.md)**

The frontend includes:
- Dashboard with key metrics and activities
- Waybill management and tracking
- Contract management
- Asset inventory and status tracking
- Operations logging
- Anomaly detection and management
- Analytics and reporting
- AI-powered chat support

## What the Backend Agent Does

The agent:
1. Extracts waybill IDs from user input
2. Fetches waybill events and metadata using API tools
3. Validates event sequence: Created → Picked Up → In Transit → At Border → Arrived → Delivered → Closed
4. Identifies anomalies (missing steps, out-of-sequence timestamps, etc.)
5. Returns a JSON report with findings

## Example Usage

### Backend Agent Usage

Make sure you're in the `backend/agent/` directory with the virtual environment activated.

#### Direct Execution
The agent will automatically test with waybill `WB3005` when run directly:
```bash
cd backend/agent
python agent_waybill_agentic_loggs.py
```

#### LangGraph Dev Server
Interact with the agent through the LangGraph dev server interface:
```bash
cd backend/agent
langgraph dev
```

#### API Server
Use the REST API for programmatic access:
```bash
# Navigate to backend directory
cd backend/agent

# Start the server
python new_waybill_api_server.py

# Test with curl
curl -X POST "http://localhost:8080/check" \
  -H "Content-Type: application/json" \
  -d '{"waybill_id": "WB3005"}'
```

### Frontend Portal Usage

For the frontend portal setup and usage, please refer to the detailed instructions in:
📖 **[Frontend Setup Guide](./cpkc-erp-portal/README.md)**

### Python Client Example
```python
import requests

# Check waybill for anomalies
response = requests.post(
    "http://localhost:8080/api/anomalies?status=NEW",
    json={"waybill_id": "WB3005"}
)
result = response.json()
print(f"Analysis for {result['waybill_id']}: {result['result']}")
```

## Test Use Cases

The following waybill IDs can be used to test different anomaly scenarios:

| Waybill ID | Test Case | Description |
|------------|-----------|-------------|
| `WB3000` | Missing Closed Event | Tests detection of missing "Closed" event at the end of the sequence |
| `WB3013` | No Issues | Valid sequence with no anomalies - should pass all checks |
| `WB3005` | Sequence Error | Contains sequence errors and missing events |
| `WB3019` | CSN ID Mismatch | Tests detection of inconsistent CSN ID values across events |