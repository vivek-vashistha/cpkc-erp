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
pip install langgraph langchain-core langchain-openai openai python-dotenv requests
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

## What the Agent Does

The agent:
1. Extracts waybill IDs from user input
2. Fetches waybill events and metadata using API tools
3. Validates event sequence: Created → Picked Up → In Transit → At Border → Arrived → Delivered → Closed
4. Identifies anomalies (missing steps, out-of-sequence timestamps, etc.)
5. Returns a JSON report with findings

## Example Usage

The agent will automatically test with waybill `WB3005` when run directly, or you can interact with it through the LangGraph dev server interface.

## Test Use Cases

The following waybill IDs can be used to test different anomaly scenarios:

| Waybill ID | Test Case | Description |
|------------|-----------|-------------|
| `WB3000` | Missing Closed Event | Tests detection of missing "Closed" event at the end of the sequence |
| `WB3013` | No Issues | Valid sequence with no anomalies - should pass all checks |
| `WB3005` | Sequence Error | Contains sequence errors and missing events |
| `WB3019` | CSN ID Mismatch | Tests detection of inconsistent CSN ID values across events |