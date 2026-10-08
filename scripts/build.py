"""Entry point.

    python scripts/build.py            # live: fetch from GitHub, regenerate everything
    python scripts/build.py --offline  # rebuild from the last data/profile.json (no network)
    python scripts/build.py --demo     # invented demo data, for previewing design changes
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import demo_data
import fetch_data
import readme
import stats
import svg_assets
from common import DATA, ROOT, load_config


def pick_repos(data: dict, cfg: dict) -> list[dict]:
    login = data["login"].lower()
    pool = data["pinned"] if cfg["projects"]["source"] == "pinned" and data["pinned"] else data["recent"]
    return [r for r in pool if r["name"].lower() != login][: cfg["projects"]["max"]]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args()

    cfg = load_config()
    if a.demo:
        data = demo_data.make()
        print("!! DEMO DATA — not your real activity", file=sys.stderr)
    elif a.offline:
        data = json.loads(DATA.read_text())
    else:
        login = cfg.get("username") or os.environ.get("GITHUB_REPOSITORY_OWNER", "")
        data = fetch_data.fetch(login)

    st = stats.compute(data)
    repos = pick_repos(data, cfg)
    files = svg_assets.build_all(data, st, cfg, repos)

    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    svg_assets.write_all(files)
    (ROOT / "README.md").write_text(readme.build(cfg, st, files, repos), encoding="utf-8")
    print(f"ok: {len(files)} svgs, {len(repos)} cards, {st['total']} contributions")


if __name__ == "__main__":
    main()
