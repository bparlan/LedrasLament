"""Generation Gateway — token-tracking for fal.ai API calls.
Advisory only: warns when rights are exhausted but NEVER blocks.
Use case: gate.has_rights(n) before generating; gate.deduct(n) after.
If rights == 0, gateway logs a warning and allows generation to proceed."""
import json
from pathlib import Path
GATE_FILE = Path("gateway.json")
class Gateway:
    def __init__(self, initial_rights=1):
        self.initial = initial_rights
        self.file = GATE_FILE
        self.load()

    def load(self):
        if self.file.exists():
            try:
                data = json.loads(self.file.read_text())
                self.rights = data.get("rights", self.initial)
                self.used = data.get("used", 0)
                self.initial = data.get("initial", self.initial)
            except Exception:
                self.rights = self.initial
                self.used = 0
        else:
            self.rights = self.initial
            self.used = 0

    def save(self):
        self.file.write_text(json.dumps({
            "rights": self.rights,
            "used": self.used,
            "initial": self.initial
        }))

    def has_rights(self, n=1):
        return self.rights >= n

    def deduct(self, n=1):
        if not self.has_rights(n):
            print(f"⚠️  Gateway: rights exhausted ({self.rights}), overdrawing. Used: {self.used + n}")
        self.rights = max(0, self.rights - n)
        self.used += n
        self.save()
        return self.rights

    def get_status(self):
        return {
            "rights": self.rights,
            "used": self.used,
            "initial": self.initial,
            "available": self.has_rights()
        }