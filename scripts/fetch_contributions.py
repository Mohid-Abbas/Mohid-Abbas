import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "Mohid-Abbas"
URL = f"https://github.com/users/{USERNAME}/contributions"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/contributions.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Mohid-Abbas-profile-readme/2.0)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

r = requests.get(URL, headers=HEADERS, timeout=30)
r.raise_for_status()

soup = BeautifulSoup(r.text, "html.parser")

# GitHub currently exposes the calendar as <td class="ContributionCalendar-day" ...>.
cells = soup.select("td.ContributionCalendar-day[data-date][data-level]")
if not cells:
    raise RuntimeError(
        "GitHub returned no contribution cells. Refusing to overwrite the existing graph."
    )

# Exact counts are stored in <tool-tip for="CELL_ID">... contributions ...</tool-tip>.
tooltips = {}
for tip in soup.find_all("tool-tip"):
    cell_id = tip.get("for")
    if not cell_id:
        continue
    text = tip.get_text(" ", strip=True)
    m = re.search(r"([\d,]+)\s+contribution", text)
    if m:
        tooltips[cell_id] = int(m.group(1).replace(",", ""))

# If GitHub changes the tooltip markup, level/date data is still useful.
days = []
for cell in cells:
    date = cell.get("data-date")
    level = max(0, min(4, int(cell.get("data-level", "0"))))
    count = tooltips.get(cell.get("id"), 0 if level == 0 else None)
    days.append({"date": date, "level": level, "count": count})

# Prefer the exact total shown by GitHub's contribution page.
total = None
heading = soup.get_text(" ", strip=True)
m = re.search(r"([\d,]+) contributions? in the last year", heading)
if m:
    total = int(m.group(1).replace(",", ""))

payload = {
    "username": USERNAME,
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "total": total,
    "days": days,
}

OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
print(f"Saved {len(days)} contribution days; total={total}.")
