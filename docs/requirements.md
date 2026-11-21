# Requirements: Douban Library

Last updated: 2026-11-20 · Kickoff: short

## Core need

Show everything I've finished reading and watching, taken from my Douban export,
on my website's Library page, grouped into book, film and TV.

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
| Film and TV posters | TMDB API, `/search/multi` by original title or title (see TMDB matching) | Free API key from TMDB account settings, sent as `Authorization: Bearer <Read Access Token>` | Yes, non-commercial with attribution; no keeping data over 6 months (see rules above) | Yes: 7 titles searched by hand on 2026-11-20, 6 matched by the rule, 1 needs a person |
| Book covers (manga included) | Downloaded by me, by hand | Manual | My call | n/a |

## TMDB matching

Decided 2026-11-20, after testing 7 titles by hand with curl, then 21 titles with
`scripts/test_matching.py` (results below).

- **Query:** `originalTitle` if present, else `title`.
  - A trailing `...` is removed: the export cut 48 finished items' `originalTitle`
    short (e.g. `Doctor Strange in the Multiverse of ...`).
  - TV season: the season number comes from "第X季" in Douban's `title` (all 321
    season items have it, Chinese numerals). Its text is removed from the query:
    "第X季" from `title`; "Season 6", "2nd Season", "シーズン1", "시즌 3" from
    `originalTitle`. Other forms (`더 글로리2`, `第2期`, `肆`) are searched as they are.
  - **Fallback** (decided 2026-11-20): if the search returns no results, search again
    with Douban's Chinese `title` (season part removed). The year and season checks
    still apply. The record notes that the fallback query was used.
- **Endpoint:** with `language=zh-CN` (it only sets the language of the results,
  not what is matched). Only the first page of results (20) is read.
  - Items with a season in the title: `/search/tv`, since they must be TV.
    Searching films too would let them push the right show off the first page.
    `/search/tv` results have no `media_type`; the script sets it to `tv`.
    (Decided 2026-11-20.)
  - All other items: `/search/multi`. It returns films and TV together, each with a
    `media_type`, so the match decides film or TV. Skip `person` results.
  - Films use `title` / `release_date`, TV uses `name` / `first_air_date`.
- **Accept:** among the results whose year is within 1 of the year in Douban's `info`,
  the best one, in this order: (1) its (`zh-CN`) title is exactly Douban's Chinese
  `title`; (2) the smaller year difference; (3) TMDB's order. A 1-year gap is normal:
  黑炮事件 is 1986 on Douban and 1985 on TMDB. The year tiebreak (2026-11-21) fixed 6
  matches where a same-year film lost to a TV version or sequel a year off
  (当男人恋爱时, 隧道, 画皮2, 勇敢者的游戏, 海贼王剧场版9, 反叛的童谣).
  The title preference was added 2026-11-21 after the full run: ~170 matches weren't
  TMDB's first result, and ~12 of them were wrong, usually a TV show that only
  contains the title (变形金刚 → *Transformers: Animated*, 布鲁克林 → *Taxi Brooklyn*)
  or a film whose Chinese title differs (暖 → *Eternal Sunshine*, 暖暖内含光). Tested
  offline on the saved candidates: 23 matches change, ~18 clearly for the better.
  Titles are compared after Unicode NFKC normalization and without spaces, since
  Douban writes `哈利·波特与死亡圣器(上)` and TMDB `（上）` (found in the spot check;
  changes only that one match, to Part 1). Not used for TV seasons, which already
  have the season check.
- **TV seasons:** after finding the show, get `/tv/{id}` and check the season's own
  `air_date` against Douban's date, not the show's `first_air_date`. Seasons have
  their own `poster_path`. The `seasons` list in `/tv/{id}` has each season's
  `season_number`, `air_date` and `poster_path`, so this one request serves both the
  check and the details; `/tv/{id}/season/{n}` isn't needed. With several TV
  candidates, check them in order until one passes.
- **Manual list** (a person picks the match, nothing is guessed):
  - no result from TMDB, with the fallback search too;
  - no result within 1 year of Douban's year;
  - no date in Douban's `info` (15 finished items), so no year to check;
  - a TV season whose season number isn't in the show's `seasons` list on TMDB
    (e.g. TMDB counts 物理魔法使马修 第二季 as part of season 1).

  A missing `originalTitle` alone is not a reason: ~243 of the 253 finished items
  without one are Chinese-language, and their `title` is the original title.
- **Shown in the original language** (decided 2026-11-20):
  - Title: TMDB's `original_title` (film) or `original_name` (TV) for matched items.
    Changed 2026-11-20 from Douban's titles: TMDB's are cleaner, and the future
    marking tool will use TMDB, not Douban. Items without a TMDB match fall back to
    Douban's `originalTitle`, else `title`. For a TV season the title is built from the
    show's name and the season number (format still open). TMDB titles count as
    stored TMDB data, so the 6-month rule applies to them.
  - Poster: after matching, request the details (`/movie/{id}` or `/tv/{id}`) with
    `language=<original_language>` from the match, and use that `poster_path`.
    Checked on 直到T恤干透 (322570): `ja` and `zh-CN` give different posters.
- **Titles in other languages** (decided 2026-11-21): the records also keep TMDB's
  English (`title_en`, en-US) and Simplified Chinese (`title_zh`, zh-CN) titles, from
  `append_to_response=translations` on the details request (no extra request). Not
  shown in v1; kept for a possible language switch on the site later. TMDB often has
  no zh-CN title for foreign items (*Slow Horses* has only zh-TW / zh-HK), so for
  items from Douban the Chinese title can come from Douban's `title` instead.
- **Not needed:** full-width characters (`Ｔ`) match the same as normal ones; running
  time from `info` isn't used unless ties between a film and a show turn up.

| Douban title | Query | Result |
|---|---|---|
| 玛蒂尔达 | 玛蒂尔达 / Matilda | ✓ same film (10830) with both |
| 流人 第六季 | 流人 / Slow Horses | ✗ right show only #18 / ✓ only result (95480); season 6 `air_date` matches Douban exactly |
| 铁拳教育 | 참교육 / 铁拳教育 | ✓ tv (276161) with both; 3 films in results fail the year check |
| 直到T恤干透 | Ｔシャツが乾くまで | ✓ tv (322570), full-width and normal `T` same result |
| 黑炮事件 | 黑炮事件 (no original title) | ✓ film (176643), 1985 vs 1986; a 2019 video essay ruled out by year |
| 哀乐中年 | 哀樂中年 (original title, traditional characters) | ✓ film (176628), 1949 |
| 杨门女将 | 杨门女将 (no date) | ? three exact-name results (2001 tv, 1981 tv, 1960 film); needs a person |

**Script test, 2026-11-20** (`scripts/test_matching.py`, steps 1–3 of the fetch script,
before the `...` and fallback rules). The 7 titles above gave the same results. Of all
21: 13 matched, all correct by eye (no wrong match); 8 manual.

| Douban title | Case | Result |
|---|---|---|
| 奇异博士2：疯狂多元宇宙 | cut-off English title | ✓ film (453395), found despite the `...` |
| 现在不是出轨的问题 | cut-off Korean title | ✗ no results → ✓ tv (301418) once the `...` is removed |
| 美国恐怖故事 第一季 | cut-off title + season | ✗ no results → ✓ tv (1413), season 1, via the fallback `美国恐怖故事` |
| 黑暗荣耀 第二季 | `더 글로리2` | ✗ no results → fallback finds the show (136283), but TMDB has one 16-episode season for both parts: manual |
| 一拳超人 第二季 | `ワンパンマン 第2期` | ✗ no results → ✓ tv (63926), season 2 aired 2019-04-10, via the fallback `一拳超人` |
| 夏目友人帐 第四季 | `夏目友人帳 肆` | ✓ tv (69500), season 4 aired 2012-01-03 (Douban 01-02) |
| 物理魔法使马修 第二季 | season subtitle in the title | manual: show found (204832), but TMDB has only season 1 |
| 动物狂想曲 第一季 | `BEASTARS`, no season marker | ✓ tv (90937), season 1 |
| 鱿鱼游戏 第一季 | `오징어 게임`, no season marker | ✓ tv (93405), season 1 |
| 吐槽大会 第五季 | season, no original title | ✓ tv (84698), season 5 aired on Douban's date |
| 西游记 | no date (`Journey to the West`) | manual, as expected (20 results) |
| 西游记 | common title, 1986 | ✓ tv (13923); the year picks it from 20 versions |
| 杨门女将之女将初征 | no date, two same-name results | manual, as expected |
| 杨门女将之情定穆柯寨 | year only (2001) | ✓ film (1088882) |

The 4 "no results" items led to the `...` and fallback rules. Rerun with both rules
(same day): 16 matched, all correct; 5 manual (3 without a date, 2 where TMDB numbers
the seasons differently: 物理魔法使马修, 黑暗荣耀).

**How fresh it needs to be:** my own records are frozen at the export date
(2026-11-12), with new items added by hand until a recording tool exists. No re-export
planned. TMDB data is refreshed at least every 6 months.

## Scope

- **In v1:**
  - Library page with three categories: book, film, TV. Manga are shown under book
    (decided 2026-11-19), so books need no type.
  - Every finished item (read/watched) listed under its category.
  - Film or TV for each film/TV item: an automatic first guess, then I fix mistakes by
    hand. A TMDB match tells film from TV; otherwise "第X季" → TV.
  - Film/TV items that TMDB can't match safely go on a manual list for me to check,
    instead of getting a guessed poster (rules in TMDB matching).
  - Each TV season is its own item (Douban lists seasons separately), not grouped
    under one show.
  - Output: one JSON file per category (book, film, TV) with the most complete
    data for each item. It doesn't need to match the current `data/library.ts` shape.
  - Film and TV covers from TMDB, shown from TMDB's image server, not stored.
  - Book covers (manga included) added by hand over time, newest first.
  - A simple placeholder card for any item without a cover. Unmatched film/TV
    items are shown this way, with their Douban title, until I fix or hide them.
  - My own decisions go in `data/fixes.json`, keyed by Douban `subjectId`: a TMDB
    match (`id`, `media_type`, `season`), and/or `"hidden": true` to leave an item
    off the site. An entry with only `hidden` means checked and not on TMDB. No
    `hidden` field means shown. (Decided 2026-11-20.)
  - TMDB credit (logo + notice) on the site.
  - Each matched film/TV card links to its TMDB page, built from the saved
    `media_type`, `id` and season (e.g. `themoviedb.org/movie/176643`,
    `themoviedb.org/tv/95480/season/6`); no URL is stored (decided 2026-11-20).
  - Ratings and comments: optional, may or may not show.
- **Out:** want-to-read/watch items, in-progress items, tags (only on 471 of 1,762
  watched films/TV and 147 of 472 read books; not useful for the site, left out of the output but
  still in the raw export).
- **Later:**
  - A tool to record new books, films and TV myself, in this same repo, that updates the website.

## Open questions

- [x] How well does TMDB match my titles, especially Chinese ones? Answered
  2026-11-20 by 7 hand searches and a 21-title script test (no wrong match); the rule
  is in TMDB matching. Still to watch when the script runs on everything: how long
  the manual list gets, and whether a wrong match slips through with the right year.
- [x] Posters in Chinese or in the original language? Original language, titles too
  (see TMDB matching).
- [x] Show Douban's Chinese title as a smaller second line under the original title?
  No: only the original title is shown (decided 2026-11-20).
- [ ] For a TV season: show the season's poster or the show's poster?
- [ ] Title format for a TV season: "Slow Horses Season 6", "Slow Horses · S6", or
  something else?
- [ ] Confirm in TMDB's image docs that linking to their image server is the intended use.
- [ ] Does saving TMDB ids or poster addresses count as keeping data? If yes, how and
  how often to refresh (at least every 6 months).
- [ ] Show ratings and comments in v1, or not?
- [ ] Order inside each category: newest marked first?
- [ ] A category with ~1,500 films is a long page: fine for v1, or does it need paging
  or search?
- [ ] The 2 films with no marked date: where do they go?
- [ ] Items without a TMDB match: link to their Douban page (`url` in the raw data),
  or no link?
- [ ] Where do my hand fixes (film/TV corrections, missing titles) live so that re-running the
  script, e.g. for the 6-month TMDB refresh, doesn't overwrite them? Suggestion: a
  separate fixes file keyed by Douban id that the script applies last.
- [ ] What is `library-app/` for?
