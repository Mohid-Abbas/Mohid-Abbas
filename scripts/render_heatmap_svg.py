import json
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT/"data/contributions.json").read_text(encoding="utf-8"))
days = data.get("days", [])
by_date = {d["date"]: d for d in days}
palette = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
dates = sorted(by_date)
last = datetime.strptime(dates[-1], "%Y-%m-%d").date() if dates else datetime.utcnow().date()
end = last + timedelta(days=(6-last.weekday())%7)
start = end - timedelta(weeks=52)

cells=[]
for col in range(53):
    for row in range(7):
        day=start+timedelta(days=col*7+row)
        item=by_date.get(day.isoformat(), {})
        level=max(0,min(5,int(item.get("level",0))))
        x,y=70+col*15,48+row*15
        delay=(col*7+row)*0.01
        cells.append(f'<rect x="{x}" y="{y}" width="11" height="11" rx="3" fill="{palette[level]}" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur=".35s" fill="freeze"/></rect>')

total=sum(int(d.get("count",0)) for d in days)
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="190" viewBox="0 0 900 190">
<rect width="900" height="190" rx="12" fill="#0d1117"/>
<text x="18" y="25" fill="#39d353" font-family="monospace" font-size="12">&gt; ./contributions.sh</text>
<text x="690" y="25" fill="#8b949e" font-family="monospace" font-size="12">{total:,} contributions</text>
<g font-family="monospace" font-size="10" fill="#8b949e"><text x="18" y="55">Mon</text><text x="18" y="70">Tue</text><text x="18" y="85">Wed</text><text x="18" y="100">Thu</text><text x="18" y="115">Fri</text><text x="18" y="130">Sat</text><text x="18" y="145">Sun</text></g>
<g>{''.join(cells)}</g>
<text x="18" y="170" fill="#8b949e" font-family="monospace" font-size="11">Less</text><text x="825" y="170" fill="#8b949e" font-family="monospace" font-size="11">More</text>
</svg>'''
(ROOT/"assets/heatmap/contributions.svg").write_text(svg, encoding="utf-8")
print("Rendered contribution SVG.")
