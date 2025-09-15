# retrieve.py
# Cheap retrieval: recent, same-bucket neighbors, basic feature-distance sort.
import json
from typing import List, Dict


def _load_recent(path: str = "anomalies.jsonl", limit: int = 200) -> List[dict]:
    items = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    items.append(json.loads(line))
                except Exception:
                    continue
    except FileNotFoundError:
        pass
    return items[-limit:]


def retrieve_similar(ctx: Dict, features: Dict, k: int = 4) -> List[Dict]:
    bucket = f'{ctx.get("anomaly_type", "?")}|{ctx.get("lane_key", "?")}|{ctx.get("commodity", "?")}'
    items = [x for x in _load_recent() if x.get("bucket") == bucket]

    def delta(a, b):
        if a is None or b is None:
            return 0
        return abs(a - b)

    def score(it):
        f = it.get("features", {})
        s = 0
        s -= delta(features.get("dep_delay_min"), f.get("dep_delay_min")) / 60.0
        s -= delta(features.get("arr_delay_min"), f.get("arr_delay_min")) / 60.0
        return s

    items.sort(key=score, reverse=True)
    out = []
    for it in items[:k]:
        out.append({
            "anomaly_type": it.get("ctx", {}).get("anomaly_type"),
            "label": it.get("label", "?"),
            "final_fix": it.get("final_fix"),
            "notes": it.get("notes", ""),
        })
    return out