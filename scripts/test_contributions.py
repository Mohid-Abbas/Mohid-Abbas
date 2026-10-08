import json
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "data/contributions.json"
data = json.loads(p.read_text())
assert isinstance(data.get("days"), list)
assert "total" in data
print("Contribution data structure: OK")
