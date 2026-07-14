#!/usr/bin/env python3
"""Build albums.json and download covers (iTunes primary, Cover Art Archive fallback)."""

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = "TodayListen/1.0 (personal fan project; local use)"
BASE = Path(__file__).resolve().parent
COVER_DIR = BASE / "covers"
COVER_DIR.mkdir(exist_ok=True)

# Curated discography: group studio + key compilations + both solo careers
ALBUMS = [
    # KinKi Kids / Domoto group — studio
    {"title": "A album", "artist": "KinKi Kids", "artistKey": "group", "year": "1997"},
    {"title": "B album", "artist": "KinKi Kids", "artistKey": "group", "year": "1998"},
    {"title": "C album", "artist": "KinKi Kids", "artistKey": "group", "year": "1999"},
    {"title": "D album", "artist": "KinKi Kids", "artistKey": "group", "year": "2000"},
    {"title": "E album", "artist": "KinKi Kids", "artistKey": "group", "year": "2001"},
    {"title": "F album", "artist": "KinKi Kids", "artistKey": "group", "year": "2002"},
    {"title": "G album -24/7-", "artist": "KinKi Kids", "artistKey": "group", "year": "2003",
     "itunes": "G album -24/7- KinKi Kids"},
    {"title": "H album -H・A・N・D-", "artist": "KinKi Kids", "artistKey": "group", "year": "2005",
     "itunes": "H album KinKi Kids"},
    {"title": "I album -iD-", "artist": "KinKi Kids", "artistKey": "group", "year": "2006",
     "itunes": "I album -iD- KinKi Kids"},
    {"title": "Φ", "artist": "KinKi Kids", "artistKey": "group", "year": "2007",
     "itunes": "φ KinKi Kids"},
    {"title": "J album", "artist": "KinKi Kids", "artistKey": "group", "year": "2009"},
    {"title": "K album", "artist": "KinKi Kids", "artistKey": "group", "year": "2011"},
    {"title": "L album", "artist": "KinKi Kids", "artistKey": "group", "year": "2013"},
    {"title": "M album", "artist": "KinKi Kids", "artistKey": "group", "year": "2014"},
    {"title": "N album", "artist": "KinKi Kids", "artistKey": "group", "year": "2016"},
    {"title": "O album", "artist": "KinKi Kids", "artistKey": "group", "year": "2020"},
    {"title": "P album", "artist": "KinKi Kids", "artistKey": "group", "year": "2023"},
    # KinKi Kids — compilations
    {"title": "KinKi Single Selection", "artist": "KinKi Kids", "artistKey": "group", "year": "2000"},
    {"title": "KinKi Single Selection II", "artist": "KinKi Kids", "artistKey": "group", "year": "2004"},
    {"title": "39", "artist": "KinKi Kids", "artistKey": "group", "year": "2007"},
    {"title": "Ballad Selection", "artist": "KinKi Kids", "artistKey": "group", "year": "2017"},
    {"title": "The BEST", "artist": "KinKi Kids", "artistKey": "group", "year": "2017"},
    # 堂本剛 solo
    {"title": "ROSSO E AZZURRO", "artist": "堂本剛", "artistKey": "tsuyoshi", "year": "2002",
     "itunes": "ROSSO E AZZURRO 堂本剛"},
    {"title": "Si", "artist": "堂本剛", "artistKey": "tsuyoshi", "year": "2004",
     "itunes": "Si 堂本剛"},
    {"title": "Coward", "artist": "堂本剛", "artistKey": "tsuyoshi", "year": "2006"},
    {"title": "Neo Africa Rainbow Ax", "artist": "堂本剛", "artistKey": "tsuyoshi", "year": "2009",
     "itunes": "Neo Africa Rainbow Ax 堂本剛"},
    {"title": "I and 愛", "artist": "堂本剛", "artistKey": "tsuyoshi", "year": "2012",
     "itunes": "I and 愛 堂本剛"},
    {"title": "美 我 空 -ビガク- my beautiful sky", "artist": "堂本剛", "artistKey": "tsuyoshi", "year": "2013",
     "itunes": "美我空 堂本剛"},
    {"title": "shamanippon -ラカチノトヒ-", "artist": "ENDLICHERI☆ENDLICHERI", "artistKey": "tsuyoshi", "year": "2014",
     "itunes": "shamanippon ラカチノトヒ"},
    {"title": "shamanippon -ロイノチノイ-", "artist": "ENDLICHERI☆ENDLICHERI", "artistKey": "tsuyoshi", "year": "2016",
     "itunes": "shamanippon ロイノチノイ"},
    {"title": "TU", "artist": "堂本剛", "artistKey": "tsuyoshi", "year": "2018"},
    {"title": "HYBRID FUNK", "artist": "ENDRECHERI", "artistKey": "tsuyoshi", "year": "2018"},
    {"title": "NARALIEN", "artist": "ENDRECHERI", "artistKey": "tsuyoshi", "year": "2020"},
    {"title": "LOVE FADERS", "artist": "ENDRECHERI", "artistKey": "tsuyoshi", "year": "2021"},
    {"title": "GO TO FUNK", "artist": "ENDRECHERI", "artistKey": "tsuyoshi", "year": "2023"},
    {"title": "kaba", "artist": "堂本剛", "artistKey": "tsuyoshi", "year": "2015",
     "itunes": "kaba 堂本剛"},
    # 堂本光一 solo
    {"title": "mirror", "artist": "堂本光一", "artistKey": "koichi", "year": "2006"},
    {"title": "BPM", "artist": "堂本光一", "artistKey": "koichi", "year": "2010"},
    {"title": "Gravity", "artist": "堂本光一", "artistKey": "koichi", "year": "2012"},
    {"title": "Spiral", "artist": "堂本光一", "artistKey": "koichi", "year": "2015"},
    {"title": "PLAYFUL", "artist": "堂本光一", "artistKey": "koichi", "year": "2021"},
    {"title": "RAISE", "artist": "堂本光一", "artistKey": "koichi", "year": "2025"},
]


def get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def download(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 1000:
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        if len(data) < 800:
            return False
        dest.write_bytes(data)
        return True
    except Exception:
        return False


def slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return (s or "album")[:50]


def itunes_cover(album: dict, dest: Path) -> bool:
    artist = album["artist"]
    query = album.get("itunes") or f'{album["title"]} {artist}'
    params = urllib.parse.urlencode({
        "term": query,
        "country": "jp",
        "media": "music",
        "entity": "album",
        "limit": "8",
    })
    url = f"https://itunes.apple.com/search?{params}"
    try:
        data = get_json(url)
    except Exception as e:
        print(f"itunes err {e}", end=" ")
        return False

    results = data.get("results") or []
    title_l = album["title"].lower()
    artist_l = artist.lower()
    # score candidates
    best = None
    best_score = -1
    for r in results:
        ca = (r.get("collectionName") or "").lower()
        an = (r.get("artistName") or "").lower()
        score = 0
        if title_l in ca or ca in title_l:
            score += 5
        if any(w in ca for w in re.findall(r"[a-z0-9]+", title_l) if len(w) > 1):
            score += 2
        if artist_l in an or "kinki" in an or "domoto" in an or "endrecheri" in an or "endlicheri" in an:
            score += 3
        if album["year"] and str(r.get("releaseDate", "")).startswith(album["year"]):
            score += 2
        if score > best_score:
            best_score = score
            best = r

    if not best or best_score < 3:
        # looser: first result that mentions artist family
        for r in results:
            an = (r.get("artistName") or "").lower()
            if any(x in an for x in ("kinki", "domoto", "endrecheri", "endlicheri", "堂本")):
                best = r
                best_score = 3
                break

    if not best:
        return False

    art = best.get("artworkUrl100") or ""
    if not art:
        return False
    # bump resolution
    art = art.replace("100x100bb", "600x600bb").replace("100x100", "600x600")
    return download(art, dest)


def main():
    out_albums = []
    for i, album in enumerate(ALBUMS):
        title = album.get("display") or album["title"]
        slug = f'{album["artistKey"]}-{slugify(title)}-{album["year"]}'
        dest = COVER_DIR / f"{slug}.jpg"
        rel = f"covers/{slug}.jpg"

        print(f'[{i+1}/{len(ALBUMS)}] {album["artist"]} — {title} ...', end=" ", flush=True)
        ok = itunes_cover(album, dest)
        time.sleep(0.35)
        if ok:
            print("OK")
        else:
            print("NO COVER")
            rel = ""

        out_albums.append({
            "id": slug,
            "title": title,
            "artist": album["artist"],
            "artistKey": album["artistKey"],
            "year": album["year"],
            "cover": rel,
        })

    path = BASE / "albums.json"
    path.write_text(json.dumps(out_albums, ensure_ascii=False, indent=2), encoding="utf-8")
    missing = sum(1 for a in out_albums if not a["cover"])
    print(f"\nWrote {len(out_albums)} albums. Missing covers: {missing}")


if __name__ == "__main__":
    main()
