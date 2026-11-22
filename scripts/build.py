"""Build the films.json and tv.json in output/. The items in
these two files will be displayed in the personal website as
initial library items.

Step 1: Load all three source files (raw douban data, fetched
tmdb data, and hand fixes)
Step 2: Skip the hidden or unmatched items.
Step 3: build one item.

"""

import json
from datetime import date

from douban import ROOT, load_finished_movies
from fetch_tmdb import load_fixes, load_records, year_of

FILM = ROOT / "output" / "film.json"
TV = ROOT / "output" / "tv.json"


def build_item(movie, record, fix):
    selected = record["selected"]
    details = selected["details"]
    # TMDB data for one season (air_date, poster_path); None for films and whole shows
    season_details = details["season"]

    item_id = movie["subjectId"]
    status = "done"
    title = details["original_title"]

    if season_details is not None:
        year = year_of(season_details["air_date"])
        # A few seasons have no poster of their own: fall back to the show's poster
        poster_path = season_details["poster_path"] or details["poster_path"]
    else:
        year = year_of(details["release_date"])
        poster_path = details["poster_path"]

    # Films have no season key; TV always has one (None = the whole show)
    tmdb = {"id": selected["id"], "media_type": selected["media_type"]}
    if selected["media_type"] == "tv":
        tmdb["season"] = selected["season"]

    marked_at = fix.get("marked_at") or movie["markedAt"]

    return {
        "id": item_id,
        "status": status,
        "title": title,
        "year": year,
        "marked_at": marked_at,
        "poster_path": poster_path,
        "tmdb": tmdb,
    }


def write_output(path, items):
    """Write one category file: {generated_at, count, items}."""
    output = {
        "generated_at": date.today().isoformat(),
        "count": len(items),
        "items": items,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    movies = load_finished_movies()
    fixes = load_fixes()
    records = load_records()

    films = []
    tv = []
    hidden = []
    unmatched = []

    for movie in movies:
        subject_id = movie["subjectId"]
        record = records.get(subject_id)
        fix = fixes.get(subject_id, {})

        # If an item was set "hidden": true manually, it will not be displayed
        if fix.get("hidden"):
            hidden.append(subject_id)
            continue

        # If an item doesn't have a record or have a selected candidate,
        # then it isn't displayed either
        if record is None or record["selected"] is None:
            if fix.get("id"):
                print(
                    f"warning: {subject_id} has a fix but no fetched data; run fetch_tmdb.py"
                )
            unmatched.append(subject_id)
            continue

        media_type = record["selected"]["media_type"]
        if media_type == "movie":
            films.append(build_item(movie, record, fix))
        elif media_type == "tv":
            tv.append(build_item(movie, record, fix))
        else:
            print(f"warning: {subject_id} has unknown media_type {media_type}")

    # Sort films and tv list
    films.sort(key=lambda item: (item["marked_at"], item["id"]), reverse=True)
    tv.sort(key=lambda item: (item["marked_at"], item["id"]), reverse=True)

    # Write list to output/film.json and output/tv.json
    write_output(FILM, films)
    write_output(TV, tv)

    print(
        f"films: {len(films)}, tv: {len(tv)}, unmatched: {len(unmatched)}, hidden: {len(hidden)}"
    )
    print(
        f"total: {len(films) + len(tv) + len(unmatched) + len(hidden)} / {len(movies)}"
    )
    print(f"wrote {FILM.relative_to(ROOT)} and {TV.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
