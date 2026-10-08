"""Generate every animated SVG (dark + light variants).

Design rules
* Teal = software / AI, amber = hardware / signal. One neutral base.
* Every asset has its own OPAQUE panel, so a dark file is still legible if the
  page happens to be light (and vice-versa) — no dependence on the theme switch.
* Pure CSS / SMIL animation, no scripts (GitHub only allows that in <img> SVGs).
* `prefers-reduced-motion` → static, fully-drawn final state.
* Fonts: system stacks only. Web fonts never load inside <img> SVGs.
"""
from __future__ import annotations

from datetime import date
from string import Template

from common import GEN, clean, compact, esc, fmt_int, wrap

SANS = '-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif'
MONO = 'ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace'

PALETTES = {
    "dark": dict(panel="#0d1117", border="#30363d", text="#e6edf3", muted="#8b949e",
                 teal="#2dd4bf", amber="#f59e0b", hi="#fbbf24", pulse="#d5fff8",
                 l0="#1b2432", l1="#0e4a47", l2="#0f766e", l3="#14b8a6", l4="#2dd4bf"),
    "light": dict(panel="#ffffff", border="#d0d7de", text="#1f2328", muted="#59636e",
                  teal="#0f766e", amber="#b45309", hi="#f59e0b", pulse="#042f2e",
                  l0="#e6ebf1", l1="#b7efe7", l2="#5fd4c7", l3="#1aa396", l4="#0f766e"),
}

BASE_CSS = Template("""
text{font-family:$sans}
.mono{font-family:$mono}
@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.pk{display:none}}
""")


def _open(w: int, h: int, P: dict, title: str, desc: str, css: str = "", defs: str = "") -> str:
    base = BASE_CSS.substitute(sans=SANS, mono=MONO)
    var = "".join(f"--{k}:{v};" for k, v in P.items())
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{esc(title)}"><title>{esc(title)}</title><desc>{esc(desc)}</desc>'
            f'<style>svg{{{var}}}{base}{Template(css).safe_substitute(**P)}</style>{defs}'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="{P["panel"]}" stroke="{P["border"]}"/>')


# ═════════════════════════════════════════════════════════════════════════════
#  HERO — headline, rotating role line, and "AI → hardware" signal art
# ═════════════════════════════════════════════════════════════════════════════
def hero_svg(cfg: dict, P: dict) -> str:
    h, av = cfg["hero"], cfg.get("availability", {})
    W, H = 900, 250
    lines = h["headline"]
    fs = min(38, int(430 / (0.54 * max(len(x) for x in lines))))
    items = h["rotating"]
    N, D = len(items), 2.4
    a, b = 100 / N, 1.8
    css = f"""
.u{{animation:up .8s cubic-bezier(.2,.8,.2,1) backwards}}
.r{{opacity:0;animation:rot {N * D}s linear infinite;animation-fill-mode:backwards}}
@media (prefers-reduced-motion:reduce){{.r{{opacity:0}}.r.first{{opacity:1}}}}
@keyframes rot{{0%{{opacity:0;transform:translateY(7px)}}{b}%{{opacity:1;transform:none}}{a - b:.2f}%{{opacity:1;transform:none}}{a:.2f}%{{opacity:0;transform:translateY(-7px)}}100%{{opacity:0}}}}
.n{{animation:np 3.2s ease-in-out infinite;animation-delay:calc(var(--k)*.35s)}}
@keyframes np{{0%,100%{{opacity:.45}}50%{{opacity:1}}}}
.dot{{animation:ring 2.4s ease-out infinite;transform-box:fill-box;transform-origin:center}}
@keyframes ring{{0%{{opacity:.7;transform:scale(1)}}100%{{opacity:0;transform:scale(3)}}}}
.chip{{opacity:.1;animation:cp 1.2s ease-in-out infinite}}
@keyframes cp{{0%,100%{{opacity:.05}}50%{{opacity:.22}}}}
"""
    defs = (f'<defs><pattern id="g" width="22" height="22" patternUnits="userSpaceOnUse">'
            f'<circle cx="1.5" cy="1.5" r=".9" fill="{P["muted"]}" opacity=".35"/></pattern>'
            f'<linearGradient id="fade" x1="0" x2="1"><stop offset=".25" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset=".7" stop-color="#fff" stop-opacity="1"/></linearGradient>'
            f'<mask id="m"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask></defs>')
    s = _open(W, H, P, "Hero", f"{' '.join(lines)} — {', '.join(items)}", css, defs)
    s += f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="13" fill="url(#g)" mask="url(#m)"/>'

    # ── text column ──
    s += (f'<text class="u mono" x="40" y="52" font-size="12" letter-spacing="2.2" fill="{P["teal"]}" '
          f'style="animation-delay:.05s">{esc(h["eyebrow"])}</text>')
    for i, ln in enumerate(lines):
        s += (f'<text class="u" x="40" y="{104 + i * (fs + 8)}" font-size="{fs}" font-weight="700" '
              f'letter-spacing="-.6" fill="{P["text"]}" style="animation-delay:{.15 + i * .12}s">{esc(ln)}</text>')
    ry = 104 + (fs + 8) + 36
    s += f'<text class="u mono" x="40" y="{ry}" font-size="15" fill="{P["muted"]}" style="animation-delay:.5s">›</text>'
    for i, it in enumerate(items):
        s += (f'<text class="r mono{" first" if i == 0 else ""}" x="58" y="{ry}" font-size="15" fill="{P["teal"]}" '
              f'style="animation-delay:{i * D}s">{esc(it)}</text>')
    if av.get("show") and av.get("text"):
        txt = av["text"]
        pw = int(len(txt) * 7.3 + 40)
        py = H - 50
        s += (f'<g class="u" style="animation-delay:.7s"><rect x="40" y="{py}" width="{pw}" height="28" rx="14" '
              f'fill="{P["teal"]}" fill-opacity=".1" stroke="{P["teal"]}" stroke-opacity=".45"/>'
              f'<circle class="dot" cx="58" cy="{py + 14}" r="3.5" fill="{P["teal"]}"/>'
              f'<circle cx="58" cy="{py + 14}" r="3.5" fill="{P["teal"]}"/>'
              f'<text class="mono" x="72" y="{py + 18}" font-size="12" fill="{P["text"]}">{esc(txt)}</text></g>')

    # ── art: tiny neural net → traces → chip ──
    L1 = [(520, 70), (520, 125), (520, 180)]
    L2 = [(590, 52), (590, 98), (590, 152), (590, 198)]
    L3 = [(660, 80), (660, 125), (660, 170)]
    OUT = (715, 125)
    art = ""
    for A, Bn in ((L1, L2), (L2, L3), (L3, [OUT])):
        for (x1, y1) in A:
            for (x2, y2) in Bn:
                art += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{P["muted"]}" stroke-opacity=".28"/>'
    for pin_y in (105, 125, 145):
        pts = f"715,125 742,125 742,{pin_y} 770,{pin_y}" if pin_y != 125 else "715,125 770,125"
        art += f'<polyline points="{pts}" fill="none" stroke="{P["amber"]}" stroke-width="1.5" stroke-opacity=".75"/>'
    k = 0
    for layer in (L1, L2, L3):
        for (x, y) in layer:
            art += f'<circle class="n" style="--k:{k}" cx="{x}" cy="{y}" r="5" fill="{P["teal"]}"/>'
            k += 1
    art += f'<circle cx="{OUT[0]}" cy="{OUT[1]}" r="6" fill="{P["teal"]}"/>'
    # chip
    cx0, cy0 = 770, 85
    art += (f'<rect class="chip" x="{cx0}" y="{cy0}" width="90" height="80" rx="8" fill="{P["amber"]}"/>'
            f'<rect x="{cx0}" y="{cy0}" width="90" height="80" rx="8" fill="none" stroke="{P["amber"]}" stroke-width="1.6"/>'
            f'<rect x="{cx0 + 20}" y="{cy0 + 15}" width="50" height="50" rx="4" fill="none" stroke="{P["amber"]}" stroke-opacity=".6"/>'
            f'<text class="mono" x="{cx0 + 45}" y="{cy0 + 44}" font-size="10.5" text-anchor="middle" fill="{P["amber"]}">{esc(h.get("chip_label", "MCU"))}</text>')
    for yy in (105, 125, 145):
        art += f'<line x1="{cx0 + 90}" y1="{yy}" x2="{cx0 + 102}" y2="{yy}" stroke="{P["amber"]}" stroke-opacity=".7" stroke-width="1.5"/>'
    for xx in (cx0 + 20, cx0 + 45, cx0 + 70):
        art += (f'<line x1="{xx}" y1="{cy0 - 8}" x2="{xx}" y2="{cy0}" stroke="{P["amber"]}" stroke-opacity=".7" stroke-width="1.5"/>'
                f'<line x1="{xx}" y1="{cy0 + 80}" x2="{xx}" y2="{cy0 + 88}" stroke="{P["amber"]}" stroke-opacity=".7" stroke-width="1.5"/>')
    # packets (SMIL — works inside <img> SVGs)
    paths = ["M520,125 L590,98 L660,125 L715,125 L742,125 L742,105 L770,105",
             "M520,70 L590,152 L660,170 L715,125 L770,125",
             "M520,180 L590,198 L660,80 L715,125 L742,125 L742,145 L770,145"]
    for i, p in enumerate(paths):
        art += (f'<circle class="pk" r="3.6" opacity="0" fill="{P["hi"]}"><animateMotion dur="3.6s" begin="{i * 1.2}s" repeatCount="indefinite" path="{p}"/>'
                f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.92;1" dur="3.6s" begin="{i * 1.2}s" repeatCount="indefinite"/></circle>')
    return s + art + "</svg>"


# ═════════════════════════════════════════════════════════════════════════════
#  CONTRIBUTION BUBBLES — column-by-column fill, then a bright current sweeps →
# ═════════════════════════════════════════════════════════════════════════════
RADII = [2.1, 3.7, 4.8, 5.9, 6.8]
SCALE = [1.7, 1.35, 1.25, 1.18, 1.12]       # how much each level swells under the sweep


def contrib_svg(data: dict, st: dict, P: dict) -> str:
    weeks = data["weeks"]
    n, PITCH, X0, Y0 = len(weeks), 15, 40, 74
    W, H = X0 + n * PITCH + 8, Y0 + 7 * PITCH + 50
    FILL_STEP, CYCLE, SWEEP = 0.05, 14, 7        # seconds
    css = f"""
.p{{transform-box:fill-box;transform-origin:center;animation:pop {CYCLE}s cubic-bezier(.2,.8,.2,1) infinite backwards;
   animation-delay:calc(var(--i)*{FILL_STEP}s + var(--j)*.018s)}}
@keyframes pop{{0%{{transform:scale(0);opacity:0}}3.5%{{transform:scale(1.25);opacity:1}}5.5%{{transform:scale(1);opacity:1}}
   95%{{transform:scale(1);opacity:1}}100%{{transform:scale(0);opacity:0}}}}
.d{{fill:var(--c);transform-box:fill-box;transform-origin:center;animation:sweep {SWEEP}s linear infinite;
   animation-delay:calc(var(--i)*{FILL_STEP}s + 3.4s)}}
@keyframes sweep{{0%{{fill:var(--c);transform:scale(1)}}2%{{fill:var(--pulse);transform:scale(var(--s))}}
   9%{{fill:var(--c);transform:scale(1)}}100%{{fill:var(--c);transform:scale(1)}}}}
""" + "".join(f".l{i}{{--c:var(--l{i});--s:{SCALE[i]}}}" for i in range(5)) + ".h{animation:up .8s backwards}"
    s = _open(W, H, P, "Contribution activity",
              f"{st['total']} contributions in the last year; {st['active_days']} active days; longest streak {st['longest_streak']} days.", css)

    s += (f'<text class="h" x="24" y="42"><tspan font-size="28" font-weight="700" fill="{P["text"]}">{fmt_int(st["total"])}</tspan>'
          f'<tspan font-size="13" dx="8" fill="{P["muted"]}">contributions in the last year</tspan></text>')
    s += (f'<text class="h mono" x="{W - 24}" y="38" font-size="12" text-anchor="end" fill="{P["muted"]}">'
          f'<tspan fill="{P["text"]}" font-weight="700">{st["active_days"]}</tspan> active days  ·  '
          f'longest streak <tspan fill="{P["text"]}" font-weight="700">{st["longest_streak"]}d</tspan>  ·  '
          f'current <tspan fill="{P["text"]}" font-weight="700">{st["current_streak"]}d</tspan></text>')

    # month + weekday labels
    prev_m, last_col = None, -9
    for ci, w in enumerate(weeks):
        m = date.fromisoformat(w[0]["date"]).month
        if m != prev_m and ci - last_col >= 3:
            s += (f'<text class="mono" x="{X0 + ci * PITCH}" y="{Y0 - 10}" font-size="10" fill="{P["muted"]}">'
                  f'{date(2000, m, 1).strftime("%b")}</text>')
            last_col = ci
        prev_m = m
    for row, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        s += (f'<text class="mono" x="{X0 - 10}" y="{Y0 + row * PITCH + PITCH / 2 + 3.5}" font-size="10" '
              f'text-anchor="end" fill="{P["muted"]}">{lab}</text>')

    # bubbles
    for ci, w in enumerate(weeks):
        for d in w:
            r, lv = d["weekday"], d["level"]
            cx, cy = X0 + ci * PITCH + PITCH / 2, Y0 + r * PITCH + PITCH / 2
            s += (f'<g class="p" style="--i:{ci};--j:{r}"><circle class="d l{lv}" cx="{cx}" cy="{cy}" r="{RADII[lv]}">'
                  f'<title>{d["count"]} contributions on {d["date"]}</title></circle></g>')

    # legend
    lx, ly = W - 24 - 150, H - 20
    s += f'<text class="mono" x="{lx}" y="{ly + 3}" font-size="10" fill="{P["muted"]}">Less</text>'
    for i in range(5):
        s += f'<circle cx="{lx + 44 + i * 16}" cy="{ly}" r="{RADII[i] * .85:.1f}" fill="{P[f"l{i}"]}"/>'
    s += f'<text class="mono" x="{lx + 44 + 5 * 16 + 2}" y="{ly + 3}" font-size="10" fill="{P["muted"]}">More</text>'
    return s + "</svg>"


# ═════════════════════════════════════════════════════════════════════════════
#  CHARTS
# ═════════════════════════════════════════════════════════════════════════════
def lang_rows(data: dict, cfg: dict) -> list[tuple[str, int]]:
    ex = set(cfg["languages"]["exclude"])
    langs = {k: v for k, v in data["languages"].items() if k not in ex}
    return sorted(langs.items(), key=lambda kv: -kv[1])[: cfg["languages"]["top"]]


def chart_height(data: dict, cfg: dict) -> int:
    return max(218, 88 + len(lang_rows(data, cfg)) * 30 + 6)


def lang_svg(data: dict, cfg: dict, P: dict, H: int) -> str | None:
    ex = set(cfg["languages"]["exclude"])
    tot = sum(v for k, v in data["languages"].items() if k not in ex)
    top = lang_rows(data, cfg)
    if not tot:
        return None
    mx = top[0][1]
    W, y0, pitch = 410, 88, 30
    css = ".b{transform-box:fill-box;transform-origin:left center;animation:gx .9s cubic-bezier(.2,.8,.2,1) backwards;animation-delay:calc(var(--k)*.08s + .15s)}" \
          "@keyframes gx{from{transform:scaleX(0)}to{transform:none}}.f{animation:up .6s backwards;animation-delay:calc(var(--k)*.08s)}"
    s = _open(W, H, P, "Top languages", ", ".join(f"{k} {v / tot * 100:.0f}%" for k, v in top), css)
    s += f'<text x="24" y="36" font-size="15" font-weight="700" fill="{P["text"]}">Languages</text>'
    s += f'<text x="24" y="54" font-size="11.5" fill="{P["muted"]}">share of code by size · notebooks and markup excluded</text>'
    for i, (name, v) in enumerate(top):
        cy = y0 + i * pitch
        pct = v / tot * 100
        label = "<1%" if pct < 1 else f"{pct:.0f}%"
        s += (f'<g class="f" style="--k:{i}"><text class="mono" x="24" y="{cy + 4}" font-size="12.5" fill="{P["text"]}">{esc(name)}</text></g>'
              f'<rect x="132" y="{cy - 4}" width="208" height="8" rx="4" fill="{P["l0"]}"/>'
              f'<rect class="b" style="--k:{i}" x="132" y="{cy - 4}" width="{max(6, 208 * v / mx):.1f}" height="8" rx="4" fill="{P["teal"]}"/>'
              f'<text class="mono f" style="--k:{i}" x="{W - 24}" y="{cy + 4}" font-size="12" text-anchor="end" fill="{P["muted"]}">{label}</text>')
    return s + "</svg>"


def month_svg(st: dict, P: dict, H: int = 218) -> str:
    months = st["months"]
    mx = max(m["count"] for m in months) or 1
    W, x0, x1 = 410, 24, 386
    base = H - 46
    ph = base - 80
    pitch = (x1 - x0) / len(months)
    bw = 18
    css = ".b{transform-box:fill-box;transform-origin:50% 100%;animation:gy .8s cubic-bezier(.2,.8,.2,1) backwards;animation-delay:calc(var(--k)*.05s + .15s)}" \
          "@keyframes gy{from{transform:scaleY(0)}to{transform:none}}.f{animation:up .6s backwards;animation-delay:calc(var(--k)*.05s + .5s)}"
    s = _open(W, H, P, "Contributions by month",
              ", ".join(f"{m['label']} {m['count']}" for m in months), css)
    s += f'<text x="24" y="36" font-size="15" font-weight="700" fill="{P["text"]}">Contributions by month</text>'
    s += f'<text x="24" y="54" font-size="11.5" fill="{P["muted"]}">last 12 months · current month in amber</text>'
    s += f'<line x1="{x0}" y1="{base}" x2="{x1}" y2="{base}" stroke="{P["border"]}"/>'
    for i, m in enumerate(months):
        cx = x0 + pitch * i + pitch / 2
        h = 0 if m["count"] == 0 else max(2.5, m["count"] / mx * ph)
        col = P["amber"] if i == len(months) - 1 else P["teal"]
        if h:
            s += f'<rect class="b" style="--k:{i}" x="{cx - bw / 2:.1f}" y="{base - h:.1f}" width="{bw}" height="{h:.1f}" rx="3" fill="{col}"/>'
            s += (f'<text class="mono f" style="--k:{i}" x="{cx:.1f}" y="{base - h - 6:.1f}" font-size="9.5" '
                  f'text-anchor="middle" fill="{P["muted"]}">{compact(m["count"])}</text>')
        s += f'<text class="mono" x="{cx:.1f}" y="{base + 17}" font-size="10" text-anchor="middle" fill="{P["muted"]}">{m["label"]}</text>'
    return s + "</svg>"


# ═════════════════════════════════════════════════════════════════════════════
#  STACK CHIPS
# ═════════════════════════════════════════════════════════════════════════════
def stack_svg(cfg: dict, P: dict) -> str:
    W, X0, ROW, GAP = 840, 150, 34, 14
    y, k, body = 24, 0, ""
    for g in cfg["stack"]:
        col = P["amber"] if g.get("domain") == "hardware" else P["teal"]
        x, first_y = X0, y
        for it in g["items"]:
            w = int(len(it) * 7.6 + 26)
            if x + w > W - 24:
                x, y = X0, y + ROW
            body += (f'<g class="c" style="--k:{k}"><rect x="{x}" y="{y}" width="{w}" height="26" rx="13" fill="{col}" fill-opacity=".1" '
                     f'stroke="{col}" stroke-opacity=".5"/><text class="mono" x="{x + w / 2}" y="{y + 17}" font-size="12.5" '
                     f'text-anchor="middle" fill="{P["text"]}">{esc(it)}</text></g>')
            x += w + 8
            k += 1
        body += (f'<text class="mono" x="24" y="{first_y + 17}" font-size="11" letter-spacing="1.6" fill="{col}">{esc(g["label"])}</text>')
        y += ROW + GAP
    H = y - GAP + 24 - (ROW - 26)
    css = ".c{animation:up .6s cubic-bezier(.2,.8,.2,1) backwards;animation-delay:calc(var(--k)*.04s)}"
    return _open(W, H, P, "Stack", "; ".join(f"{g['label']}: {', '.join(g['items'])}" for g in cfg["stack"]), css) + body + "</svg>"


# ═════════════════════════════════════════════════════════════════════════════
#  PROJECT CARDS (one SVG per pinned repo)
# ═════════════════════════════════════════════════════════════════════════════
def is_hardware(repo: dict, cfg: dict) -> bool:
    pc = cfg["projects"]
    return repo["name"] in pc.get("hardware_repos", []) or bool(set(repo["topics"]) & set(pc.get("hardware_topics", [])))


def card_svg(repo: dict, idx: int, cfg: dict, P: dict) -> str:
    W, H = 410, 156
    hw = is_hardware(repo, cfg)
    col = P["amber"] if hw else P["teal"]
    tag = "HARDWARE" if hw else "AI · SOFTWARE"
    ov = cfg["projects"].get("override", {}).get(repo["name"], {})
    desc = ov.get("tagline") or clean(repo["description"]) or "No description yet. Add one on GitHub and this card updates itself."
    lines = wrap(desc, 56, 2)
    name = repo["name"] if len(repo["name"]) <= 42 else repo["name"][:41] + "…"
    name_fs = 17 if len(name) <= 30 else 15
    defs = (f'<defs><radialGradient id="gl" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="300">'
            f'<stop offset="0" style="stop-color:{col}" stop-opacity=".16"/><stop offset="1" style="stop-color:{col}" stop-opacity="0"/>'
            f'</radialGradient></defs>')
    css = f".all{{animation:up .7s cubic-bezier(.2,.8,.2,1) backwards;animation-delay:{.08 * idx:.2f}s}}"
    s = _open(W, H, P, f"{repo['name']} — {tag}", desc, css, defs)
    s += f'<g class="all"><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="url(#gl)"/>'
    pw = int(len(tag) * 7.4 + 22)
    s += (f'<rect x="20" y="18" width="{pw}" height="22" rx="11" fill="{col}" fill-opacity=".12" stroke="{col}" stroke-opacity=".5"/>'
          f'<text class="mono" x="{20 + pw / 2}" y="33" font-size="10.5" letter-spacing="1.2" text-anchor="middle" fill="{col}">{tag}</text>')
    stats = []
    if repo["stars"]:
        stats.append(f"★ {repo['stars']}")
    if repo["forks"]:
        stats.append(f"forks {repo['forks']}")
    if stats:
        s += f'<text class="mono" x="{W - 20}" y="33" font-size="11.5" text-anchor="end" fill="{P["muted"]}">{esc("   ".join(stats))}</text>'
    s += f'<text x="20" y="68" font-size="{name_fs}" font-weight="700" fill="{P["text"]}">{esc(name)}</text>'
    for i, ln in enumerate(lines):
        s += f'<text x="20" y="{92 + i * 18}" font-size="12.5" fill="{P["muted"]}">{esc(ln)}</text>'
    if repo["language"]:
        s += (f'<circle cx="25" cy="{H - 22}" r="4" fill="{col}"/>'
              f'<text class="mono" x="36" y="{H - 18}" font-size="11.5" fill="{P["text"]}">{esc(repo["language"])}</text>')
    return s + "</g></svg>"


# ═════════════════════════════════════════════════════════════════════════════
def build_all(data: dict, st: dict, cfg: dict, repos: list[dict]) -> dict[str, str]:
    """Return {filename: svg} for both themes. Optional charts return None → skipped."""
    out: dict[str, str] = {}
    for theme, P in PALETTES.items():
        out[f"hero-{theme}.svg"] = hero_svg(cfg, P)
        out[f"activity-{theme}.svg"] = contrib_svg(data, st, P)
        ch = chart_height(data, cfg)
        out[f"months-{theme}.svg"] = month_svg(st, P, ch)
        out[f"stack-{theme}.svg"] = stack_svg(cfg, P)
        lang = lang_svg(data, cfg, P, ch)
        if lang:
            out[f"languages-{theme}.svg"] = lang
        for i, r in enumerate(repos):
            out[f"card-{i}-{theme}.svg"] = card_svg(r, i, cfg, P)
    return out


def write_all(files: dict[str, str]) -> None:
    GEN.mkdir(parents=True, exist_ok=True)
    for old in GEN.glob("*.svg"):          # drop cards for repos that are no longer pinned
        old.unlink()
    for name, svg in files.items():
        (GEN / name).write_text(svg, encoding="utf-8")
