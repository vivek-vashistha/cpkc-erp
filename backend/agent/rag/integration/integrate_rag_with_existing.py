# Integration Script for Existing CPKC Agent
"""
This script integrates RAG capabilities into the existing agent_waybill_agentic_loggs.py
while maintaining full compatibility with the current system.
"""

import os
import shutil
from datetime import datetime

def backup_existing_agent():
    """Create backup of existing agent file"""
    original_file = "agent_waybill_agentic_loggs.py"
    backup_file = f"agent_waybill_agentic_loggs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    
    if os.path.exists(original_file):
        shutil.copy2(original_file, backup_file)
        print(f"✅ Backup created: {backup_file}")
        return backup_file
    else:
        print(f"⚠️  Original file not found: {original_file}")
        return None

def create_rag_integrated_agent():
    """Create RAG-integrated version of the existing agent"""
    
    # Read the existing agent file
    with open("agent_waybill_agentic_loggs.py", "r") as f:
        existing_content = f.read()
    
    # Create the RAG-integrated version
    rag_integrated_content = existing_content
    
    # Add RAG imports after existing imports
    rag_imports = '''
# RAG Integration Imports
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from rag.tools.rag_tools import RAG_TOOLS
from rag.learning.simple_learning import get_learned_insights, get_learning_stats
from rag.integration.rag_integration_for_existing import get_rag_enhanced_anomaly_detector, enhance_anomalies_with_rag
'''
    
    # Insert RAG imports after the existing imports
    insert_point = existing_content.find("from others.prompts.system_prompt_13_09_2025 import SYSTEM_13_09_2025 as SYSTEM")
    if insert_point != -1:
        rag_integrated_content = (
            existing_content[:insert_point] + 
            rag_imports + "\n" + 
            existing_content[insert_point:]
        )
    
    # Update the TOOLS dictionary to include RAG tools
    tools_update = '''
# Enhanced Tools with RAG
ENHANCED_TOOLS = {
    **TOOLS,  # Include existing tools
    **RAG_TOOLS,  # Add RAG tools
    "get_learned_insights": get_learned_insights,
    "get_learning_stats": get_learning_stats,
}
'''
    
    # Replace the TOOLS definition
    tools_start = existing_content.find("TOOLS = {")
    tools_end = existing_content.find("}", tools_start) + 1
    
    if tools_start != -1 and tools_end != -1:
        rag_integrated_content = (
            existing_content[:tools_start] + 
            tools_update + 
            existing_content[tools_end:]
        )
    
    # Update the LLM binding to use enhanced tools
    llm_update = '''
llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0).bind_tools(list(ENHANCED_TOOLS.values()))
'''
    
    # Replace the LLM definition
    llm_start = existing_content.find("llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0).bind_tools(list(TOOLS.values()))")
    if llm_start != -1:
        llm_end = existing_content.find("\n", llm_start)
        rag_integrated_content = (
            existing_content[:llm_start] + 
            llm_update + 
            existing_content[llm_end:]
        )
    
    # Update the tools_node to use enhanced tools
    tools_node_update = '''
        if name not in ENHANCED_TOOLS:
            result = {"error": f"Unknown tool: {name}"}
        else:
            try:
                result = ENHANCED_TOOLS[name].invoke(args)
            except Exception as e:
                result = {"error": str(e)}
'''
    
    # Replace the tools_node logic
    tools_node_start = existing_content.find("if name not in TOOLS:")
    if tools_node_start != -1:
        tools_node_end = existing_content.find("result = TOOLS[name].invoke(args)", tools_node_start)
        if tools_node_end != -1:
            tools_node_end = existing_content.find("}", tools_node_end) + 1
            rag_integrated_content = (
                existing_content[:tools_node_start] + 
                tools_node_update + 
                existing_content[tools_node_end:]
            )
    
    # Write the RAG-integrated agent
    with open("agent_waybill_agentic_loggs_rag_enhanced.py", "w") as f:
        f.write(rag_integrated_content)
    
    print("✅ RAG-integrated agent created: agent_waybill_agentic_loggs_rag_enhanced.py")
    return "agent_waybill_agentic_loggs_rag_enhanced.py"

def create_rag_enhanced_system_prompt():
    """Create RAG-enhanced system prompt"""
    
    prompt_content = '''
# RAG-Enhanced System Prompt for CPKC Agent
# This prompt integrates RAG capabilities while maintaining compatibility

RAG_ENHANCED_SYSTEM = """
You are a logistics QA assistant with access to a comprehensive knowledge base of anomaly patterns, 
resolution strategies, and business rules. You have enhanced capabilities through RAG (Retrieval-Augmented Generation).

### TASK
The user provides a waybill ID (e.g., "WB3005", possibly embedded in a sentence).
1) Extract waybill_id (regex: \bWB\d+\b).
2) BEFORE analyzing, call search_anomaly_patterns("anomaly detection", "waybill analysis") to get relevant knowledge.
3) Call tools as needed to fetch events and waybill metadata.
4) Use get_learned_insights() to get confidence scores based on historical data.
5) Validate the required sequence (exactly and in order):
   Canonical order (must be chronological):
    Created → Picked Up → In Transit → At Border → Arrived → Delivered → Closed

   Terminal events:
    - Closed (always terminal)
    - Cancelled (terminal; mutually exclusive with Delivered)

   Allowed event types:
    ["Created","Picked Up","In Transit","At Border","Arrived","Delivered","Closed","Cancelled"]

6) Find anomalies using RAG-enhanced analysis:
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

### RAG ENHANCEMENT WORKFLOW
1. ALWAYS call search_anomaly_patterns("anomaly detection", "waybill analysis") before analyzing
2. Use get_learned_insights() for each anomaly type you detect
3. Reference retrieved patterns, rules, and historical cases in your analysis
4. Apply proven resolution strategies from historical cases
5. Use enhanced confidence scores based on historical success rates

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
  "confidence": number,                   // 0.0–1.0 (enhanced by RAG historical data)
  "suggested_fix": {
    "actions": [
      {
        "name": "INSERT_EVENT"|"REORDER_EVENTS"|"CORRECT_EVENT_TS"|"REVIEW_TERMINAL_STATE"|
             "MERGE_DUPLICATE_EVENTS"|"TRIM_POST_TERMINAL_EVENTS"|"MAP_EVENT_TYPE"|
             "SET_CARID"|"SET_CSNID"|null,
        "args": [ { "key": string, "value": string } ],
        "rationale": string    // detailed human-friendly description enhanced with RAG context
      }
    ]
  },
  "status": "NEW"|"UNCHANGED",
  "rpa_status": "Auto Fix"|"Manual Review Required"|"Needs Data"|null,
  "created_ts": string,                   // ISO 8601 UTC with trailing "Z"
  "updated_ts": string,                   // same format; for a new record equals created_ts
  "details": string,                     // Detailed human-friendly description enhanced with RAG context
  "needs_confirmation": boolean         // true if human intervention is required
}

- IDs: generate as anomaly_{epochMillis}_{10-char lowercase a-z0-9}.
- Timestamps: generate current UTC as ISO 8601 ending with "Z".
- If there are NO anomalies, return [] exactly.
- Set "needs_confirmation": true when any action is suggested; otherwise false.
- Use double quotes everywhere. No trailing commas. No extra keys.
- ENHANCE confidence scores using historical data from RAG
- ENHANCE suggested fixes with proven strategies from historical cases
- ENHANCE details with context from retrieved knowledge

### STYLE
- Do all reasoning internally; OUTPUT MUST BE JSON ARRAY ONLY.
- Do not wrap in markdown backticks. Do not add explanations, headings, or bullets.
- Use RAG knowledge to enhance your analysis but maintain the exact output format.
"""
'''
    
    with open("rag_enhanced_system_prompt.py", "w") as f:
        f.write(prompt_content)
    
    print("✅ RAG-enhanced system prompt created: rag_enhanced_system_prompt.py")

def create_integration_instructions():
    """Create integration instructions"""
    
    instructions = '''
# RAG Integration Instructions for Existing CPKC Agent

## Files Created:
1. `agent_waybill_agentic_loggs_rag_enhanced.py` - RAG-integrated version of your agent
2. `rag_enhanced_system_prompt.py` - RAG-enhanced system prompt
3. `rag_integration_for_existing.py` - RAG integration utilities

## Integration Options:

### Option 1: Use RAG-Enhanced Agent (Recommended)
```python
# Replace the import in your API server
from agent_waybill_agentic_loggs_rag_enhanced import graph

# The rest of your code remains the same
```

### Option 2: Manual Integration
1. Add RAG imports to your existing agent:
```python
from rag.tools.rag_tools import RAG_TOOLS
from rag.learning.simple_learning import get_learned_insights, get_learning_stats
```

2. Update your TOOLS dictionary:
```python
ENHANCED_TOOLS = {
    **TOOLS,  # Include existing tools
    **RAG_TOOLS,  # Add RAG tools
    "get_learned_insights": get_learned_insights,
    "get_learning_stats": get_learning_stats,
}
```

3. Update your LLM binding:
```python
llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0).bind_tools(list(ENHANCED_TOOLS.values()))
```

4. Update your tools_node to use ENHANCED_TOOLS instead of TOOLS

### Option 3: Use RAG-Enhanced System Prompt
Replace your system prompt with the RAG-enhanced version:
```python
from rag_enhanced_system_prompt import RAG_ENHANCED_SYSTEM
# Use RAG_ENHANCED_SYSTEM instead of SYSTEM_13_09_2025
```

## Testing the Integration:

### Test 1: Basic RAG Functionality
```python
from rag.integration.rag_integration_for_existing import get_rag_enhanced_anomaly_detector

detector = get_rag_enhanced_anomaly_detector()
anomaly = detector.get_rag_enhanced_anomaly(
    waybill_id="WB3005",
    anomaly_type="MISSING_STEP",
    base_confidence=0.8,
    base_details="Missing 'Closed' event"
)
print(anomaly)
```

### Test 2: Enhanced Anomaly Detection
```python
from rag.integration.rag_integration_for_existing import enhance_anomalies_with_rag

# Your existing anomalies
existing_anomalies = [
    {
        "id": "anomaly_123",
        "waybill_id": "WB3005",
        "type": "MISSING_STEP",
        "confidence": 0.8,
        "details": "Missing 'Closed' event"
    }
]

# Enhance with RAG
enhanced_anomalies = enhance_anomalies_with_rag(existing_anomalies, "WB3005")
print(enhanced_anomalies)
```

### Test 3: API Server Integration
```python
# In your new_waybill_api_server.py, change the import:
from agent_waybill_agentic_loggs_rag_enhanced import graph

# Everything else remains the same
```

## Key Benefits:
1. **Enhanced Confidence**: RAG provides confidence scores based on historical data
2. **Better Fixes**: Suggested fixes include proven strategies from historical cases
3. **Context-Aware**: Analysis considers similar past anomalies
4. **Learning**: System learns from new resolutions and feedback
5. **Backward Compatible**: Works with existing API and data structures

## Next Steps:
1. Test the RAG-enhanced agent with your existing waybill data
2. Monitor the enhanced confidence scores and fix suggestions
3. Add more domain-specific knowledge to the RAG system
4. Collect feedback from resolutions to improve learning

## Troubleshooting:
- If you get import errors, ensure the `rag` package is in your Python path
- If tools don't work, check that ENHANCED_TOOLS is properly defined
- If confidence scores seem off, verify the learning system has historical data
- If fixes aren't enhanced, check that the knowledge base has relevant patterns

## Support:
- Check the demo scripts in `rag/demos/` for examples
- Review the integration utilities in `rag/integration/`
- Read the comprehensive documentation in `rag/README.md`
'''
    
    with open("RAG_INTEGRATION_INSTRUCTIONS.md", "w") as f:
        f.write(instructions)
    
    print("✅ Integration instructions created: RAG_INTEGRATION_INSTRUCTIONS.md")

def main():
    """Main integration function"""
    print("🔧 RAG Integration for Existing CPKC Agent")
    print("=" * 60)
    
    # Create backup
    backup_file = backup_existing_agent()
    
    # Create RAG-integrated agent
    rag_agent_file = create_rag_integrated_agent()
    
    # Create RAG-enhanced system prompt
    create_rag_enhanced_system_prompt()
    
    # Create integration instructions
    create_integration_instructions()
    
    print("\n" + "=" * 60)
    print("✅ RAG Integration Complete!")
    print("\nFiles Created:")
    print(f"1. {rag_agent_file} - RAG-integrated agent")
    print("2. rag_enhanced_system_prompt.py - Enhanced system prompt")
    print("3. RAG_INTEGRATION_INSTRUCTIONS.md - Integration guide")
    
    if backup_file:
        print(f"\n📁 Original agent backed up to: {backup_file}")
    
    print("\n🚀 Next Steps:")
    print("1. Test the RAG-enhanced agent:")
    print("   python agent_waybill_agentic_loggs_rag_enhanced.py")
    print("2. Update your API server to use the enhanced agent")
    print("3. Test with your existing waybill data")
    print("4. Monitor enhanced confidence scores and fix suggestions")

if __name__ == "__main__":
    main()
