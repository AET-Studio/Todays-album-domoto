#!/usr/bin/env python3
"""Build lucky-colors.json from album covers; sync albums data."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = Path(__file__).resolve().parent

# Approximate Chinese color names by hue/lightness buckets
def name_for_rgb(r, g, b):
    mx, mn = max(r, g, b), min(r, g, b)
    chroma = mx - mn
    lum = (r + g + b) / 3
    if chroma < 18:
        if lum > 210: return "米色"
        if lum > 160: return "银灰"
        if lum > 90: return "石墨色"
        return "墨色"
    # hue
    if mx == r:
        h = (60 * ((g - b) / chroma) + 360) % 360
    elif mx == g:
        h = 60 * ((b - r) / chroma) + 120
    else:
        h = 60 * ((r - g) / chroma) + 240

    if lum > 200 and chroma < 60:
        return "素色"
    if h < 15 or h >= 345:
        return "朱红" if lum < 140 else "绯色"
    if h < 35:
        return "茜色" if lum < 120 else "橙色"
    if h < 55:
        return "缃色" if lum > 140 else "杏色"
    if h < 80:
        return "嫩芽色" if lum > 150 else "橄榄色"
    if h < 150:
        return "松叶色" if lum < 130 else "若緑色"
    if h < 175:
        return "青磁色"
    if h < 200:
        return "水色"
    if h < 230:
        return "縹色"
    if h < 260:
        return "靛青"
    if h < 290:
        return "葡萄色"
    if h < 320:
        return "紫罗兰"
    return "臙脂色" if lum < 130 else "蔷薇色"


def dominant_rgb(path: Path):
    from PIL import Image
    img = Image.open(path).convert("RGB").resize((48, 48))
    pixels = list(img.getdata())
    buckets = {}
    for r, g, b in pixels:
        if r > 245 and g > 245 and b > 245:
            continue
        if r < 20 and g < 20 and b < 20:
            continue
        key = (r // 24 * 24, g // 24 * 24, b // 24 * 24)
        buckets[key] = buckets.get(key, 0) + 1
    if not buckets:
        return (110, 143, 150)
    best = max(buckets.items(), key=lambda x: x[1])[0]
    return best


albums = json.loads((BASE / "albums.json").read_text(encoding="utf-8"))
# drop 39 Very much if any; keep 39 (2007)
albums = [a for a in albums if a.get("title") != "39 Very much" and "39-very-much" not in a.get("id", "")]

# ensure si cover
for a in albums:
    if a.get("title") in ("[síː]", "[si:]", "Si", "[siː]"):
        a["title"] = "[si:]"
        a["cover"] = "covers/tsuyoshi-si-2002.jpg"
        a["id"] = "tsuyoshi-si-2004"

lucky = {}
existing_path = BASE / "lucky-colors.json"
if existing_path.exists():
    try:
        lucky = json.loads(existing_path.read_text(encoding="utf-8"))
    except Exception:
        lucky = {}

for a in albums:
    cover = BASE / a["cover"]
    if not cover.exists():
        lucky.setdefault(a["id"], "米色")
        continue
    if a["id"] in lucky and lucky[a["id"]]:
        continue
    r, g, b = dominant_rgb(cover)
    lucky[a["id"]] = name_for_rgb(r, g, b)
    print(a["id"], lucky[a["id"]], f"rgb({r},{g},{b})")

# prune keys not in albums
ids = {a["id"] for a in albums}
lucky = {k: v for k, v in lucky.items() if k in ids}

(BASE / "albums.json").write_text(json.dumps(albums, ensure_ascii=False, indent=2), encoding="utf-8")
(BASE / "albums-data.js").write_text(
    "window.ALBUMS_DATA = " + json.dumps(albums, ensure_ascii=False, indent=2) + ";\n",
    encoding="utf-8",
)
(BASE / "lucky-colors.json").write_text(json.dumps(lucky, ensure_ascii=False, indent=2), encoding="utf-8")
(BASE / "lucky-colors.js").write_text(
    "window.LUCKY_COLORS = " + json.dumps(lucky, ensure_ascii=False, indent=2) + ";\n",
    encoding="utf-8",
)

# human readable table
lines = ["# 今日幸运色对照表", "", "改这个文件对应的 `lucky-colors.json` 同名字段即可。格式：`专辑id`: `颜色名`", "", "| 专辑 | 艺人 | 年 | id | 幸运色 |", "|---|---|---|---|---|"]
for a in albums:
    lines.append(f"| {a['title']} | {a['artist']} | {a['year']} | `{a['id']}` | {lucky.get(a['id'], '')} |")
(BASE / "幸运色对照表.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("albums", len(albums), "colors", len(lucky))
