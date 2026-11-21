"""README step 2: test TMDB matching on about 20 titles.

Runs steps 1–3 of fetch_tmdb.py (search → candidates → selection) on titles chosen
for the risky cases, and prints the result for a person to judge: right match,
correctly manual, or WRONG match (the important one, since it slips through silently).
Nothing is saved.

Run from library-app/ with the virtual environment active:
    python scripts/test_matching.py
"""

import os
import sys

from dotenv import load_dotenv

from douban import ROOT, build_search, load_finished_movies
from tmdb import find_season
from fetch_tmdb import find_candidates, select_candidate

# subjectId → why this title is in the test
TEST_TITLES = {
    # The 7 titles first tested by hand on 2026-11-20 (doc, TMDB matching)
    "1296148": "玛蒂尔达: original title is English",
    "36689816": "流人 第六季: season, season's own air_date",
    "37071123": "铁拳教育: Korean show without a season marker",
    "38462800": "直到T恤干透: Japanese, full-width Ｔ",
    "1434269": "黑炮事件: 1-year gap (1986 vs 1985)",
    "4719384": "哀乐中年: old film, year only",
    "3010220": "杨门女将: no date → manual",
    # Cut-off original titles ("...")
    "30304994": "奇异博士2: cut-off English title",
    "37501131": "现在不是出轨的问题: cut-off Korean title",
    "6729183": "美国恐怖故事 第一季: cut-off title and a season",
    # Season written in a form the script doesn't remove
    "36193784": "黑暗荣耀 第二季: 더 글로리2",
    "26882339": "一拳超人 第二季: ワンパンマン 第2期",
    "6855097": "夏目友人帐 第四季: 夏目友人帳 肆",
    "36464643": "物理魔法使马修 第二季: season subtitle in the title",
    # First season with no marker in the original title
    "30458442": "动物狂想曲 第一季: BEASTARS",
    "34812928": "鱿鱼游戏 第一季: 오징어 게임",
    # Season item with no original title
    "35236741": "吐槽大会 第五季: Chinese variety show",
    # No date, or a common title
    "35322194": "西游记 (no date): many versions → manual",
    "2156663": "西游记 (1986): common title, but with a year",
    "19965274": "杨门女将之女将初征: no date, two same-name candidates",
    # Year-only date
    "19965275": "杨门女将之情定穆柯寨: year only, expect 1088882",
}

SHOW_CANDIDATES = 5  # how many candidates to print per title


def main():
    load_dotenv(ROOT / ".env")
    if not os.environ.get("TMDB_TOKEN"):
        sys.exit("TMDB_TOKEN is missing: put it in library-app/.env")

    by_id = {movie["subjectId"]: movie for movie in load_finished_movies()}
    matched = 0

    for subject_id, why in TEST_TITLES.items():
        movie = by_id[subject_id]
        search = build_search(movie)
        candidates = find_candidates(movie, search)
        selected, details = select_candidate(search, candidates, movie["title"])

        print(f"\n{why}")
        print(f"  douban: {movie['title']} | {movie['originalTitle']!r} | {movie['info'][:20]!r}")
        print(f"  search: {search}")
        print(f"  candidates: {len(candidates)}")
        for candidate in candidates[:SHOW_CANDIDATES]:
            print(
                f"    {candidate['media_type']:5} {candidate['id']:>8}  "
                f"{candidate['release_date']}  {candidate['title']}"
            )
        if selected is None:
            print("  → manual")
            continue
        matched += 1
        line = f"  → {selected['media_type']} {selected['id']} {selected['release_date']} {selected['title']}"
        if details is not None:
            season = find_season(details, search["season"])
            if season is not None:
                line += f", season {search['season']} aired {season['air_date']}"
        print(line)

    print(f"\nMatched {matched} of {len(TEST_TITLES)}, manual {len(TEST_TITLES) - matched}.")


if __name__ == "__main__":
    main()
