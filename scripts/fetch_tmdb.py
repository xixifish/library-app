"""Fetch TMDB data for finished Douban films and TV.

Step 1: build each item's `search` part (query, year, season) from the raw export.
Step 2: search TMDB and turn the results into `candidates`.
Step 3: select the match by the year rule (seasons: the season's own air_date).

The parts live in douban.py (the raw data) and tmdb.py (the TMDB requests).
Rules: docs/requirements.md, "TMDB matching". Record format: docs/fetch-examples.json.
Run from library-app/ with the virtual environment active: python scripts/fetch_tmdb.py
"""

import json
import os
import sys

from dotenv import load_dotenv
from douban import ROOT, build_fallback_query, build_search, load_finished_movies
from tmdb import get_tv_details, search_tmdb

EXAMPLES = ROOT / "docs" / "fetch-examples.json"


def find_candidates(movie, search):
    """Search TMDB with search["query"]. If that finds nothing, search again with
    Douban's Chinese title (season part removed) and note it in
    search["fallback_query"], so the record shows which query found the candidates.
    The year and season checks in select_candidate apply either way."""
    candidates = search_tmdb(search)
    if candidates:
        return candidates
    fallback = build_fallback_query(movie)
    if fallback == search["query"]:
        return candidates  # the same search again would find nothing new
    search["fallback_query"] = fallback
    return search_tmdb({**search, "query": fallback})


def year_of(date):
    """'2026-09-16' → 2026; None (no date) → None."""
    return int(date[:4]) if date else None


def find_season(details, season_number):
    """The entry for one season in a show's `seasons` list, or None if TMDB
    doesn't have that season."""
    for season in details["seasons"]:
        if season["season_number"] == season_number:
            return season
    return None


def select_candidate(search, candidates):
    """Pick the match by the year rule. Always returns two values:
    (candidate, details) for a season item, (candidate, None) for a film or a
    whole show (details come later), (None, None) if nothing passes (-> manual).

    - Film or whole show: the first candidate whose year is within 1 of Douban's.
    - TV season: the first show whose season `search["season"]` aired within 1 year
      of Douban's year. That needs /tv/{id}, one request per show checked.
    """
    if search["year"] is None:
        return None, None

    if search["season"] is not None:
        for candidate in candidates:
            # A season can't air before its show started: skip such shows
            # without spending a request.
            show_year = year_of(candidate["release_date"])
            if show_year is not None and show_year > search["year"] + 1:
                continue
            details = get_tv_details(candidate["id"], candidate["original_language"])
            season = find_season(details, search["season"])
            if season is None:
                continue
            season_year = year_of(season["air_date"])
            if season_year is not None and abs(season_year - search["year"]) <= 1:
                return candidate, details
        return None, None

    for candidate in candidates:
        year = year_of(candidate["release_date"])
        if year is not None and abs(year - search["year"]) <= 1:
            return candidate, None
    return None, None


def main():
    load_dotenv(ROOT / ".env")
    if not os.environ.get("TMDB_TOKEN"):
        sys.exit("TMDB_TOKEN is missing: put it in library-app/.env")

    movies = load_finished_movies()
    by_id = {
        # { movie_douban_id: movie }
        movie["subjectId"]: movie
        for movie in movies
    }

    # Check against the examples, which were written by hand:
    # does the code build the same `search`, and does TMDB return the same candidates?
    with open(EXAMPLES, encoding="utf-8") as f:
        examples = json.load(f)
    print("Examples:")
    for example in examples:
        movie = by_id[example["douban"]["subjectId"]]
        built = build_search(movie)
        result = (
            "ok"
            if built == example["search"]
            else f"DIFFERENT, expected {example['search']}"
        )
        print(f"\n  {movie['title']}: search {built} {result}")

        candidates = find_candidates(movie, built)
        selected, details = select_candidate(built, candidates)
        for candidate in candidates:
            print(
                f"    {candidate['media_type']:5} {candidate['id']:>8}  "
                f"{candidate['release_date']}  {candidate['title']}"
            )
        same = [c["id"] for c in candidates] == [c["id"] for c in example["candidates"]]
        print(
            f"  candidates: {len(candidates)}, "
            + (
                "same as the example"
                if same
                else f"DIFFERENT from the example ({len(example['candidates'])})"
            )
        )
        # What the rule should pick: the example's match if it was `matched`.
        # For `manual` and `fixed` the rule finds nothing (a `fixed` match is my own).
        if example["status"] == "matched":
            expected_id = example["selected"]["id"]
        else:
            expected_id = None
        selected_id = selected["id"] if selected else None
        if selected is None:
            description = "none (manual)"
        else:
            description = (
                f"{selected['media_type']} {selected['id']} {selected['release_date']}"
            )
            if details is not None:  # only season matches have details at this point
                season = find_season(details, built["season"])
                if season is not None:
                    description += (
                        f", season {built['season']} aired {season['air_date']}"
                    )
        selection_result = (
            "ok" if selected_id == expected_id else f"DIFFERENT, expected {expected_id}"
        )
        print(f"  selected: {description} {selection_result}")


if __name__ == "__main__":
    main()
