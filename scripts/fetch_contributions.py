import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests

USERNAME = "Mohid-Abbas"
API = "https://api.github.com/graphql"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/contributions.json"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            contributionLevel
            color
          }
        }
      }
    }
  }
}
"""

token = os.environ.get("GITHUB_TOKEN")
if not token:
    raise RuntimeError("GITHUB_TOKEN is required. The GitHub Action supplies it automatically.")

r = requests.post(
    API,
    json={"query": QUERY, "variables": {"login": USERNAME}},
    headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    },
    timeout=30,
)
r.raise_for_status()
payload = r.json()
if payload.get("errors"):
    raise RuntimeError(json.dumps(payload["errors"], indent=2))

calendar = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]

def level(value: str) -> int:
    return {
        "NONE": 0,
        "FIRST_QUARTILE": 1,
        "SECOND_QUARTILE": 2,
        "THIRD_QUARTILE": 3,
        "FOURTH_QUARTILE": 4,
    }.get(value, 0)

days = []
for week in calendar["weeks"]:
    for day in week["contributionDays"]:
        days.append({
            "date": day["date"],
            "count": day["contributionCount"],
            "level": level(day["contributionLevel"]),
            "color": day["color"],
        })

if len(days) < 300:
    raise RuntimeError(f"GitHub returned only {len(days)} days; refusing to replace the graph.")

result = {
    "username": USERNAME,
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "total": calendar["totalContributions"],
    "days": days,
}
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(f"Fetched {len(days)} days; total={result['total']}.")
