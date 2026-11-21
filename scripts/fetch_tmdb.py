"""Fetch TMDB data for finished Douban films and TV, one record per item.

Step 1: build each item's `search` part (query, year, season) from the raw export.
Step 2: search TMDB and turn the results into `candidates`.
Step 3: select the match by the year rule (seasons: the season's own air_date).
Step 4: get the match's details and build the record's `selected` part.
Step 5: apply my fixes (data/fixes.json), write each record as soon as it's done,
        and resume: items that already have a record are skipped.

Records go to cache/tmdb-records.jsonl, one JSON record per line, appended. If an
item is fetched again (e.g. after a fix), its newer line wins.
The parts live in douban.py (the raw data) and tmdb.py (the TMDB requests).
Rules: docs/requirements.md, "TMDB matching". Record format: docs/fetch-examples.json.

Run from library-app/ with the virtual environment active:
    python scripts/fetch_tmdb.py            # everything not fetched yet
    python scripts/fetch_tmdb.py --limit 5  # only the next 5, for a test
    python scripts/fetch_tmdb.py --refetch 1301578 1434269  # these items again
    python scripts/fetch_tmdb.py --all      # every item again (after a format change)
"""

import argparse
import json
import os
import sys
import unicodedata
from collections import Counter
from datetime import date

import requests
from dotenv import load_dotenv

from douban import ROOT, build_fallback_query, build_search, load_finished_movies
from tmdb import get_details, get_tv_details, search_tmdb, to_details, find_season

RECORDS = ROOT / "cache" / "tmdb-records.jsonl"
FIXES = ROOT / "data" / "fixes.json"


# --- Steps 1–4: search, select, details ---


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


def same_title(a, b):
    """Titles equal after normalizing: full-width characters become normal ones
    (Douban '(上)' vs TMDB '（上）', '：' vs ':') and spaces are ignored."""

    def normalize(text):
        return unicodedata.normalize("NFKC", text or "").replace(" ", "")

    return normalize(a) == normalize(b)


def year_of(date_text):
    """'2026-09-16' → 2026; None (no date) → None."""
    return int(date_text[:4]) if date_text else None


def select_candidate(search, candidates, douban_title):
    """Pick the match by the year rule. Always returns two values:
    (candidate, details) for a season item, (candidate, None) for a film or a
    whole show (details come later), (None, None) if nothing passes (-> manual).

    - Film or whole show: among the candidates whose year is within 1 of Douban's,
      preferred in this order: the exact Douban Chinese title, then the smaller
      year difference, then TMDB's order.
      (Without the title preference, a TV show that only contains the title, e.g.
      Transformers: Animated for 变形金刚, could come first and win.)
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

    passing = []
    for candidate in candidates:
        year = year_of(candidate["release_date"])
        if year is not None and abs(year - search["year"]) <= 1:
            passing.append(candidate)
    if not passing:
        return None, None
    # Best first: the exact Chinese title, then the smaller year difference, then
    # TMDB's order (min() keeps the earliest of equal candidates).
    best = min(
        passing,
        key=lambda candidate: (
            not same_title(candidate["title"], douban_title),
            abs(year_of(candidate["release_date"]) - search["year"]),
        ),
    )
    return best, None


def build_selected(match, details, search):
    """The record's `selected` part for a matched candidate. `details` is the full
    response if select_candidate already fetched it (season items); otherwise it is
    requested here (films and whole shows), one request."""
    if details is None:
        details = get_details(match["media_type"], match["id"], match["original_language"])
    return {
        "id": match["id"],
        "media_type": match["media_type"],
        "season": search["season"],
        "original_language": match["original_language"],
        "details": to_details(details, search["season"]),
    }


# --- Step 5: fixes, whole records, saving, resuming ---


def status_code(error):
    """The HTTP status of a requests.HTTPError, or None. `error.response` is always
    set by raise_for_status(), but its type allows None, so check it."""
    return error.response.status_code if error.response is not None else None


def selected_from_fix(fix, candidates):
    """The `selected` part for a match I chose by hand. The fix gives only `id`,
    `media_type` and `season`; the original language (for the poster) comes from the
    candidates if the id is among them, else from one extra request."""
    language = next(
        (
            c["original_language"]
            for c in candidates
            if c["id"] == fix["id"] and c["media_type"] == fix["media_type"]
        ),
        None,
    )
    if language is None:
        language = get_details(fix["media_type"], fix["id"], None)["original_language"]
    details = get_details(fix["media_type"], fix["id"], language)
    season = fix.get("season")
    return {
        "id": fix["id"],
        "media_type": fix["media_type"],
        "season": season,  # TMDB's season number, which can differ from Douban's
        "original_language": language,
        "details": to_details(details, season),
    }


def fetch_record(movie, fix=None, previous=None):
    """The whole record for one item (format: docs/fetch-examples.json).

    - A fix with an id: no search; `fixed`, with details for my chosen id. The
      search and candidates of an earlier record are kept: they show why the item
      needed me.
    - A fix with only `hidden`: checked by me and not on TMDB → `not_on_tmdb`.
    - No fix: search, select and get details → `matched` or `manual`.
    """
    record = {
        "fetch_date": date.today().isoformat(),
        "status": None,
        "douban": {
            "subjectId": movie["subjectId"],
            "title": movie["title"],
            "originalTitle": movie["originalTitle"],
            "info": movie["info"],
        },
        "search": build_search(movie),
        "candidates": [],
        "selected": None,
    }

    if fix is not None:
        if previous is not None:
            record["search"] = previous["search"]
            record["candidates"] = previous["candidates"]
        if "id" not in fix:
            record["status"] = "not_on_tmdb"
            return record
        try:
            record["selected"] = selected_from_fix(fix, record["candidates"])
            record["status"] = "fixed"
        except requests.HTTPError as error:
            if status_code(error) != 404:
                raise
            print(f"    fix id {fix['id']} not found on TMDB: check data/fixes.json")
            record["status"] = "manual"
        return record

    search = record["search"]
    record["candidates"] = find_candidates(movie, search)
    match, details = select_candidate(search, record["candidates"], movie["title"])
    if match is None:
        record["status"] = "manual"
    else:
        record["status"] = "matched"
        record["selected"] = build_selected(match, details, search)
    return record


def needs_fetch(fix, previous):
    """Fetch an item if it has no record yet, or if its fix isn't applied yet."""
    if previous is None:
        return True
    if fix is None:
        return False
    if "id" not in fix:
        return previous["status"] != "not_on_tmdb"
    selected = previous["selected"]
    return (
        previous["status"] != "fixed"
        or selected is None
        or selected["id"] != fix["id"]
        or selected["media_type"] != fix["media_type"]
        or selected["season"] != fix.get("season")
    )


def load_fixes():
    if not FIXES.exists():
        return {}
    with open(FIXES, encoding="utf-8") as f:
        return json.load(f)


def load_records():
    """All saved records by subjectId; a later line for the same item wins."""
    records = {}
    if RECORDS.exists():
        with open(RECORDS, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    records[record["douban"]["subjectId"]] = record
    return records


def append_record(record):
    """Write one record right away, so a stop loses at most the current item."""
    RECORDS.parent.mkdir(exist_ok=True)
    with open(RECORDS, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Fetch TMDB data for Douban films and TV.")
    parser.add_argument("--limit", type=int, help="fetch at most this many items")
    parser.add_argument(
        "--refetch",
        nargs="+",
        metavar="SUBJECT_ID",
        help="fetch only these items, even if they already have a record "
        "(e.g. after a rule change)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="fetch every item again, e.g. after the record format changed; "
        "fixes still apply",
    )
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    if not os.environ.get("TMDB_TOKEN"):
        sys.exit("TMDB_TOKEN is missing: put it in library-app/.env")

    movies = load_finished_movies()
    fixes = load_fixes()
    records = load_records()
    if args.all:
        todo = list(movies)
    elif args.refetch:
        wanted = set(args.refetch)
        todo = [movie for movie in movies if movie["subjectId"] in wanted]
        unknown = wanted - {movie["subjectId"] for movie in todo}
        if unknown:
            print(f"Not finished items in the export, ignored: {', '.join(sorted(unknown))}")
    else:
        todo = [
            movie
            for movie in movies
            if needs_fetch(fixes.get(movie["subjectId"]), records.get(movie["subjectId"]))
        ]
    print(f"{len(movies)} finished items, {len(records)} with a record, {len(todo)} to fetch.")
    if args.limit is not None:
        todo = todo[: args.limit]

    skipped = 0
    try:
        for number, movie in enumerate(todo, start=1):
            subject_id = movie["subjectId"]
            try:
                record = fetch_record(movie, fixes.get(subject_id), records.get(subject_id))
            except requests.HTTPError as error:
                if status_code(error) == 401:
                    sys.exit("TMDB says 401 Unauthorized: check TMDB_TOKEN in .env")
                print(f"[{number}/{len(todo)}] skipped {movie['title']}: {error}")
                skipped += 1
                continue
            except (requests.ConnectionError, requests.Timeout) as error:
                print(f"[{number}/{len(todo)}] skipped {movie['title']}: {error}")
                skipped += 1
                continue
            append_record(record)
            print(f"[{number}/{len(todo)}] {record['status']:11} {movie['title']}")
    except KeyboardInterrupt:
        print("\nStopped. Run again to continue where it stopped.")

    statuses = Counter(record["status"] for record in load_records().values())
    print(f"\nRecords: {dict(statuses)}. Skipped this run (tried again next run): {skipped}.")


if __name__ == "__main__":
    main()
