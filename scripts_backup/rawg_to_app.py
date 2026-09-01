#!/usr/bin/env python3
"""Convert the RAWG PS3 extract (54 raw fields, pipe-joined) into the
ps3-game-library.html app schema (comma-joined, app-friendly fields).

Field mapping (54 RAWG fields are ALL preserved — raw values kept verbatim
in `_raw` for the full-detail viewer):
  name->title  released->released(+year)  rating(1-5)->user_score(0-100)
  metacritic->critic_score  playtime->playtime  developers->developer
  publishers->publisher  genres/|tags/platforms -> comma-joined
  esrb_rating(JSON)->content_rating  ratings(JSON)->critic_sentiment +
  user_score_sentiment  ratings_count->critic_count
  reviews_text_count->user_score_count  achievements_count->achievements_count
  tba -> title suffix "TBA"  DLC detection -> is_dlc
"""
import json, re, sys

SRC = "/tmp/ps3_full.json"
DST = "/data/workspace/HermesBackup/ps3_games.json"

data = json.load(open(SRC, encoding="utf-8"))
print("source rows:", len(data))

DLC_PAT = re.compile(
    r"(?::\s*dlc\b|\bdlc\b|\bexpansion\b|\badd-?on\b|\bsoundtrack\b|\bskin pack\b|\bdeluxe bundle\b|\bseason pass\b|\bstandalone expansion\b)",
    re.I)

def fnum(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def jl(v):
    """parse a rawg json-ish string; return {} on failure"""
    if not v or not isinstance(v, str):
        return {}
    try:
        return json.loads(v)
    except Exception:
        return {}

def top_segment(ratings_json):
    """largest RAWG rating segment -> lowercase title, or None"""
    segs = [s for s in re.findall(r"\{[^{}]*\}", ratings_json or "") if s]
    best, best_p = None, -1.0
    for s in segs:
        try:
            m = dict(re.findall(r"(\w+):\s*([^,}]+)", s))
            p = float(m.get("percent", 0))
            if p > best_p:
                best, best_p = m.get("title", "").strip().lower(), p
        except Exception:
            continue
    return best or None

ESRB_SHORT = {
    "everyone": "E", "everyone 10+": "E10+", "teen": "T",
    "mature": "M", "adults only": "AO", "rating pending": "RP",
}

def nice_name(name):
    # strip rawg parenthetical suffixes for display title only if empty later
    return (name or "").strip()

out = []
for g in data:
    raw = dict(g)  # all 54 fields verbatim
    name = nice_name(g.get("name")) or "(untitled)"
    released = (g.get("released") or "").strip()
    year = released[:4] if re.match(r"^\d{4}", released) else None
    if str(g.get("tba")).strip() in ("1", "1.0", "True", "true") or released.lower() == "tba":
        year = "TBA"

    mc = fnum(g.get("metacritic"))
    us = fnum(g.get("rating"))
    rating_top = fnum(g.get("rating_top")) or 5.0
    # normalize RAWG 1..rating_top -> 0..100
    user_score = None
    if us is not None:
        user_score = round(max(0.0, min(100.0, (us / 5.0) * 100.0)), 1)

    parents = fnum(g.get("parents_count")) or 0
    name_dlc = bool(DLC_PAT.search(name))
    is_dlc = parents > 0 or name_dlc

    esrb = jl(g.get("esrb_rating"))
    esrb_name = (esrb.get("name") or "").strip()
    content_rating = ESRB_SHORT.get(esrb_name.lower(), esrb_name or None)

    ratings_json = g.get("ratings") or ""
    sentiment = top_segment(ratings_json)
    # map largest segment onto the app's critic/user sentiment fields
    critic_sentiment = sentiment
    user_score_sentiment = sentiment

    platforms = (g.get("platforms") or "").replace("|", ", ")
    genres = (g.get("genres") or "").replace("|", ", ")
    tags = (g.get("tags") or "").replace("|", ", ")
    developers = (g.get("developers") or "").replace("|", ", ")
    publishers = (g.get("publishers") or "").replace("|", ", ")

    series = ""  # RAWG has no series field; game_series_count is numeric only
    achievements = fnum(g.get("achievements_count"))
    achievements = int(achievements) if achievements is not None else None

    rec = {
        "title": name,
        "genres": genres or None,
        "developer": developers or None,
        "publisher": publishers or None,
        "platforms": platforms or None,
        "year": year,
        "released": released or None,
        "playtime": fnum(g.get("playtime")),
        "tags": tags or None,
        "is_dlc": is_dlc,
        "critic_score": int(mc) if mc is not None else None,
        "user_score": user_score,
        "critic_count": int(fnum(g.get("ratings_count"))) if fnum(g.get("ratings_count")) is not None else None,
        "user_score_count": int(fnum(g.get("reviews_text_count"))) if fnum(g.get("reviews_text_count")) is not None else None,
        "critic_sentiment": critic_sentiment,
        "user_score_sentiment": user_score_sentiment,
        "content_rating": content_rating,
        "series": series or None,
        "achievements_count": achievements,
        "background_image": g.get("background_image") or None,
        "website": g.get("website") or None,
        "reddit_url": g.get("reddit_url") or None,
        "metacritic_url": g.get("metacritic_url") or None,
        "description": (g.get("description_raw") or "").strip() or None,
        "_raw": raw,
    }
    out.append(rec)

# ---- validation ----
n = len(out)
assert n == 3209, f"expected 3209 rows, got {n}"
required = ["title", "genres", "developer", "publisher", "platforms", "year",
            "released", "playtime", "tags", "is_dlc", "critic_score", "user_score",
            "critic_count", "user_score_count", "critic_sentiment",
            "user_score_sentiment", "content_rating", "series",
            "achievements_count", "background_image", "website", "reddit_url",
            "metacritic_url", "description", "_raw"]
bad_schema = [r["title"] for r in out if set(r.keys()) != set(required)]
assert not bad_schema, f"rows with wrong field set: {bad_schema[:5]}"
RAWG54 = ["id","slug","name","released","background_image","rating","rating_top",
          "ratings_count","reviews_text_count","added","metacritic","playtime",
          "suggestions_count","updated","reviews_count","saturated_color",
          "dominant_color","platforms","stores","developers","genres","tags",
          "publishers","esrb_rating","added_by_status","metacritic_url","ratings",
          "clip","name_original","reddit_url","movies_count","reactions",
          "background_image_additional","website","reddit_count","achievements_count",
          "youtube_count","short_screenshots","creators_count","twitch_count",
          "alternative_names","parent_achievements_count","additions_count",
          "metacritic_platforms","screenshots_count","parent_platforms",
          "game_series_count","description","description_raw","parents_count",
          "reddit_name","reddit_description","reddit_logo","tba"]
bad_raw = [r["title"] for r in out if set(r["_raw"].keys()) != set(RAWG54)]
assert not bad_raw, f"rows with wrong _raw field set: {bad_raw[:5]}"

ndlc = sum(1 for r in out if r["is_dlc"])
print(f"rows: {n} | DLC-flagged: {ndlc} | games: {n - ndlc}")
print(f"titles unique: {len({r['title'] for r in out})}")
print(f"with critic_score: {sum(1 for r in out if r['critic_score'] is not None)}")
print(f"with user_score: {sum(1 for r in out if r['user_score'] is not None)}")
print(f"with content_rating: {sum(1 for r in out if r['content_rating'])}")
print(f"with description: {sum(1 for r in out if r['description'])}")

json.dump(out, open(DST, "w", encoding="utf-8"), ensure_ascii=False)
import os
print("written:", DST, round(os.path.getsize(DST) / 1e6, 1), "MB")
