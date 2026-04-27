import json
import os

class StateStore:
    def __init__(self, path="data/state.json"):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def load(self, default_state):
        if not os.path.exists(self.path):
            self.save(default_state)
            return default_state
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = default_state.copy()
            merged.update(data)
            return merged
        except Exception:
            self.save(default_state)
            return default_state

    def save(self, state):
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp, self.path)
