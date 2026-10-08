"""Assemble README.md from README.template.md + generated assets."""
from __future__ import annotations

import hashlib

from common import ROOT, esc

REL = "assets/generated"


def _ver(files: dict[str, str], name: str) -> str:
    return hashlib.sha1(files[name].encode()).hexdigest()[:8]     # cache-buster for GitHub's image proxy


def picture(files: dict[str, str], base: str, alt: str, width: str | None = None) -> str:
    w = f' width="{width}"' if width else ""
    d, l = f"{base}-dark.svg", f"{base}-light.svg"
    return (f'<picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="{REL}/{d}?v={_ver(files, d)}">'
            f'<source media="(prefers-color-scheme: light)" srcset="{REL}/{l}?v={_ver(files, l)}">'
            f'<img alt="{esc(alt)}" src="{REL}/{d}?v={_ver(files, d)}"{w}></picture>')


def build(cfg: dict, st: dict, files: dict[str, str], repos: list[dict]) -> str:
    h = cfg["hero"]
    hero = f'<p align="center">{picture(files, "hero", " ".join(h["headline"]) + " — " + ", ".join(h["rotating"]), "100%")}</p>'

    ln = cfg.get("links", {})
    bits = []
    if ln.get("resume"):
        bits.append(f'<a href="{esc(ln["resume"])}"><b>Résumé</b></a>')
    if ln.get("portfolio"):
        bits.append(f'<a href="{esc(ln["portfolio"])}"><b>Portfolio</b></a>')
    if ln.get("linkedin"):
        bits.append(f'<a href="{esc(ln["linkedin"])}"><b>LinkedIn</b></a>')
    if ln.get("email"):
        bits.append(f'<a href="mailto:{esc(ln["email"])}"><b>{esc(ln["email"])}</b></a>')
    links = f'<p align="center">{"  ·  ".join(bits)}</p>' if bits else ""

    if repos:
        cells = []
        for i, r in enumerate(repos):
            alt = (r["name"] + ": " + r["description"])[:200]
            cells.append('<a href="' + esc(r["url"]) + '">' + picture(files, "card-" + str(i), alt, "49%") + "</a>")
        rows = ["&nbsp;".join(cells[i:i + 2]) for i in range(0, len(cells), 2)]
        projects = "\n\n".join(f'<p align="center">{r}</p>' for r in rows)
    else:
        projects = "_Pin a few repositories on GitHub and they will appear here automatically._"

    stack = f'<p align="center">{picture(files, "stack", "Stack: " + "; ".join(g["label"] + " – " + ", ".join(g["items"]) for g in cfg["stack"]), "100%")}</p>'
    act_alt = str(st["total"]) + " contributions in the last year, " + str(st["active_days"]) + " active days"
    activity = '<p align="center">' + picture(files, "activity", act_alt, "100%") + "</p>"
    charts = [picture(files, "months", "Contributions by month, last 12 months", "49%")]
    if "languages-dark.svg" in files:
        charts.insert(0, picture(files, "languages", "Top languages by code size", "49%"))
    insights = '<p align="center">' + "&nbsp;".join(charts) + "</p>"

    tpl = (ROOT / "README.template.md").read_text(encoding="utf-8")
    out = (tpl.replace("{{hero}}", hero).replace("{{links}}", links).replace("{{projects}}", projects)
              .replace("{{stack}}", stack).replace("{{activity}}", activity).replace("{{insights}}", insights))
    return out
