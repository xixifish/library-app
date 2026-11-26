# Book API test: Google Books

Hand test before any book code (see the open questions in `requirements.md`).
Started 2026-11-26.

**Questions:**

1. How many books does Google Books find, by ISBN and by title + author?
2. Are the covers real (not the grey "image not available" picture) and of the right edition?
3. Are title, authors and year correct and complete enough to show on the site?

**Requests:**

- By ISBN: `https://www.googleapis.com/books/v1/volumes?q=isbn:<ISBN>`
- By title + author: `https://www.googleapis.com/books/v1/volumes?q=intitle:<title>+inauthor:<author>`
  (URL-encode Chinese text)

**Legend:** ✅ yes · ❌ no · ⚠️ partly (explain in notes)

## The sample (Douban data, for comparing)

| # | subjectId | ISBN | Title | Authors | Publisher | Published | Kind |
|---|---|---|---|---|---|---|---|
| 1 | 30355759 | 9780735211292 | Atomic Habits | James Clear | Avery | 2018-10 | English |
| 2 | 35563599 | 9781098103965 | Python for Data Analysis, 3rd Edition | Wes McKinney | O'Reilly Media | 2022-9 | English, edition check |
| 3 | 27062726 | 9787516812969 | 贾想 I | 贾樟柯, 万佳欢 编 | 台海出版社 | 2017-6 | Mainland |
| 4 | 25870991 | 9787513903318 | 曾国藩的正面与侧面 | 张宏杰 | 民主与建设出版社 | 2014-4 | Mainland |
| 5 | 26830207 | 9787115427847 | 设计师要懂心理学2 | [美] Susan M.Weinschenk | 人民邮电出版社 | 2016-7 | Mainland translation |
| 6 | 1361873 | 9789574918034 | 一個女人兩張床 | 亦舒 | 林白 | 2001-9 | Taiwan novel |
| 7 | 3114540 | 9789571020112 | 浪人劍客(03) | 井上雄彥 | 尖端出版社 | 1999/12/10 | Taiwan manga |
| 8 | 26881891 | 9789865824662 | 深夜食堂 17 | 安倍夜郎 | 新經典文化 | 2016-10 | Taiwan manga |
| 9 | 10345414 | 9789882070370 | 浪客行 18 | 井上雄彥, 吉川英治, [日本] 井上雄彦 | 天下出版（國際）有限公司 | (none) | Hong Kong manga |
| 10 | 4828606 | 9783469351579 | 異獸魔都(14) | 林田球 | 長鴻 | 2010/07/15 | Taiwan manga, suspicious ISBN (978-3 = German) |

## Results

| # | Title | Found by ISBN | Title + author search used | Found by title + author | Real cover | Right edition | Title / authors / year OK | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | Atomic Habits | ✅ | `intitle:atomic habits inauthor:clear` | ⚠️ | ✅ (zoom=2 good size) | ✅ ISBN matches | ✅ | ISBN edition `XfFvDwAAQBAJ` not in the search's top 10; #1 was the Tamil edition, then workbook, other editions, summaries. Subtitle in its own field. Date 2018-10-16 (Douban 2018-10). Publisher Penguin vs Douban's Avery (a Penguin imprint; not shown anyway). |
| 2 | Python for Data Analysis 3e | ❌ | `intitle:"python for data analysis" inauthor:mckinney` | ✅ #1 (2022, ebook ISBN 9781098104009) | ✅ in search result | ⚠️ 3rd edition, ebook ISBN not print | ✅ | Print ISBN not in Google; search finds 3rd, 2nd and 1st editions, newest first. Google id `EgKBEAAAQBAJ`. |
| 3 | 贾想 I | ✅ | `intitle:贾想 inauthor:贾樟柯` | ✅ #2 of 3 | ❌ none | ✅ ISBN matches | ⚠️ | Title without "I", subtitle 贾樟柯电影手记 1996-2008, year 2017 only, no publisher. #1 is the 2009 edition (has a cover). |
| 4 | 曾国藩的正面与侧面 | ✅ | `intitle:曾国藩的正面与侧面 inauthor:张宏杰` | ✅ #2 of 5 | ❌ none | ✅ ISBN matches | ❌ | **Wrong author: 張敞** (Douban 张宏杰). Year 2014 only, no publisher. 5 editions, none with a cover. |
| 5 | 设计师要懂心理学2 | ✅ | `intitle:设计师要懂心理学 inauthor:Weinschenk` | ✅ #1 of 2 | ❌ none | ✅ ISBN matches | ⚠️ | **Title lacks the "2"**, so it reads as the first book (also listed, 2013). Author only as 魏因申克. No publisher. |
| 6 | 一個女人兩張床 | ✅ | `intitle:一個女人兩張床 inauthor:亦舒` | ✅ only result | ❌ none | ✅ ISBN matches | ⚠️ | Year 2000 (Douban 2001-9). Language says zh-CN for a Taiwan edition. No publisher. |
| 7 | 浪人劍客(03) | ✅ | `intitle:浪人劍客 inauthor:井上雄彥` | ✅ #1 of 2 | ❌ none | ✅ ISBN matches | ⚠️ | **No volume number** (title just 浪人劍客), so all volumes would look the same. Year 1998 (Douban 1999). Authors include 吉川英治 and two translators. |
| 8 | 深夜食堂 17 | ✅ | `intitle:深夜食堂 inauthor:安倍夜郎` | ❌ not in top 5 of 113 | ❌ none | ✅ ISBN matches | ⚠️ | **No volume number.** Search returns mainland and Japanese volumes; only the Japanese ones have covers. |
| 9 | 浪客行 18 | ❌ | `intitle:浪客行 inauthor:井上雄彥` | ❌ | ❌ | | | Hong Kong edition unknown to Google. Search finds only two art books (畫集). |
| 10 | 異獸魔都(14) | ❌ | `intitle:異獸魔都 inauthor:林田球` | ⚠️ other edition | ✅ for the other edition | ❌ | | Douban ISBN is wrong (978-3). Search finds the 2020 典藏版 (collector's edition) volumes, with covers and volume numbers, but not the 2010 edition. 24 results. |

## Round 2: more English books (ISBN only, 2026-11-26)

The first sample had only 2 English books, so 8 harder ones were added: picture books, a box
set, an old Scholastic edition, local publishers, an anthology. Covers were downloaded and
looked at (in `../work/cover-test/`, outside the repo).

| subjectId | ISBN | Title | Found by ISBN | Cover zoom=1 | Cover zoom=2 | Title / authors / year OK | Notes |
|---|---|---|---|---|---|---|---|
| 4295403 | 9780007365388 | The Tiger Who Came to Tea | ❌ | | | | Title search finds 17 results: audiobook, activity book, lift-the-flap... Exact title is #3 (another edition). |
| 4281716 | 9781877467141 | Duck, Death and the Tulip | ✅ | ✅ | ✅ 300 px | ✅ | Publisher "Gecko Press TM". |
| 32706849 | 9781338267228 | The Bad Guys Box Set | ✅ | ✅ 128 px | ❌ placeholder | ⚠️ | Title "The Bad Guys Box Set:" (trailing colon), publisher "Bad Guys". Douban has no author; Google gives Aaron Blabey. |
| 1344161 | 9780439139601 | Harry Potter and the Goblet of Fire | ❌ | | | | Title search: exact title is #1 but a 2019 edition; #2 is a teaching guide. |
| 30242583 | 9780143771876 | Bobby, the Littlest War Hero | ✅ | ✅ 128 px | ❌ placeholder | ⚠️ | Only first author (Glyn Harper; Douban also Jenny Cooper). |
| 11578037 | 9781742200170 | Lonely Planet New Zealand | ✅ | ✅ 128 px | ❌ placeholder | ⚠️ | Title just "New Zealand", year 2012, no publisher. |
| 38207789 | 9781761170508 | the best australian science writing 2025 | ✅ | ✅ 128 px | ❌ placeholder | ✅ | Gives editors as authors (Douban has none). |
| 3260224 | 9780141035819 | Design as Art | ✅ (2 results) | ✅ 128 px | ❌ placeholder | ⚠️ | Result #1 publisher "National Geographic Books" (wrong), 2019; #2 ePenguin 2008. |

**Round 2 result:** 6 of 8 found by ISBN. All 6 have a real cover at `zoom=1` (128 px wide),
but only 1 at `zoom=2`; the other 5 return the "image not available" picture at `zoom=2` and
`zoom=0`. Atomic Habits and Duck, Death and the Tulip are the exceptions with large covers.

## Round 3: Open Library on the same books (2026-11-26)

Cover by ISBN: `https://covers.openlibrary.org/b/isbn/<ISBN>-L.jpg?default=false` (no key;
`default=false` returns 404 instead of a blank image when there's no cover). Book data:
`https://openlibrary.org/api/books?bibkeys=ISBN:<ISBN>&format=json&jscmd=data`.
Covers were looked at (in `../work/ol-test/`, outside the repo).

| Book | Google: found / cover | Open Library: found / large cover | Best cover |
|---|---|---|---|
| Atomic Habits | ✅ / large | ✅ / ✅ 331×500 | either |
| Python for Data Analysis 3e | ❌ (title search ✅, cover) | ❌ / ❌ | Google via title search |
| The Tiger Who Came to Tea | ❌ | ❌ / ❌ | none |
| Duck, Death and the Tulip | ✅ / large | ✅ / ❌ | Google |
| The Bad Guys Box Set | ✅ / small | ✅ / ✅ 500×490 | Open Library |
| Harry Potter and the Goblet of Fire | ❌ | ✅ / ✅ 330×500, the Scholastic edition | Open Library |
| Bobby, the Littlest War Hero | ✅ / small | ✅ / ❌ | Google small |
| Lonely Planet New Zealand | ✅ / small | ✅ / ✅ 322×500 | Open Library |
| Best Australian Science Writing 2025 | ✅ / small | ✅ / ❌ | Google small |
| Design as Art | ✅ / small | ✅ / ⚠️ 179×293 | Open Library (medium) |
| 6 Chinese books (贾想 ... 深夜食堂) | 6 found / 0 covers | 2 found / 0 covers | none |

**Round 3 result:** for the 10 English books, Google alone gives a large cover for 2;
Open Library alone for 5 (one medium); **both together for 6–7, plus a small Google cover
for 2 more**. Only The Tiger Who Came to Tea has no cover anywhere by ISBN. Open Library's
data is about as good as Google's for English (also "New Zealand" without "Lonely Planet";
Atomic Habits has no author and the wrong year). For Chinese books it is no help: no covers,
titles in pinyin ("Jia xiang", "Shen ye shi tang").

## Learned so far

- **An API key is required.** Without one, requests count against a shared anonymous
  project whose daily limit is 0 (error 429 `RESOURCE_EXHAUSTED`, `quota_limit_value: "0"`).
  Key created 2026-11-26 in Google Cloud project `library-app`, restricted to the Books API,
  no application restriction (scripts run from a laptop). Stored in `.env` as
  `GOOGLE_BOOKS_API_KEY`; add `&key=...` to requests. Never paste or commit it.
- **Fields that matter** (in `items[0].volumeInfo`): `title`, `subtitle` (separate, so the
  site can show the title alone), `authors`, `publishedDate`, `industryIdentifiers`
  (ISBN-10/13, to confirm the edition), `imageLinks.thumbnail`, `language`. Plus
  `items[0].id`, Google's id for the book, like the TMDB id for films; keep it in book records.
- **Cover links** start with `http://`; the site is https, so the fetch step will probably
  switch them to `https://`. `zoom=1` is a small image (~128 px wide), too small for a card.
  Changing the link's `zoom` works: `zoom=2` is larger and looks good enough for a card;
  `zoom=0` is very large (Atomic Habits, 2026-11-26). **But most books only have the small
  one**: in round 2, 5 of 6 covers were the "image not available" picture at `zoom=2` and
  `zoom=0`, while `zoom=1` was real. The JSON doesn't say which sizes exist. The placeholder
  is always the same image (300×391 at zoom=2, 575×750 at zoom=0), so a script could spot it.
- Everything else (`description`, `saleInfo`, `accessInfo`, `readingModes`, ...) is not needed.
- **Search lists editions, not books**: translations, ebooks, reprints, workbooks and
  summaries each have their own entry. Result #1 is often not the one you want, and the
  order changed between two identical requests a few minutes apart. The marking tool
  must show a list to pick from. (`langRestrict=en` not tried yet.)
- **Chinese-language books: found, but no covers.** All 6 mainland/Taiwan books with a
  valid ISBN were found, and none had a cover. Their data is thin: no publisher, year
  only, volume numbers missing (浪人劍客, 深夜食堂, 设计师要懂心理学 without "2"), one
  wrong author (曾国藩的正面与侧面 → 張敞).

## Summary

No single API has good data and covers for all my books:

- **Google Books** finds most English books by ISBN (8 of 12) and by title, but most covers
  are only 128 px; its search lists every edition in an unstable order. It finds mainland
  and Taiwan books but with no covers and thin or wrong data (no volume numbers, one
  wrong author). Needs an API key.
- **Open Library** has large covers for about half the English books (5 of 10), including
  ones Google can't find; nothing useful for Chinese books.
- **Together** they give a cover for 9 of 10 English books (6–7 large).

**Decisions (2026-11-26, recorded in `requirements.md`):** imported books use Douban's
title/authors/year; covers from Google Books only (Open Library maybe later); books without
a cover are not shown in v1. In the marking tool, books are my own records and API search
only pre-fills the form.
