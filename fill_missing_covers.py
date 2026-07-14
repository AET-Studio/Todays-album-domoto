#!/usr/bin/env python3
"""Fill missing Tsuyoshi album covers from Deezer / Wikipedia."""

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = "TodayListen/1.0 (personal fan project)"
COVER = Path("covers")


def get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def dl(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        if len(data) < 800:
            return False
        dest.write_bytes(data)
        return True
    except Exception as e:
        print("  dl fail:", e)
        return False


def try_deezer(queries, dest: Path) -> bool:
    for q in queries:
        url = "https://api.deezer.com/search/album?" + urllib.parse.urlencode({"q": q, "limit": 12})
        try:
            data = get(url)
        except Exception as e:
            print("  deezer err", e)
            continue
        for a in data.get("data") or []:
            art = a.get("artist", {}).get("name", "")
            title = a.get("title", "")
            cover = a.get("cover_xl") or a.get("cover_big")
            print(f"  deezer: {art} | {title}")
            al = art.lower()
            if any(x in al for x in ("domoto", "endre", "endlich", "tsuyoshi")) or "堂本" in art:
                if cover and dl(cover, dest):
                    print("  SAVED via Deezer")
                    return True
        time.sleep(0.4)
    return False


def try_wiki(lang: str, titles, dest: Path) -> bool:
    for title in titles:
        api = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "piprop": "original",
            "titles": title,
        })
        try:
            data = get(api)
        except Exception as e:
            print("  wiki err", e)
            continue
        for p in data.get("query", {}).get("pages", {}).values():
            src = (p.get("original") or {}).get("source")
            print(f"  wiki {lang}:{title} -> {src or 'no image'}")
            if src and dl(src, dest):
                print("  SAVED via Wikipedia")
                return True
        time.sleep(0.4)
    return False


def try_mb_search(query: str, dest: Path) -> bool:
    url = "https://musicbrainz.org/ws/2/release-group?" + urllib.parse.urlencode({
        "query": query,
        "fmt": "json",
        "limit": 8,
    })
    try:
        data = get(url)
    except Exception as e:
        print("  mb err", e)
        return False
    time.sleep(1.1)
    for rg in data.get("release-groups") or []:
        print("  mb rg:", rg.get("title"), "|", ", ".join(a["name"] for a in rg.get("artist-credit", [])))
        rgid = rg["id"]
        for u in (
            f"https://coverartarchive.org/release-group/{rgid}/front-500",
            f"https://coverartarchive.org/release-group/{rgid}/front",
        ):
            try:
                if dl(u, dest):
                    print("  SAVED via CAA RG")
                    return True
            except Exception:
                pass
            time.sleep(0.25)
        # releases
        ru = f"https://musicbrainz.org/ws/2/release?release-group={rgid}&limit=10&fmt=json"
        try:
            rels = get(ru).get("releases") or []
        except Exception:
            continue
        time.sleep(1.1)
        for rel in rels:
            for u in (
                f"https://coverartarchive.org/release/{rel['id']}/front-500",
                f"https://coverartarchive.org/release/{rel['id']}/front",
            ):
                try:
                    if dl(u, dest):
                        print("  SAVED via CAA release")
                        return True
                except Exception:
                    pass
                time.sleep(0.25)
    return False


TARGETS = [
    {
        "file": "tsuyoshi-rosso-e-azzurro-2002.jpg",
        "id": "tsuyoshi-rosso-e-azzurro-2002",
        "deezer": ["ROSSO E AZZURRO Domoto", "ROSSO E AZZURRO Tsuyoshi"],
        "wiki_ja": ["ROSSO E AZZURRO"],
        "wiki_en": ["Rosso e Azzurro"],
        "mb": 'releasegroup:"ROSSO E AZZURRO" AND artist:"堂本剛"',
    },
    {
        "file": "tsuyoshi-coward-2006.jpg",
        "id": "tsuyoshi-coward-2006",
        "deezer": ["Coward Domoto Tsuyoshi", "Coward Tsuyoshi Domoto"],
        "wiki_ja": ["Coward (堂本剛のアルバム)", "Coward"],
        "wiki_en": ["Coward (Tsuyoshi Domoto album)"],
        "mb": 'releasegroup:"Coward" AND artist:"堂本剛"',
    },
    {
        "file": "tsuyoshi-neo-africa-rainbow-ax-2009.jpg",
        "id": "tsuyoshi-neo-africa-rainbow-ax-2009",
        "deezer": ["Neo Africa Rainbow Ax Domoto", "NEO AFRICA RAINBOW AX"],
        "wiki_ja": ["Neo Africa Rainbow Ax"],
        "wiki_en": ["Neo Africa Rainbow Ax"],
        "mb": 'releasegroup:"Neo Africa Rainbow Ax"',
    },
]


def main():
    for t in TARGETS:
        dest = COVER / t["file"]
        print("===", t["file"])
        if dest.exists() and dest.stat().st_size > 1000:
            print("  already have")
            continue
        if try_deezer(t["deezer"], dest):
            continue
        if try_wiki("ja", t["wiki_ja"], dest):
            continue
        if try_wiki("en", t["wiki_en"], dest):
            continue
        if try_mb_search(t["mb"], dest):
            continue
        print("  STILL MISSING")

    albums = json.loads(Path("albums.json").read_text(encoding="utf-8"))
    for t in TARGETS:
        path = COVER / t["file"]
        if path.exists() and path.stat().st_size > 1000:
            for a in albums:
                if a["id"] == t["id"]:
                    a["cover"] = f"covers/{t['file']}"
    Path("albums.json").write_text(json.dumps(albums, ensure_ascii=False, indent=2), encoding="utf-8")
    missing = [a["title"] for a in albums if not a["cover"]]
    print("Remaining:", missing)


if __name__ == "__main__":
    main()
