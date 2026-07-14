#!/usr/bin/env python3
"""Sync albums.json with covers on disk; strip lyrics; add netease links."""
import json
import sys
import urllib.parse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = Path(__file__).resolve().parent
COVERS = {p.name for p in (BASE / "covers").glob("*.jpg")}

NETEASE_ARTIST = {
    "group": "https://music.163.com/#/search/m/?s=KinKi%20Kids&type=100",
    "tsuyoshi": "https://music.163.com/#/search/m/?s=%E5%A0%82%E6%9C%AC%E5%89%9B&type=100",
    "koichi": "https://music.163.com/#/search/m/?s=%E5%A0%82%E6%9C%AC%E5%85%89%E4%B8%80&type=100",
}

def netease_album(artist, title):
    q = urllib.parse.quote(f"{artist} {title}")
    return f"https://music.163.com/#/search/m/?s={q}&type=10"

def netease_artist(key):
    return NETEASE_ARTIST.get(key) or NETEASE_ARTIST["group"]

albums = json.loads((BASE / "albums.json").read_text(encoding="utf-8"))
out = []

for a in albums:
    # fix si cover path
    if a.get("id") == "tsuyoshi-s-2004" or a.get("title") in ("[síː]", "[si:]", "Si"):
        a["id"] = "tsuyoshi-si-2004"
        a["title"] = "[síː]"
        a["cover"] = "covers/tsuyoshi-si-2002.jpg"
        a["year"] = "2004"

    cover_name = Path(a.get("cover") or "").name
    if cover_name not in COVERS:
        print("drop", a.get("title"), a.get("cover"))
        continue

    a.pop("lyrics", None)
    a["netease"] = netease_album(a["artist"], a["title"])
    a["neteaseArtist"] = netease_artist(a.get("artistKey"))
    # spotify/apple artist fallbacks
    if a.get("artistKey") == "group":
        a["appleArtist"] = "https://music.apple.com/jp/artist/kinki-kids/1494211347"
        a["spotifyArtist"] = "https://open.spotify.com/search/KinKi%20Kids/artists"
    elif a.get("artistKey") == "tsuyoshi":
        a["appleArtist"] = "https://music.apple.com/jp/search?term=%E5%A0%82%E6%9C%AC%E5%89%9B"
        a["spotifyArtist"] = "https://open.spotify.com/search/%E5%A0%82%E6%9C%AC%E5%89%9B/artists"
    else:
        a["appleArtist"] = "https://music.apple.com/jp/search?term=%E5%A0%82%E6%9C%AC%E5%85%89%E4%B8%80"
        a["spotifyArtist"] = "https://open.spotify.com/search/%E5%A0%82%E6%9C%AC%E5%85%89%E4%B8%80/artists"
    out.append(a)

# add またね if orphan cover exists
if "group-matane-2026.jpg" in COVERS and not any(a["title"] == "またね" for a in out):
    out.append({
        "id": "group-matane-2026",
        "title": "またね",
        "artist": "DOMOTO",
        "artistKey": "group",
        "period": "DOMOTO",
        "year": "2026",
        "type": "ep",
        "cover": "covers/group-matane-2026.jpg",
        "apple": "https://music.apple.com/jp/search?term=DOMOTO%20%E3%81%BE%E3%81%9F%E3%81%AD",
        "spotify": "https://open.spotify.com/search/DOMOTO%20%E3%81%BE%E3%81%9F%E3%81%AD/albums",
        "netease": netease_album("DOMOTO", "またね"),
        "neteaseArtist": NETEASE_ARTIST["group"],
        "appleArtist": "https://music.apple.com/jp/artist/kinki-kids/1494211347",
        "spotifyArtist": "https://open.spotify.com/search/DOMOTO/artists",
    })
    print("added またね")

(BASE / "albums.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
(BASE / "albums-data.js").write_text(
    "window.ALBUMS_DATA = " + json.dumps(out, ensure_ascii=False, indent=2) + ";\n",
    encoding="utf-8",
)
print("synced", len(out), "albums")
