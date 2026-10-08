"""Everything derived from the raw calendar: totals, streaks, monthly series."""
from __future__ import annotations

from datetime import date


def compute(data: dict) -> dict:
    days = [d for w in data["weeks"] for d in w]
    days.sort(key=lambda d: d["date"])
    active = [d for d in days if d["count"] > 0]

    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)

    # current streak: today may still be empty, so allow it to be skipped
    cur, seq = 0, list(reversed(days))
    if seq and seq[0]["count"] == 0:
        seq = seq[1:]
    for d in seq:
        if d["count"] == 0:
            break
        cur += 1

    # last 12 calendar months, ending with the (partial) current one
    last = date.fromisoformat(days[-1]["date"])
    keys = []
    y, m = last.year, last.month
    for _ in range(12):
        keys.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    keys.reverse()
    totals = {k: 0 for k in keys}
    for d in days:
        dt = date.fromisoformat(d["date"])
        if (dt.year, dt.month) in totals:
            totals[(dt.year, dt.month)] += d["count"]
    months = [{"label": date(y, m, 1).strftime("%b"), "count": c} for (y, m), c in totals.items()]

    return {"total": data.get("total", sum(d["count"] for d in days)),
            "active_days": len(active), "longest_streak": longest, "current_streak": cur,
            "months": months}
