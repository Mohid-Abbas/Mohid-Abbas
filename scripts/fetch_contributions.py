import json, re
from datetime import datetime, timezone
from pathlib import Path
import requests
from bs4 import BeautifulSoup

USERNAME = "Mohid-Abbas"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path(__file__).resolve().parents[1] / "data/contributions.json"

r = requests.get(URL, headers={"User-Agent": "Mohid-Abbas-profile-readme/1.0"}, timeout=30)
r.raise_for_status()
soup = BeautifulSoup(r.text, "html.parser")

days = []
for cell in soup.select("td.ContributionCalendar-day"):
    date = cell.get("data-date")
    level = int(cell.get("data-level") or 0)
    label = cell.get("aria-label", "")
    match = re.search(r"([\d,]+)\s+contribution", label)
    count = int(match.group(1).replace(",", "")) if match else 0
    if date:
        days.append({"date": date, "level": level, "count": count, "label": label})

OUT.write_text(json.dumps({"username": USERNAME, "updated_at": datetime.now(timezone.utc).isoformat(), "days": days}, indent=2), encoding="utf-8")
print(f"Saved {len(days)} contribution days.")
