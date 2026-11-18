import json

with open("raw/books.json", encoding="utf-8") as f:
    books = json.load(f)

print(json.dumps(books[0], indent=2, ensure_ascii=False))

with open("raw/movies.json", encoding="utf-8") as f:
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
from collections import Counter

print(Counter(book.get("status") for book in books))
print(Counter(movie.get("status") for movie in movies))

# Check `markedAt`
# 1. What are the earliest and latest dates?
# 2. Which records are missing one?
from datetime import datetime

# Books
book_markedAts = []
for book in books:
    new_book_dict = {
        "subjectId": book.get("subjectId"),
        "title": book.get("title"),
    }
    marked_at = book.get("markedAt")
    if marked_at == "":
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
