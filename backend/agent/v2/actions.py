# actions.py
# Canonicalize free-text LLM suggestions into a small, typed action space.
import re
from typing import List, Dict

ACTIONS = {"REQUEST_DOC", "ESCALATE_TO", "REASSIGN_CAR", "NOTIFY_CUSTOMER"}


def canonicalize(llm_texts: List[str]) -> List[Dict]:
    arms = []
    for t in llm_texts or []:
        t_low = t.lower()
        if "doc" in t_low or "document" in t_low:
            m = re.search(r"(b13a|b3|nafta|usmca|invoice|packing\s*list)", t_low)
            arms.append({"arm": "REQUEST_DOC", "params": {"doc": m.group(1).upper() if m else "UNKNOWN"}, "raw": t})
        elif "escalat" in t_low or "supervisor" in t_low or "yard" in t_low:
            role = "yard_ops" if "yard" in t_low else "supervisor"
            arms.append({"arm": "ESCALATE_TO", "params": {"role": role}, "raw": t})
        elif "reassign" in t_low or "swap car" in t_low:
            crit = "closest_available" if "closest" in t_low else "any_available"
            arms.append({"arm": "REASSIGN_CAR", "params": {"criteria": crit}, "raw": t})
        elif "notify" in t_low or "inform" in t_low:
            ch = "email" if "email" in t_low else ("sms" if "sms" in t_low else "portal")
            arms.append({"arm": "NOTIFY_CUSTOMER", "params": {"channel": ch}, "raw": t})
    # dedupe by (arm, params)
    seen, out = set(), []
    for a in arms:
        key = (a["arm"], tuple(sorted(a["params"].items())))
        if key not in seen:
            seen.add(key)
            out.append(a)
    return out