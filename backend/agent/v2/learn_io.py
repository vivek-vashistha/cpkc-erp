# learn_io.py
# Minimal JSONL appenders for anomalies, feedback, outcomes.
import json, time, os

ANOMALY_LOG = os.getenv("ANOMALY_LOG", "anomalies.jsonl")
FEEDBACK_LOG = os.getenv("FEEDBACK_LOG", "feedback.jsonl")
OUTCOME_LOG  = os.getenv("OUTCOME_LOG",  "outcomes.jsonl")


def append_jsonl(path, obj):
    obj = dict(obj)
    obj["_ts"] = int(time.time() * 1000)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def log_anomaly(anomaly: dict):
    append_jsonl(ANOMALY_LOG, anomaly)


def log_feedback(obj: dict):
    append_jsonl(FEEDBACK_LOG, obj)


def log_outcome(obj: dict):
    append_jsonl(OUTCOME_LOG, obj)