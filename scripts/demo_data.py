"""Deterministic DEMO data for local previews (python scripts/build.py --demo).

Shaped like a real profile (quiet months, then a dense stretch) but entirely
invented — never commit demo output as if it were real activity.
"""
from __future__ import annotations

import random
from datetime import date, timedelta


def make(end: date | None = None) -> dict:
    rng = random.Random(7)
    end = end or date(2026, 10, 9)
    start = end - timedelta(days=364)
    start -= timedelta(days=(start.weekday() + 1) % 7)          # back to a Sunday
    days = []
    d = start
    while d <= end:
        wd = (d.weekday() + 1) % 7                               # GitHub: Sunday = 0
        if d < date(2026, 2, 3):
            c = rng.choice([0, 0, 0, 0, 0, 0, 1, 2]) if d >= date(2025, 12, 20) else 0
        else:
            base = 34 if wd not in (0, 6) else 12
            c = 0 if rng.random() < 0.10 else max(0, int(rng.lognormvariate(0, .75) * base * .72))
        days.append({"date": d.isoformat(), "count": c, "weekday": wd})
        d += timedelta(days=1)

    nz = sorted(x["count"] for x in days if x["count"])
    q = [nz[len(nz) * i // 4] for i in (1, 2, 3)] if nz else [1, 2, 3]
    for x in days:
        c = x["count"]
        x["level"] = 0 if c == 0 else 1 if c <= q[0] else 2 if c <= q[1] else 3 if c <= q[2] else 4

    weeks, cur = [], []
    for x in days:
        if x["weekday"] == 0 and cur:
            weeks.append(cur)
            cur = []
        cur.append(x)
    weeks.append(cur)

    def repo(name, desc, lang, topics=(), stars=0, forks=0):
        return {"name": name, "description": desc, "url": f"https://github.com/Mohid-Abbas/{name}",
                "stars": stars, "forks": forks, "language": lang, "topics": list(topics)}

    pinned = [
        repo("synapse-context-aware-companion",
             "Synapse is a context-aware wearable AI companion. ESP32-based locket for gesture control and audio input, paired with a processing hub for real-time speech-to-text.", "Python", ["esp32"]),
        repo("medidash-autonomous-vehicle",
             "MediDash: Autonomous Medical Delivery Robot. An ESP32-powered mobile agent for hospital logistics with FSM-driven navigation and PID-controlled steering.", "C++", ["robotics"], stars=1),
        repo("cmapss-iot-predictive-pipeline",
             "End-to-end ML pipeline for Remaining Useful Life (RUL) prediction on NASA C-MAPSS turbofan engine data.", "Python"),
        repo("explainable-network-intrusion-detection",
             "A production-style NIDS using XGBoost/LightGBM on CIC-IDS2017 to classify network traffic, with SHAP explainability.", "Python"),
        repo("rag-document-assistant",
             "LangGraph-powered reasoning engine, LangChain integration, and a containerized FastAPI backend with ChromaDB vector storage.", "Python"),
        repo("ai-workflow-platform",
             "A high-performance automation ecosystem built on n8n that orchestrates workflows across 15+ services including Gmail, Slack and Notion.", "Python", forks=1),
    ]
    langs = {"Python": 412_000, "C++": 128_000, "JavaScript": 61_000, "C": 24_000,
             "TypeScript": 19_000, "Jupyter Notebook": 900_000}   # last one is filtered out
    return {"demo": True, "login": "Mohid-Abbas", "total": sum(x["count"] for x in days),
            "weeks": weeks, "pinned": pinned, "recent": [], "languages": langs}
