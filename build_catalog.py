#!/usr/bin/env python3
"""Build albums.json with lyrics + Apple/Spotify links; fetch missing covers."""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = "TodaysShelf/1.1 (personal fan project; local use)"
BASE = Path(__file__).resolve().parent
COVER = BASE / "covers"
COVER.mkdir(exist_ok=True)

# lyrics: short commonly-quoted lines (fan/forum/review favorites), not full songs
ALBUMS = [
  # —— KinKi Kids / DOMOTO ——
  {"title": "A album", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "1997",
   "lyrics": [
     {"song": "Kissからはじまるミステリー", "line": "Kissからはじまるミステリー 愛が魔法をかける"},
     {"song": "愛されるより 愛したい", "line": "愛されるより 愛したい そう思えるくらいに"},
   ]},
  {"title": "B album", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "1998",
   "lyrics": [
     {"song": "ジェットコースター・ロマンス", "line": "ジェットコースター・ロマンス 本気になって墜落しそう"},
     {"song": "愛のかたまり", "line": "X'masなんていらないくらい 日々が愛のかたまり"},
   ]},
  {"title": "C album", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "1999",
   "lyrics": [
     {"song": "Flower", "line": "Flower 君は僕のすべてさ"},
     {"song": "雨のMelody", "line": "雨のMelodyが聞こえるよ"},
   ]},
  {"title": "D album", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2000",
   "lyrics": [
     {"song": "ボクの背中には羽根がある", "line": "ボクの背中には羽根がある どんな夢もかなう気がする"},
     {"song": "夏の王様", "line": "夏の王様は僕たちさ"},
   ]},
  {"title": "E album", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2001",
   "lyrics": [
     {"song": "ボクのせいじゃない", "line": "ボクのせいじゃない 恋が悪戯をするんだ"},
     {"song": "Hey! みんな元気かい?", "line": "Hey! みんな元気かい?"},
   ]},
  {"title": "F album", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2002",
   "lyrics": [
     {"song": "情熱", "line": "情熱を throng  throng"},
     {"song": "カナシミ ブルー", "line": "カナシミ ブルーがこぼれないように"},
   ]},
  {"title": "G album -24/7-", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2003",
   "itunes": "G album 24/7 KinKi Kids",
   "lyrics": [
     {"song": "永遠のBLOODS", "line": "永遠のBLOODS 溶け合う二人の記憶"},
     {"song": "薄荷キャンディー", "line": "薄荷キャンディーのように冷たいキス"},
   ]},
  {"title": "H album -H・A・N・D-", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2005",
   "itunes": "H album KinKi Kids",
   "lyrics": [
     {"song": "ね、元気？", "line": "ね、元気？ 窓を開けたら声が届くかな"},
     {"song": "ビロードの闇", "line": "ビロードの闇に溶ける声"},
   ]},
  {"title": "I album -iD-", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2006",
   "itunes": "I album iD KinKi Kids",
   "lyrics": [
     {"song": "Harmony of December", "line": "Harmony of December 君と歌う季節"},
     {"song": "SNOW! SNOW! SNOW!", "line": "SNOW! SNOW! SNOW! 舞い落ちる想い"},
   ]},
  {"title": "Φ", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2007",
   "itunes": "φ KinKi Kids",
   "lyrics": [
     {"song": "Secret Code", "line": "Secret Code 解き明かせない恋"},
     {"song": "僕は思う", "line": "僕は思う 君の隣が一番だ"},
   ]},
  {"title": "J album", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2009",
   "lyrics": [
     {"song": "スワンソング", "line": "スワンソングが聞こえる夜"},
     {"song": "Key of Life", "line": "Key of Life 君がくれる光"},
   ]},
  {"title": "K album", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2011",
   "lyrics": [
     {"song": "Time", "line": "Timeよ止まれ この瞬間だけ"},
     {"song": "稲妻ブースター", "line": "稲妻ブースター 駆け抜けろ"},
   ]},
  {"title": "L album", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2013",
   "lyrics": [
     {"song": "まだ終わらない夏", "line": "まだ終わらない夏があるなら"},
     {"song": "約束", "line": "約束って言っちゃおうか"},
   ]},
  {"title": "M album", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2014",
   "lyrics": [
     {"song": "鍵のない箱", "line": "鍵のない箱を開けるように"},
     {"song": "ずっと", "line": "ずっと この手を離さないで"},
   ]},
  {"title": "N album", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2016",
   "lyrics": [
     {"song": "薔薇と太陽", "line": "薔薇と太陽 どちらが君を照らすの"},
     {"song": "夢を見れば傷つくこともある", "line": "夢を見れば傷つくこともある それでもいい"},
   ]},
  {"title": "O album", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2020",
   "lyrics": [
     {"song": "KANZAI BOYA", "line": "KANZAI BOYA 笑い飛ばせこの街で"},
     {"song": "The Story of Us", "line": "The Story of Us まだ続きがある"},
   ]},
  {"title": "P album", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2023",
   "lyrics": [
     {"song": "シュレーディンガー", "line": "シュレーディンガーの箱の中 生きてる心"},
     {"song": "世界中をI LOVE YOU", "line": "世界中をI LOVE YOU 君に届ける"},
   ]},
  {"title": "KinKi Single Selection", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2000",
   "lyrics": [
     {"song": "硝子の少年", "line": "ぼくの心はひび割れたビー玉さ"},
     {"song": "愛されるより 愛したい", "line": "愛されるより 愛したい"},
     {"song": "Kissからはじまるミステリー", "line": "Kissからはじまるミステリー"},
   ]},
  {"title": "KinKi Single Selection II", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2004",
   "lyrics": [
     {"song": "薄荷キャンディー", "line": "薄荷キャンディーのように冷たいキス"},
     {"song": "ね、元気？", "line": "ね、元気？"},
     {"song": "ビロードの闇", "line": "ビロードの闇"},
   ]},
  {"title": "39", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2007",
   "lyrics": [
     {"song": "硝子の少年", "line": "Stay with me 硝子の少年時代の破片が胸へと突き刺さる"},
     {"song": "愛のかたまり", "line": "X'masなんていらないくらい 日々が愛のかたまり"},
     {"song": "ボクの背中には羽根がある", "line": "君を抱いて空も飛べる 嘘じゃないよ"},
   ]},
  {"title": "Ballad Selection", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2017",
   "lyrics": [
     {"song": "愛のかたまり", "line": "思いきり抱き寄せられると心 あなたでよかったと歌うの"},
     {"song": "スワンソング", "line": "スワンソング"},
   ]},
  {"title": "The BEST", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids", "year": "2017",
   "lyrics": [
     {"song": "硝子の少年", "line": "痛みがあるから輝く 蒼い日々がきらり"},
     {"song": "愛のかたまり", "line": "日々が愛のかたまり"},
   ]},
  {"title": "39 Very much", "artist": "KinKi Kids", "artistKey": "group", "period": "KinKi Kids → DOMOTO", "year": "2025",
   "itunes": "39 Very much KinKi Kids",
   "lyrics": [
     {"song": "硝子の少年", "line": "何かが終わってはじまる 雲が切れてぼくを照らし出す"},
     {"song": "愛のかたまり", "line": "変わっていく僕らの愛は 強く光り輝く"},
     {"song": "シュレーディンガー", "line": "シュレーディンガー"},
   ]},

  # —— 堂本剛 / 各花名 ——
  {"title": "ROSSO E AZZURRO", "artist": "堂本剛", "artistKey": "tsuyoshi", "period": "堂本剛", "year": "2002",
   "itunes": "ROSSO E AZZURRO 堂本剛",
   "lyrics": [
     {"song": "街", "line": "愛を見失ってしまう時代だ だからこそ僕らが愛を刻もう"},
     {"song": "溺愛ロジック", "line": "抱いて抱いて抱いて抱いて ズキドキさせて"},
     {"song": "心の恋人", "line": "心の恋人よ"},
   ]},
  {"title": "[síː]", "artist": "堂本剛", "artistKey": "tsuyoshi", "period": "堂本剛", "year": "2004",
   "itunes": "si 堂本剛",
   "lyrics": [
     {"song": "WAVER", "line": "WAVER 揺れる想いを止めないで"},
     {"song": "Leaving! Leaving!", "line": "Leaving! Leaving!"},
   ]},
  {"title": "Coward", "artist": "ENDLICHERI☆ENDLICHERI", "artistKey": "tsuyoshi", "period": "ENDLICHERI☆ENDLICHERI", "year": "2006",
   "itunes": "Coward ENDLICHERI",
   "lyrics": [
     {"song": "ソメイヨシノ", "line": "ソメイヨシノよ 散ってもいい それでも美しく"},
     {"song": "The Rainbow Star", "line": "The Rainbow Star"},
   ]},
  {"title": "Neo Africa Rainbow Ax", "artist": "ENDLICHERI☆ENDLICHERI", "artistKey": "tsuyoshi", "period": "ENDLICHERI☆ENDLICHERI", "year": "2007",
   "itunes": "Neo Africa Rainbow Ax",
   "lyrics": [
     {"song": "空が泣くから", "line": "空が泣くから 僕も泣いていい"},
     {"song": "Believe in intuition…", "line": "Believe in intuition…"},
   ]},
  {"title": "I AND 愛", "artist": "244 ENDLI-x", "artistKey": "tsuyoshi", "period": "244 ENDLI-x", "year": "2008",
   "itunes": "I AND 愛 244",
   "lyrics": [
     {"song": "Let's Get FUNKASY!!!", "line": "Let's Get FUNKASY!!!"},
     {"song": "Say Anything", "line": "Say Anything 愛を隠さず"},
     {"song": "Now's the time to change the world!", "line": "Now's the time to change the world!"},
   ]},
  {"title": "美 我 空 -ビガク- my beautiful sky", "artist": "剛紫", "artistKey": "tsuyoshi", "period": "剛紫", "year": "2009",
   "itunes": "美我空 剛紫",
   "lyrics": [
     {"song": "空 〜美しい我の空", "line": "美しい我の空へ届け"},
     {"song": "RAIN", "line": "RAIN 洗い流してくれるなら"},
   ]},
  {"title": "NIPPON", "artist": "堂本剛", "artistKey": "tsuyoshi", "period": "堂本剛", "year": "2011",
   "itunes": "NIPPON 堂本剛",
   "lyrics": [
     {"song": "縁を結いて", "line": "縁を結いて この手のひらに"},
     {"song": "Nijiの詩", "line": "Nijiの詩を歌おう"},
   ]},
  {"title": "shamanippon -ラカチノトヒ-", "artist": "堂本剛", "artistKey": "tsuyoshi", "period": "SHAMANIPPON", "year": "2012",
   "itunes": "shamanippon ラカチノトヒ",
   "lyrics": [
     {"song": "瞬き", "line": "瞬きのあいだにすべてが変わる"},
     {"song": "ラカチノトヒ", "line": "ラカチノトヒ"},
   ]},
  {"title": "kaba", "artist": "堂本剛", "artistKey": "tsuyoshi", "period": "堂本剛", "year": "2013",
   "itunes": "kaba 堂本剛",
   "lyrics": [
     {"song": "カバ", "line": "カバのようにゆっくりと今を味わう"},
     {"song": "カバー曲集より", "line": "他人の歌を借りて自分を歌う"},
   ]},
  {"title": "shamanippon -ロイノチノイ-", "artist": "堂本剛", "artistKey": "tsuyoshi", "period": "SHAMANIPPON", "year": "2014",
   "itunes": "shamanippon ロイノチノイ",
   "lyrics": [
     {"song": "FUNKがしたいんだどしても", "line": "FUNKがしたいんだ どしても"},
     {"song": "ロイノチノイ", "line": "ロイノチノイ"},
   ]},
  {"title": "TU", "artist": "堂本剛", "artistKey": "tsuyoshi", "period": "SHAMANIPPON / TU", "year": "2015",
   "itunes": "TU 堂本剛",
   "lyrics": [
     {"song": "T & U", "line": "T & U ふたりでひとつ"},
     {"song": "Paint it, fill it with love", "line": "Paint it, fill it with love"},
   ]},
  {"title": "Grateful Rebirth", "artist": "堂本剛", "artistKey": "tsuyoshi", "period": "堂本剛", "year": "2016",
   "itunes": "Grateful Rebirth 堂本剛",
   "lyrics": [
     {"song": "Grateful Rebirth", "line": "Grateful Rebirth 再生への礼"},
   ]},
  {"title": "HYBRID FUNK", "artist": "ENDRECHERI", "artistKey": "tsuyoshi", "period": "ENDRECHERI", "year": "2018",
   "itunes": "HYBRID FUNK ENDRECHERI",
   "lyrics": [
     {"song": "one more purple funk… -硬命 katana-", "line": "硬命 katana 斬り裂け"},
     {"song": "HYBRID FUNK", "line": "HYBRID FUNK"},
   ]},
  {"title": "NARALIEN", "artist": "ENDRECHERI", "artistKey": "tsuyoshi", "period": "ENDRECHERI", "year": "2019",
   "itunes": "NARALIEN ENDRECHERI",
   "lyrics": [
     {"song": "4 10 cake (Hot Cake)", "line": "4 10 cake Hot Cake"},
     {"song": "FUNK TRON", "line": "FUNK TRON"},
     {"song": "PURPLE FIRE", "line": "PURPLE FIRE"},
   ]},
  {"title": "LOVE FADERS", "artist": "ENDRECHERI", "artistKey": "tsuyoshi", "period": "ENDRECHERI", "year": "2020",
   "itunes": "LOVE FADERS ENDRECHERI",
   "lyrics": [
     {"song": "LOVE FADERS", "line": "LOVE FADERS フェードする恋を抱きしめて"},
   ]},
  {"title": "GO TO FUNK", "artist": "ENDRECHERI", "artistKey": "tsuyoshi", "period": "ENDRECHERI", "year": "2021",
   "itunes": "GO TO FUNK ENDRECHERI",
   "lyrics": [
     {"song": "GO TO FUNK", "line": "GO TO FUNK"},
     {"song": "Funkatopia選出", "line": "世界のFUNKの棚に置かれた一枚"},
   ]},
  {"title": "Super funk market", "artist": ".ENDRECHERI.", "artistKey": "tsuyoshi", "period": ".ENDRECHERI.", "year": "2023",
   "itunes": "Super funk market ENDRECHERI",
   "lyrics": [
     {"song": "Super funk market", "line": "Welcome to the Super funk market"},
   ]},
  {"title": "END RE", "artist": ".ENDRECHERI.", "artistKey": "tsuyoshi", "period": ".ENDRECHERI. EP", "year": "2025",
   "type": "ep",
   "itunes": "END RE ENDRECHERI",
   "lyrics": [
     {"song": "雑味 feat. George Clinton", "line": "雑味があるから生きてる"},
     {"song": "Machi….", "line": "この街でまた会おう"},
     {"song": ".ENDRECHERI. Brother", "line": ".ENDRECHERI. Brother"},
   ]},

  # —— 堂本光一 ——
  {"title": "mirror", "artist": "堂本光一", "artistKey": "koichi", "period": "堂本光一", "year": "2006",
   "lyrics": [
     {"song": "Deep in your heart", "line": "Deep in your heart 届かない想い"},
     {"song": "mirror", "line": "鏡に映るのは誰？"},
   ]},
  {"title": "BPM", "artist": "堂本光一", "artistKey": "koichi", "period": "堂本光一", "year": "2010",
   "lyrics": [
     {"song": "No more", "line": "No more"},
     {"song": "妖 -ayakashi-", "line": "妖しく揺れる影"},
   ]},
  {"title": "Gravity", "artist": "堂本光一", "artistKey": "koichi", "period": "堂本光一", "year": "2012",
   "lyrics": [
     {"song": "INTERACTIONAL", "line": "INTERACTIONAL"},
     {"song": "Fallen Angel", "line": "Fallen Angel"},
   ]},
  {"title": "Spiral", "artist": "堂本光一", "artistKey": "koichi", "period": "堂本光一", "year": "2015",
   "lyrics": [
     {"song": "Spiral", "line": "Spiral 回り続ける眩暈"},
     {"song": "金色の嘘", "line": "金色の嘘"},
   ]},
  {"title": "PLAYFUL", "artist": "堂本光一", "artistKey": "koichi", "period": "堂本光一", "year": "2021",
   "lyrics": [
     {"song": "Danger Night!", "line": "Danger Night!"},
     {"song": "PLAYFUL", "line": "PLAYFUL 遊べ まだ終わらない"},
   ]},
  {"title": "RAISE", "artist": "堂本光一", "artistKey": "koichi", "period": "堂本光一", "year": "2025",
   "itunes": "RAISE 堂本光一",
   "lyrics": [
     {"song": "RAISE", "line": "RAISE your voice"},
     {"song": "The beginning of the world", "line": "The beginning of the world"},
   ]},
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


def itunes_lookup(album: dict):
    query = album.get("itunes") or f'{album["title"]} {album["artist"]}'
    params = urllib.parse.urlencode({
        "term": query, "country": "jp", "media": "music", "entity": "album", "limit": "10",
    })
    try:
        data = get_json(f"https://itunes.apple.com/search?{params}")
    except Exception:
        return None
    results = data.get("results") or []
    title_l = album["title"].lower().replace("[", "").replace("]", "")
    best, score = None, -1
    for r in results:
        ca = (r.get("collectionName") or "").lower()
        an = (r.get("artistName") or "").lower()
        sc = 0
        if title_l[:8] in ca or ca[:8] in title_l:
            sc += 4
        keys = ("kinki", "domoto", "endre", "endlich", "堂本", "剛紫", "endli", "tsuyoshi", "koichi")
        if any(k in an for k in keys):
            sc += 3
        if album["year"] and str(r.get("releaseDate", "")).startswith(album["year"]):
            sc += 2
        if sc > score:
            score, best = sc, r
    if score < 3:
        return None
    return best


def songlink_spotify(apple_url: str) -> str:
    if not apple_url:
        return ""
    api = "https://api.song.link/v1-alpha.1/links?" + urllib.parse.urlencode({
        "url": apple_url, "userCountry": "JP",
    })
    try:
        data = get_json(api)
        return (data.get("linksByPlatform") or {}).get("spotify", {}).get("url") or ""
    except Exception:
        return ""


def main():
    out = []
    missing_cover = []
    missing_apple = []
    missing_spotify = []

    for i, album in enumerate(ALBUMS):
        title = album["title"]
        slug = f'{album["artistKey"]}-{slugify(title)}-{album["year"]}'
        dest = COVER / f"{slug}.jpg"
        rel = f"covers/{slug}.jpg"
        print(f'[{i+1}/{len(ALBUMS)}] {album["period"]} — {title}', flush=True)

        hit = itunes_lookup(album)
        time.sleep(0.35)
        apple = ""
        spotify = ""
        if hit:
            apple = hit.get("collectionViewUrl") or ""
            art = (hit.get("artworkUrl100") or "").replace("100x100bb", "600x600bb")
            if art and download(art, dest):
                print("  cover OK", flush=True)
            else:
                if not (dest.exists() and dest.stat().st_size > 1000):
                    missing_cover.append(f'{title}（{album["period"]} / {album["year"]}）')
                    rel = ""
                    print("  cover MISSING", flush=True)
            if apple:
                spotify = songlink_spotify(apple)
                time.sleep(0.5)
                if not spotify:
                    # search fallback
                    q = urllib.parse.quote(f'{album["artist"]} {title}')
                    spotify = f"https://open.spotify.com/search/{q}"
                    missing_spotify.append(f'{title}（仅搜索页）')
                    print("  spotify search fallback", flush=True)
                else:
                    print("  apple+spotify OK", flush=True)
            else:
                missing_apple.append(title)
        else:
            if not (dest.exists() and dest.stat().st_size > 1000):
                missing_cover.append(f'{title}（{album["period"]} / {album["year"]}）')
                rel = ""
            missing_apple.append(title)
            q = urllib.parse.quote(f'{album["artist"]} {title}')
            apple = f"https://music.apple.com/jp/search?term={q}"
            spotify = f"https://open.spotify.com/search/{q}"
            print("  itunes miss → search links", flush=True)

        if dest.exists() and dest.stat().st_size > 1000:
            rel = f"covers/{slug}.jpg"

        out.append({
            "id": slug,
            "title": title,
            "artist": album["artist"],
            "artistKey": album["artistKey"],
            "period": album["period"],
            "year": album["year"],
            "type": album.get("type", "album"),
            "cover": rel,
            "lyrics": album.get("lyrics") or [],
            "apple": apple,
            "spotify": spotify,
        })

    (BASE / "albums.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    (BASE / "albums-data.js").write_text(
        "window.ALBUMS_DATA = " + json.dumps(out, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    report = {
        "total": len(out),
        "missing_cover": missing_cover,
        "missing_apple_direct": missing_apple,
        "spotify_search_only": missing_spotify,
    }
    (BASE / "MISSING.md").write_text(
        "# 需要你补充的内容\n\n"
        "## 封面缺失 / 仅占位\n\n"
        + ("\n".join(f"- {x}" for x in missing_cover) or "- （无）")
        + "\n\n## Apple Music 未命中直链（目前是搜索页）\n\n"
        + ("\n".join(f"- {x}" for x in missing_apple) or "- （无）")
        + "\n\n## Spotify 仅搜索页（无精确专辑页）\n\n"
        + ("\n".join(f"- {x}" for x in missing_spotify) or "- （无）")
        + "\n\n## 说明\n\n"
        "- 「DOMOTO 时期 EP」当前按 `.ENDRECHERI.` 的迷你专 **END RE**（2025）收录。\n"
        "- 若你指的是组合 DOMOTO 的 **またね**（多曲单曲/近似 EP），请告诉我，我再加进去。\n"
        "- 歌词为论坛/乐评常见短句摘录；某专你有更想放的金句也可以直接塞给我替换。\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
