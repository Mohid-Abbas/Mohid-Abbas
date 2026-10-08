import json
from datetime import date, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data/contributions.json").read_text(encoding="utf-8"))
OUT = ROOT / "assets/heatmap/contributions.gif"

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 10)
except OSError:
    font = small = ImageFont.load_default()

W, H = 900, 180
CELL, GAP = 11, 4
X0, Y0 = 70, 40
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

days = {x["date"]: x for x in DATA.get("days", [])}

if not days:
    # Safe first-run placeholder. The Action replaces this automatically on push.
    days = {}
    total_text = "syncing..."
else:
    total_text = f"{DATA.get('total', 0):,} contributions"

valid = sorted(days)
if valid:
    last = date.fromisoformat(valid[-1])
else:
    last = date.today()
end = last + timedelta(days=(6 - last.weekday()) % 7)
start = end - timedelta(weeks=52)

frames = []
for phase in range(12):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((20, 12), "CONTRIBUTIONS", fill="#8b949e", font=font)
    d.text((735, 12), total_text, fill="#8b949e", font=small)

    for col in range(53):
        for row in range(7):
            day = start + timedelta(days=col * 7 + row)
            item = days.get(day.isoformat(), {})
            lvl = int(item.get("level", 0))
            lvl = max(0, min(4, lvl))

            # Very subtle traveling highlight; it is intentionally slow.
            if lvl > 0 and col == phase * 4:
                lvl = min(4, lvl + 1)

            x = X0 + col * (CELL + GAP)
            y = Y0 + row * (CELL + GAP)
            d.rounded_rectangle((x, y, x + CELL, y + CELL), radius=3, fill=COLORS[lvl])

    d.text((X0, 162), "Less", fill="#8b949e", font=small)
    d.text((X0 + 65, 162), "More", fill="#8b949e", font=small)
    for i in range(5):
        x = X0 + 35 + i * 16
        d.rounded_rectangle((x, 161, x + 10, 171), radius=3, fill=COLORS[i])

    frames.append(im)

# GIF transparency is used so the graph blends into GitHub's README panel.
pframes = []
for rgba in frames:
    rgb = rgba.convert("RGB")
    q = rgb.quantize(colors=63, method=Image.Quantize.MEDIANCUT)
    old_palette = q.getpalette()[:189]
    palette = [0, 0, 0] + old_palette + [0, 0, 0] * (256 - 64)
    q.putpalette(palette)
    px = q.load()
    alpha = rgba.getchannel("A").load()
    for y in range(H):
        for x in range(W):
            if alpha[x, y] == 0:
                px[x, y] = 0
            else:
                px[x, y] = px[x, y] + 1
    pframes.append(q)

pframes[0].save(
    OUT,
    save_all=True,
    append_images=pframes[1:],
    duration=220,
    loop=0,
    transparency=0,
    disposal=2,
    optimize=False,
)
print(f"Rendered {OUT}")
