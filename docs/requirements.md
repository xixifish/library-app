# Requirements: Douban Library

Last updated: 2026-11-18 · Kickoff: short

## Core need

Show everything I've finished reading and watching, taken from my Douban export,
on my website's Library page, grouped into book, manga, film and TV.

- **Problem:** my Douban history (~2,200 finished items) lives only on Douban. The
  website's Library shows 7 items I enter by hand.
- **For:** visitors to my personal website (recruiters, people curious about me), and me.
- **Today I:** enter Library items by hand in `data/library.ts`, with covers saved by hand.
- **A good result looks like:** someone opens the Library page, picks "Film", and sees
  every film I've watched, newest first, with covers where available.

## Rules from TMDB's terms

Read on 2026-11-18. My reading, not legal advice.

- Credit TMDB with one of its approved logos and this notice, in an About or Credits
  area: "This website uses TMDB and the TMDB APIs but is not endorsed, certified, or
  otherwise approved by TMDB." The logo must be less prominent than my own name or logo.
  Source: https://www.themoviedb.org/api-terms-of-use §3, logos at
  https://www.themoviedb.org/about/logos-attribution
- Don't keep anything obtained from TMDB longer than 6 months. This is a permission
  rule, not a technical one: saved poster addresses keep working, but TMDB data should be
  fetched again at least every 6 months. A refresh also picks up replaced or corrected
  posters. Source: api-terms-of-use §1.C
- Free for non-commercial use only. Ads or other income on the site would make it
  commercial and need a written agreement. Source:
  https://developer.themoviedb.org/docs/faq, api-terms-of-use §2.A
- Rate limit is around 40 requests per second; back off on a `429` response. Source:
  https://developer.themoviedb.org/docs/rate-limiting

## Data

| Data | Source | Access | Allowed to use? | Checked with a real sample? |
|------|--------|--------|-----------------|-----------------------------|
| Films and TV I've marked | Douban export (纳豆), `raw/movies.json` | One-time export, already done | My own data | Yes: 1,878 records (1,762 watched, 95 want, 21 watching). Stars on 1,749, comments on 1,028, marked dates 2011–2026 (2 missing). Original title on 1,615. No covers, no film/TV type, no IMDb/TMDB id. Cast, year, country etc. in one `info` text. About 349 titles contain "第X季". |
| Books I've marked | Douban list + detail pages, merged into `raw/books.json` (by `merge_books.py`, kept outside the repo) | One-time export, already done | My own data | Yes: 807 records (472 read, 331 want, 4 reading). ISBN on 806, stars on 467, comments on 317. Authors, publisher, date, pages, series as separate fields. Series on 419. No book/manga type. |
| Covers via Douban image links | Douban (`doubanCover` in the book data) | Refused when requested from another site (403) | n/a | Yes: one book cover link tested |
| Book covers by ISBN | Open Library | Public | Not checked | Yes: only 3 of 15 sampled read books had a cover (mostly Chinese/Taiwanese editions) |
| Film and TV posters | TMDB API, search by title + year | Free API key from TMDB account settings | Yes, non-commercial with attribution; no keeping data over 6 months (see rules above) | Not yet: docs read 2026-11-18, no live search without a key |
| Book and manga covers | Downloaded by me, by hand | Manual | My call | n/a |

**How fresh it needs to be:** my own records are frozen at the export date
(2026-11-12), with new items added by hand until a recording tool exists. No re-export
planned. TMDB data is refreshed at least every 6 months.

## Scope

- **In v1:**
  - Library page with four categories: book, manga, film, TV.
  - Every finished item (read/watched) listed under its category.
  - Type for each item: an automatic first guess, then I fix mistakes by hand. For
    films and TV, a TMDB match tells film from TV; otherwise "第X季" → TV. Every book
    starts as "book"; I mark manga by hand.
  - Each TV season is its own item (Douban lists seasons separately), not grouped
    under one show.
  - Output: one JSON file per category (book, manga, film, TV) with the most complete
    data for each item. It doesn't need to match the current `data/library.ts` shape.
  - Film and TV covers from TMDB, shown from TMDB's image server, not stored.
  - Book and manga covers added by hand over time, newest first.
  - A simple placeholder card for any item without a cover.
  - TMDB credit (logo + notice) on the site.
  - Ratings and comments: optional, may or may not show.
- **Out:** want-to-read/watch items, in-progress items, tags (only on 471 of 1,762
  watched films/TV, none on books; not useful for the site, left out of the output but
  still in the raw export).
- **Later:**
  - A tool to record new books, films and TV myself, in this same repo, that updates the website.

## Open questions

- [ ] How well does TMDB match my titles, especially Chinese ones? Test ~20 films and
  TV shows once I have a key.
- [ ] Confirm in TMDB's image docs that linking to their image server is the intended use.
- [ ] Does saving TMDB ids or poster addresses count as keeping data? If yes, how and
  how often to refresh (at least every 6 months).
- [ ] Show ratings and comments in v1, or not?
- [ ] Order inside each category: newest marked first?
- [ ] A category with ~1,500 films is a long page: fine for v1, or does it need paging
  or search?
- [ ] The 2 films with no marked date: where do they go?
- [ ] Where do my hand fixes (manga, film/TV corrections) live so that re-running the
  script, e.g. for the 6-month TMDB refresh, doesn't overwrite them? Suggestion: a
  separate fixes file keyed by Douban id that the script applies last.
- [ ] What is `library-app/` for?
