# Logistics Waybill QA Agent

A LangGraph-based agent that analyzes waybill shipments for anomalies and validates event sequences.

## Setup

### 1. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install langgraph langchain-core langchain-openai openai python-dotenv requests fastapi>=0.104.0 pydantic>=2.0.0 python-multipart>=0.0.6" uvicorn[standard]>=0.24.0
```
```bash
pip install -U "langgraph-cli[inmem]"
```

### 3. Environment Configuration

Create a `.env` file with the following variables:
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

## Running the Agent

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

## What the Agent Does

The agent:
1. Extracts waybill IDs from user input
2. Fetches waybill events and metadata using API tools
3. Validates event sequence: Created → Picked Up → In Transit → At Border → Arrived → Delivered → Closed
4. Identifies anomalies (missing steps, out-of-sequence timestamps, etc.)
5. Returns a JSON report with findings

## Example Usage

### Direct Execution
The agent will automatically test with waybill `WB3005` when run directly:
```bash
python agent_waybill_agentic_loggs.py
```

### LangGraph Dev Server
Interact with the agent through the LangGraph dev server interface:
```bash
langgraph dev
```

### API Server
Use the REST API for programmatic access:
```bash
# Start the server
python new_waybill_api_server.py

# Test with curl
curl -X POST "http://localhost:8080/check" \
  -H "Content-Type: application/json" \
  -d '{"waybill_id": "WB3005"}'
```

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