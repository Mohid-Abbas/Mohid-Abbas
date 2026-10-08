"""Shared helpers. Standard library only — the workflow needs no pip install."""
from __future__ import annotations

import re
import tomllib
from pathlib import Path
from xml.sax.saxutils import escape as _esc

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "assets" / "generated"
DATA = ROOT / "data" / "profile.json"


def load_config() -> dict:
    with open(ROOT / "config" / "profile.toml", "rb") as f:
        return tomllib.load(f)


def esc(s: object) -> str:
    return _esc(str(s), {'"': "&quot;"})


# Emoji / dingbats render with unpredictable widths inside SVG text → strip.
_EMOJI = re.compile("[\U00010000-\U0010ffff☀-➿⬀-⯿️‍]")


def clean(s: str | None) -> str:
    """Emoji runs become a ' · ' separator so 'Robot 🚑 An ESP32…' stays readable."""
    t = _EMOJI.sub("\x00", s or "")
    t = re.sub(r"\s*\x00+\s*", " · ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return re.sub(r"^(· )+|( ·)+$", "", t).strip()


def first_sentence(s: str) -> str:
    m = re.match(r"(.+?[.!?])(\s|$)", s)
    return m.group(1) if m else s


def wrap(text: str, width: int, max_lines: int) -> list[str]:
    """Greedy word wrap by character count, ellipsis if it doesn't fit."""
    words, lines, cur = text.split(), [], ""
    for i, w in enumerate(words):
        trial = f"{cur} {w}".strip()
        if len(trial) <= width:
            cur = trial
            continue
        lines.append(cur)
        cur = w
        if len(lines) == max_lines:
            break
    else:
        if cur:
            lines.append(cur)
        return lines[:max_lines] or [""]
    # ran out of lines with words left → truncate the last line
    last = lines[max_lines - 1]
    lines = lines[:max_lines]
    lines[-1] = (last[: width - 1].rstrip(" ,.;:") + "…") if len(last) >= width - 1 else last + "…"
    return lines


def fmt_int(n: int) -> str:
    return f"{n:,}"


def compact(n: int) -> str:
    if n >= 1000:
        v = n / 1000
        return f"{v:.1f}k".replace(".0k", "k")
    return str(n)
