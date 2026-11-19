import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # scripts/ → library-app/
RAW = ROOT / "raw"

with open(RAW / "books.json", encoding="utf-8") as f:
    books = json.load(f)

print(json.dumps(books[0], indent=2, ensure_ascii=False))

with open(RAW / "movies.json", encoding="utf-8") as f:
    movies_data = json.load(f)

movies = movies_data["records"]
print(json.dumps(movies[0], indent=2, ensure_ascii=False))

# Check each property and how many of them are not empty
# Books
book_properties = {}
for book in books:
    for key, value in book.items():
        if value not in ["", [], None]:
            book_properties[key] = book_properties.get(key, 0) + 1
        book_properties[key] = book_properties.get(key, 0)

print(book_properties)
# Movies/tv
movie_properties = {}
for movie in movies:
    for key, value in movie.items():
        if value not in ["", [], None]:
            movie_properties[key] = movie_properties.get(key, 0) + 1
        movie_properties[key] = movie_properties.get(key, 0)

print(movie_properties)

# Check status
print(Counter(book.get("status") for book in books))
print(Counter(movie.get("status") for movie in movies))

# Check `markedAt`
# 1. What are the earliest and latest dates?
# 2. Which records are missing one?
# Books
book_markedAts = []
for book in books:
    new_book_dict = {
        "subjectId": book.get("subjectId"),
        "title": book.get("title"),
    }
    marked_at = book.get("markedAt")
    if not marked_at:  # Covers marked_at is "", key is none or missing
        new_book_dict["markedAt"] = None
    else:
        new_book_dict["markedAt"] = datetime.strptime(marked_at, "%Y-%m-%d").date()
    book_markedAts.append(new_book_dict)

b_dates = [b["markedAt"] for b in book_markedAts if b["markedAt"] is not None]

print(f"Books' earliest marked at {min(b_dates)}")
print(f"Books' latest marked at {max(b_dates)}")


print("Books without markedat data:")
for book_markedAt in book_markedAts:
    if book_markedAt["markedAt"] is None:
        print(book_markedAt["title"], book_markedAt["subjectId"])

# Movies
movie_markedAts = []
for movie in movies:
    new_movie_dict = {
        "subjectId": movie.get("subjectId"),
        "title": movie.get("title"),
    }
    marked_at = movie.get("markedAt")
    if marked_at == "":
        new_movie_dict["markedAt"] = None
    else:
        new_movie_dict["markedAt"] = datetime.strptime(marked_at, "%Y-%m-%d").date()
    movie_markedAts.append(new_movie_dict)

m_dates = [m["markedAt"] for m in movie_markedAts if m["markedAt"] is not None]

print(f"Movies' earliest marked at {min(m_dates)}")
print(f"Movies' latest marked at {max(m_dates)}")

print("Movies without markedat data:")
for movie_markedAt in movie_markedAts:
    if movie_markedAt["markedAt"] is None:
        print(movie_markedAt["title"], movie_markedAt["subjectId"])

# Print `info` data of 5 moive records
print("info data of 5 movie records:")
for movie in movies[:5]:
    print(movie.get("info"))


# --- Step 1, remaining checks ---
# v1 only shows finished items, so from here on look at `collect` records only.
finished_books = [book for book in books if book.get("status") == "collect"]
finished_movies = [movie for movie in movies if movie.get("status") == "collect"]
print(f"\nFinished books: {len(finished_books)}, finished movies: {len(finished_movies)}")


# 1. Which fields are filled in, among finished items only?
def count_filled(records):
    counts = {}
    for record in records:
        for key, value in record.items():
            counts[key] = counts.get(key, 0)
            if value not in ["", [], None]:
                counts[key] += 1
    return counts


print("Finished books, filled fields:", count_filled(finished_books))
print("Finished movies, filled fields:", count_filled(finished_movies))

print("Finished books without a title:")
for book in finished_books:
    if not book.get("title"):
        print(
            book.get("subjectId"),
            book.get("isbn"),
            book.get("authors"),
            f"https://book.douban.com/subject/{book.get('subjectId')}",
        )

# 2. What does `info` start with? The year is needed for TMDB search.
#    - full date:    "1996-08-02(美国) / ..."
#    - partial date: "2001(中国大陆) / ..." or "2004-09(柏林电影节) / ..."
#    - no date:      starts with a name or a country
FULL_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
PARTIAL_DATE = re.compile(r"\d{4}(-\d{2})?(?!-)")

info_groups = {"full date": [], "partial date": [], "no date": []}
for movie in finished_movies:
    info = movie.get("info") or ""
    if FULL_DATE.match(info):
        info_groups["full date"].append(movie)
    elif PARTIAL_DATE.match(info):
        info_groups["partial date"].append(movie)
    else:
        info_groups["no date"].append(movie)

for group, group_movies in info_groups.items():
    print(f"\n`info` starts with {group}: {len(group_movies)}")
    for movie in group_movies[:5]:
        print(" ", movie.get("title"), "|", (movie.get("info") or "")[:50])

# 3. The movie `cover` field: is it ever filled in?
movies_with_cover = [movie for movie in movies if movie.get("cover")]
print(f"\nMovies with a `cover`: {len(movies_with_cover)} of {len(movies)}")
