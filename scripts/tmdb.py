"""Talking to TMDB: requests, search, and turning results into candidates.

Needs TMDB_TOKEN in the environment (fetch_tmdb.py loads it from library-app/.env).
Rules: docs/requirements.md, "TMDB matching".
"""

import os
import time

import requests

TMDB_API = "https://api.themoviedb.org/3"
SEARCH_LANGUAGE = "zh-CN"  # only sets the language of the results, not what matches
REQUEST_DELAY = 0.25  # seconds to wait after every request, to stay polite


def tmdb_get(path, params):
    """One GET request to TMDB. Stops with an error on a bad token or server error,
    so a problem never looks like "no results". Waits REQUEST_DELAY afterwards, so
    no caller can forget the pause."""
    response = requests.get(
        TMDB_API + path,
        headers={"Authorization": f"Bearer {os.environ['TMDB_TOKEN']}"},
        params=params,  # requests URL-encodes these, like curl's --data-urlencode
        timeout=10,
    )
    time.sleep(REQUEST_DELAY)
    response.raise_for_status()
    return response.json()  # parse the JSON that TMDB sent to a Python dict


def to_candidate(result, media_type):
    """Keep the fields a person needs to judge a result, under the same names for
    films and TV (TV's `name` / `first_air_date` become `title` / `release_date`)."""
    return {
        "id": result["id"],
        "media_type": media_type,
        "title": result.get("title") or result.get("name"),
        "release_date": result.get("release_date")
        or result.get("first_air_date")
        or None,
        "original_language": result.get("original_language"),
    }


def search_tmdb(search):
    """Search TMDB for one item; return its candidates (first page only).

    Season items must be TV, so they use /search/tv (its results have no
    `media_type`). Everything else uses /search/multi, minus `person` results."""
    params = {"query": search["query"], "language": SEARCH_LANGUAGE}
    if search["season"] is not None:
        results = tmdb_get("/search/tv", params)["results"]
        return [to_candidate(result, "tv") for result in results]
    results = tmdb_get("/search/multi", params)["results"]
    return [
        to_candidate(result, result["media_type"])
        for result in results
        if result["media_type"] in ("movie", "tv")
    ]


def get_tv_details(show_id, original_language):
    """A show's details, in its original language (for the poster). Includes the
    `seasons` list, with each season's `season_number`, `air_date` and `poster_path`."""
    params = {"language": original_language}
    details = tmdb_get(f"/tv/{show_id}", params)
    return details
