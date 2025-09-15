# bandit.py
# Thompson-sampling bandit with Beta priors per (anomaly_type|lane|commodity) bucket.
import json, os, random
from typing import Dict, List

STATE_PATH = os.getenv("BANDIT_STATE", "bandit_state.json")


def _load():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r") as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}


def _save(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f)


def bucket_key(ctx: Dict) -> str:
    return f'{ctx.get("anomaly_type", "?")}|{ctx.get("lane_key", "?")}|{ctx.get("commodity", "?")}'


class FixBandit:
    def __init__(self):
        self.state = _load()

    def select(self, ctx: Dict, arms: List[Dict]) -> List[Dict]:
        b = bucket_key(ctx)
        self.state.setdefault(b, {})
        scored = []
        for arm in arms:
            name = arm["arm"] + "|" + json.dumps(arm.get("params", {}), sort_keys=True)
            ab = self.state[b].setdefault(name, {"a": 1.0, "b": 1.0})
            sample = random.betavariate(ab["a"], ab["b"])  # Thompson sample
            scored.append((sample, name, arm))
        scored.sort(reverse=True, key=lambda x: x[0])
        return [arm for _, __, arm in scored]

    def update(self, ctx: Dict, chosen_arm: Dict, reward: float):
        b = bucket_key(ctx)
        name = chosen_arm["arm"] + "|" + json.dumps(chosen_arm.get("params", {}), sort_keys=True)
        ab = self.state.setdefault(b, {}).setdefault(name, {"a": 1.0, "b": 1.0})
        # map reward [-1,1] → [0,1]
        p = max(0.0, min(1.0, (reward + 1) / 2))
        ab["a"] += p
        ab["b"] += (1 - p)
        _save(self.state)