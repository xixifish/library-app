"""Check fetch_tmdb.py against the records written by hand in docs/fetch-examples.json.

Each example is fetched again (from TMDB, nothing is saved) and compared with the
hand-written record, field by field. `fetch_date` is ignored. A `fixed` example is
fetched with its own fix, and with the `manual` example of the same item as the
earlier record, the way a real re-run after a fix works.

Run from library-app/ with the virtual environment active:
    python scripts/check_examples.py
"""

import json
import os
import sys

from dotenv import load_dotenv

from douban import ROOT, load_finished_movies
from fetch_tmdb import fetch_record

EXAMPLES = ROOT / "docs" / "fetch-examples.json"


def main():
    load_dotenv(ROOT / ".env")
    if not os.environ.get("TMDB_TOKEN"):
        sys.exit("TMDB_TOKEN is missing: put it in library-app/.env")

    by_id = {movie["subjectId"]: movie for movie in load_finished_movies()}
    with open(EXAMPLES, encoding="utf-8") as f:
        examples = json.load(f)

    previous_by_id = {}  # the example before, for the same item
    for example in examples:
        subject_id = example["douban"]["subjectId"]
        movie = by_id[subject_id]
        fix = None
        if example["status"] == "fixed":
            selected = example["selected"]
            fix = {
                "id": selected["id"],
                "media_type": selected["media_type"],
                "season": selected["season"],
            }
        record = fetch_record(movie, fix, previous_by_id.get(subject_id))
        previous_by_id[subject_id] = example

        differences = [
            key for key in example if key != "fetch_date" and record[key] != example[key]
        ]
        label = f"{movie['title']} ({example['status']})"
        if not differences:
            print(f"ok         {label}")
            continue
        print(f"DIFFERENT  {label}: {', '.join(differences)}")
        for key in differences:
            print(f"    got:      {json.dumps(record[key], ensure_ascii=False)[:300]}")
            print(f"    expected: {json.dumps(example[key], ensure_ascii=False)[:300]}")


if __name__ == "__main__":
    main()
