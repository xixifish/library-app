# Library App

Turns my Douban history into data for the Library page on my personal website: every
book I've finished reading and every film and TV season I've finished watching.

## What it does

- Reads my Douban exports (about 470 finished books and 1,760 finished films and TV
  seasons).
- Keeps finished items only and sorts them into three categories: **book** (manga
  included), **film** and **TV**.
- Looks up film and TV posters on [TMDB](https://www.themoviedb.org/). That match also
  tells film from TV. Without a match, a title with "第X季" counts as TV.
- Writes one JSON file per category, for the website to show newest first.

Book titles and authors come from Douban; covers are looked up by ISBN on Google Books. Books without a cover are left
out for now.

## Status

- [x] Requirements: [`docs/requirements.md`](docs/requirements.md)
- [x] Step 1: explore the data (`scripts/explore.py`)
- [x] Step 2: test TMDB matching on about 20 titles (`scripts/test_matching.py`)
- [x] Build the film and TV JSON files (`scripts/build.py`)
- [x] Test a book cover source ([`docs/book-api-test.md`](docs/book-api-test.md))
- [ ] Build the book JSON file
- [ ] Show all three on the website

Later: a tool to record new books, films and TV here, which then updates the website.

## Layout

```
docs/       requirements and decisions
scripts/    Python scripts
raw/        my Douban exports (not in the repo, see below)
```

## Running

The scripts use Python 3 and only its standard library.

```sh
python3 scripts/explore.py
```

They read `raw/books.json` and `raw/movies.json`. These are my own exports and contain
personal comments, so `raw/` is gitignored and not published. To run the scripts on your
own data, put exports with the same shape there.

TMDB needs an API key. Put it in a `.env` file (gitignored), never in the code.

## Credits

This project uses TMDB and the TMDB APIs but is not endorsed, certified, or otherwise
approved by TMDB.

TMDB data is used under its [terms of use](https://www.themoviedb.org/api-terms-of-use):
non-commercial only, and refreshed at least every 6 months.

## License

[MIT](LICENSE)
