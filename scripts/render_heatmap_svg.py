import json
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "data/contributions.json").read_text(encoding="utf-8"))
days = data.get("days", [])
if not days:
    raise RuntimeError("No contribution data available. Run fetch_contributions.py first.")

by_date = {d["date"]: d for d in days}
valid_dates = sorted(by_date)
last = datetime.strptime(valid_dates[-1], "%Y-%m-%d").date()
end = last + timedelta(days=(6 - last.weekday()) % 7)
start = end - timedelta(weeks=52)

palette = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

cells = []
for col in range(53):
    for row in range(7):
        day = start + timedelta(days=col * 7 + row)
        item = by_date.get(day.isoformat(), {})
        level = max(0, min(4, int(item.get("level", 0))))
        x, y = 74 + col * 15, 45 + row * 15

        # Slow, repeating reveal. Each full cycle is about 8 seconds.
        delay = (col * 7 + row) * 0.012
        cells.append(
            f'''<rect x="{x}" y="{y}" width="11" height="11" rx="3" fill="{palette[level]}" opacity="0.18">
  <animate attributeName="opacity" values="0.18;1;0.55;1" dur="8s" begin="{delay:.3f}s" repeatCount="indefinite"/>
</rect>'''
        )

count = data.get("total")
count_text = f"{count:,} contributions" if isinstance(count, int) else "contributions"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="185" viewBox="0 0 900 185">
<rect width="900" height="185" rx="12" fill="#0d1117"/>
<text x="18" y="24" fill="#39d353" font-family="monospace" font-size="12">&gt; ./contributions.sh</text>
<text x="690" y="24" fill="#8b949e" font-family="monospace" font-size="12">{count_text}</text>
<g font-family="monospace" font-size="10" fill="#8b949e">
  <text x="18" y="57">Mon</text><text x="18" y="72">Tue</text><text x="18" y="87">Wed</text>
  <text x="18" y="102">Thu</text><text x="18" y="117">Fri</text><text x="18" y="132">Sat</text><text x="18" y="147">Sun</text>
</g>
<g>{''.join(cells)}</g>
<text x="74" y="172" fill="#8b949e" font-family="monospace" font-size="10">Less</text>
<rect x="112" y="164" width="11" height="11" rx="3" fill="#161b22"/>
<rect x="128" y="164" width="11" height="11" rx="3" fill="#0e4429"/>
<rect x="144" y="164" width="11" height="11" rx="3" fill="#006d32"/>
<rect x="160" y="164" width="11" height="11" rx="3" fill="#26a641"/>
<rect x="176" y="164" width="11" height="11" rx="3" fill="#39d353"/>
<text x="194" y="172" fill="#8b949e" font-family="monospace" font-size="10">More</text>
</svg>'''

(ROOT / "assets/heatmap/contributions.svg").write_text(svg, encoding="utf-8")
print("Rendered animated contribution SVG.")
