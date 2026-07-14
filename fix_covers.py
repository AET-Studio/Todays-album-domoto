#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json
import urllib.parse

covers = [
    ("group-39-very-much-2025.jpg", "39 Very much", "KinKi Kids", "2025", (62, 48, 42), (210, 180, 130)),
    ("tsuyoshi-neo-africa-rainbow-ax-2007.jpg", "Neo Africa\nRainbow Ax", "ENDLICHERI", "2007", (28, 72, 58), (200, 170, 80)),
    ("tsuyoshi-my-beautiful-sky-2009.jpg", "美我空", "剛紫", "2009", (70, 55, 90), (200, 180, 220)),
    ("tsuyoshi-nippon-2011.jpg", "NIPPON", "堂本剛", "2011", (40, 40, 48), (180, 160, 120)),
]

for fname, title, artist, year, bg, accent in covers:
    img = Image.new("RGB", (600, 600), bg)
    draw = ImageDraw.Draw(img)
    for y in range(0, 600, 3):
        shade = tuple(max(0, min(255, c + (4 if y % 6 == 0 else -2))) for c in bg)
        draw.line([(0, y), (600, y)], fill=shade)
    draw.rectangle([28, 28, 571, 571], outline=accent, width=2)
    try:
        font_t = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 40)
        font_a = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 22)
        font_y = ImageFont.truetype("C:/Windows/Fonts/georgia.ttf", 18)
        font_c = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 40)
    except Exception:
        font_t = font_a = font_y = font_c = ImageFont.load_default()
    lines = title.split("\n")
    y0 = 210 if len(lines) == 1 else 180
    for i, line in enumerate(lines):
        f = font_c if any(ord(c) > 127 for c in line) else font_t
        bbox = draw.textbbox((0, 0), line, font=f)
        tw = bbox[2] - bbox[0]
        draw.text(((600 - tw) / 2, y0 + i * 52), line, fill=accent, font=f)
    bbox = draw.textbbox((0, 0), artist, font=font_a)
    draw.text(((600 - (bbox[2] - bbox[0])) / 2, 420), artist, fill=(230, 220, 200), font=font_a)
    bbox = draw.textbbox((0, 0), year, font=font_y)
    draw.text(((600 - (bbox[2] - bbox[0])) / 2, 460), year, fill=(200, 190, 170), font=font_y)
    Path("covers").mkdir(exist_ok=True)
    img.save(Path("covers") / fname, quality=92)
    print("made", fname)

albums = json.loads(Path("albums.json").read_text(encoding="utf-8"))
cmap = {
    "39 Very much": "covers/group-39-very-much-2025.jpg",
    "Neo Africa Rainbow Ax": "covers/tsuyoshi-neo-africa-rainbow-ax-2007.jpg",
    "美 我 空 -ビガク- my beautiful sky": "covers/tsuyoshi-my-beautiful-sky-2009.jpg",
    "NIPPON": "covers/tsuyoshi-nippon-2011.jpg",
}
for a in albums:
    if a["title"] in cmap and (not a.get("cover")):
        a["cover"] = cmap[a["title"]]
    elif a["title"] in cmap:
        a["cover"] = cmap[a["title"]]
    # also remap rossso/coward placeholder names if empty
    if not a.get("cover"):
        # keep empty for MISSING report
        pass
    sp = a.get("spotify") or ""
    if "open.spotify.com/search/" in sp and "/albums" not in sp:
        q = urllib.parse.quote(f'{a["artist"]} {a["title"]}')
        a["spotify"] = f"https://open.spotify.com/search/{q}/albums"

# Ensure ROSSO/Coward have their existing placeholder files if any
for a in albums:
    if a["title"] == "ROSSO E AZZURRO" and not a.get("cover"):
        p = Path("covers/tsuyoshi-rosso-e-azzurro-2002.jpg")
        if p.exists():
            a["cover"] = "covers/tsuyoshi-rosso-e-azzurro-2002.jpg"
    if a["title"] == "Coward" and not a.get("cover"):
        p = Path("covers/tsuyoshi-coward-2006.jpg")
        if p.exists():
            a["cover"] = "covers/tsuyoshi-coward-2006.jpg"

Path("albums.json").write_text(json.dumps(albums, ensure_ascii=False, indent=2), encoding="utf-8")
Path("albums-data.js").write_text(
    "window.ALBUMS_DATA = " + json.dumps(albums, ensure_ascii=False, indent=2) + ";\n",
    encoding="utf-8",
)
print("with cover", sum(1 for a in albums if a.get("cover")), "/", len(albums))
