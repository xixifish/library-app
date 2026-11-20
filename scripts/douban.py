"""Reading the raw Douban export: finished films/TV, and what to search TMDB with.

Rules: docs/requirements.md, "TMDB matching".
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # scripts/ → library-app/
RAW_MOVIES = ROOT / "raw" / "movies.json"

# `info` starts with a full or partial date: "1986(中国大陆) / ...",
# "2004-09(柏林电影节) / ...", "2026-09-16(英国) / ...". Only the year is needed.
YEAR_AT_START = re.compile(r"^(\d{4})(?!\d)")

# The season number comes from Douban's Chinese title: every season item has
# "第X季" there, while `originalTitle` writes it many ways (or not at all).
SEASON_IN_TITLE = re.compile(r"\s*第([一二三四五六七八九十\d]+)季")

# Season text to remove from `originalTitle` before searching. Covers the common
# forms in the data; anything else is searched as it is.
SEASON_IN_ORIGINAL = [
    re.compile(r"\s*Season\s*\d+", re.IGNORECASE),  # Slow Horses Season 6
    re.compile(r"\s*\d+(st|nd|rd|th)\s+Season", re.IGNORECASE),  # BEASTARS 2nd Season
    re.compile(r"\s*シーズン\s*\d+"),  # 全裸監督 シーズン1
    re.compile(r"\s*시즌\s*\d+"),  # 오징어 게임 시즌 3
]

CHINESE_DIGITS = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
}


def load_finished_movies():
    with open(RAW_MOVIES, encoding="utf-8") as f:
        records = json.load(f)["records"]
    return [movie for movie in records if movie["status"] == "collect"]


def chinese_number(text):
    """'六' → 6, '十' → 10, '十二' → 12, '二十一' → 21, '3' → 3."""
    if text.isdigit():
        return int(text)
    if "十" in text:
        tens, _, ones = text.partition("十")
        return CHINESE_DIGITS.get(tens, 1) * 10 + CHINESE_DIGITS.get(ones, 0)
    return CHINESE_DIGITS[text]


def parse_year(info):
    """The year at the start of `info`, or None if it doesn't start with a date."""
    match = YEAR_AT_START.match(info or "")
    return int(match.group(1)) if match else None


def parse_season(title):
    """The season number from '流人 第六季', or None for a film or a whole show."""
    match = SEASON_IN_TITLE.search(title)
    return chinese_number(match.group(1)) if match else None


def build_query(movie, season):
    """`originalTitle` if present, else `title`; season text removed for a season item."""
    original = movie["originalTitle"].strip()
    # The export cut some long original titles short: "Doctor Strange in the
    # Multiverse of ...". Search with the part that's there.
    if original.endswith("..."):
        original = original.removesuffix("...").strip()
    query = original or movie["title"]
    if season is not None:
        if original:
            for pattern in SEASON_IN_ORIGINAL:
                query = pattern.sub("", query)
        else:
            query = SEASON_IN_TITLE.sub("", query)
    return query.strip()


def build_fallback_query(movie):
    """Douban's Chinese title without the season part: the second search when the
    first finds nothing (e.g. '黑暗荣耀 第二季' → '黑暗荣耀')."""
    return SEASON_IN_TITLE.sub("", movie["title"]).strip()


def build_search(movie):
    """`fallback_query` stays None unless the fallback search is used."""
    season = parse_season(movie["title"])
    return {
        "query": build_query(movie, season),
        "year": parse_year(movie["info"]),
        "season": season,
        "fallback_query": None,
    }
