"""Generation Gateway — token-based approval for fal_generate.py.
Usage: gate.has_rights(n) before calling generate_stage();
      gate.deduct(n) after successful generation.
If rights == 0, gate blocks."""
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
            raise PermissionError(
                f"Gateway blocked: need {n}, have {self.rights}"
            )
        self.rights -= n
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
