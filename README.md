# MovieKernel

A Django site for movie data-analysis articles, with a games section
(Tenable, Bingo, Higher or Lower, Networks). This is a complete, self-contained project —
the three games are already included. The only thing you bring over from your old
`screentrivia` project is your **data** (the database and uploaded images).

> Verified: this project boots on Django 5.2, `manage.py check` passes with no
> issues, all migrations apply, and every page renders.

---

## What's inside

```
moviekernel/
├── manage.py
├── requirements.txt
├── moviekernel/            ← project settings package
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── templates/base.html     ← cream-and-maroon site chrome
├── static/css/base.css     ← global theme
├── data/                   ← put movie_titles.csv here
├── media/                  ← uploaded images live here
├── blog/                   ← NEW: articles (the homepage)
├── tenable/                ← game
├── bingo/                  ← game
├── higherorlower/          ← game
└── networks/               ← game
```

Pages: `/` blog feed · `/article/<slug>/` an article · `/about/` ·
`/tenable/<id>/` · `/bingo/` · `/higherorlower/` · `/networks/<id>/` · `/admin/`.
The four games are reached from the **Games dropdown** in the top navigation.

---

## Setup — step by step

### 1. Put the project where you want it
Unzip the `moviekernel` folder somewhere and open a terminal **inside it** (the
folder containing `manage.py`).

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Bring your data over — pick ONE path

**Path A — keep your existing data (recommended).**
From your old `screentrivia` project folder, copy these two things into this
project's top folder:

- `db.sqlite3`  → into `moviekernel/db.sqlite3`
- the whole `media/` folder → into `moviekernel/media/`

This works because the game apps (tenable, bingo, higherorlower) are byte-identical
to your originals, so their database tables match exactly. Your existing Tenable
questions, Bingo placeholders, Higher-or-Lower actors, photos, and your admin login
all come across — including your Networks boards. (Leftover Buckets/Triples tables
and the old games-hub table are simply ignored.)

Optionally also copy `data/movie_titles.csv` over (used to re-seed the Tenable
autocomplete list if you ever need to).

**Path B — start completely fresh.**
Don't copy anything. You'll add your games' content through the admin afterwards.

### 5. Apply migrations
```bash
python manage.py migrate
```
- Path A: this just adds the new `blog_article` table to your copied database.
- Path B: this builds every table from scratch.

### 6. Admin login
- Path A: your existing superuser still works — skip this.
- Path B: create one:
  ```bash
  python manage.py createsuperuser
  ```

### 7. (Path B only, optional) Seed Tenable's movie list
With `data/movie_titles.csv` in place:
```bash
python manage.py import_movie_titles data/movie_titles.csv
```

### 8. Run it
```bash
python manage.py runserver
```
Open <http://127.0.0.1:8000/> — your blog homepage.
Admin is at <http://127.0.0.1:8000/admin/>.

### 9. Add your first article
- In the admin, open **Articles → Add article**: give it a title, a tag (e.g.
  "Box office"), a hero image, and a Markdown body — **drag an image straight into
  the body box** to upload it. Tick **Is published**, save, then reload `/`.

The four games are reachable from the **Games dropdown** in the navbar.

- (Path A, recommended) Run `python manage.py sync_movie_titles` once so every existing
  Tenable answer is in the autocomplete list — this fixes older title-matching misses.

---

## Writing articles in Markdown

```markdown
## A section heading

A paragraph with **bold**, *italics*, and a [link](https://example.com).

> A pull quote.

| Year | Films |
|------|-------|
| 2010 |   12  |
```

For an **interactive** chart later, export it from Plotly/Altair as a
self-contained HTML snippet and paste that HTML directly into the body — Markdown
passes raw HTML through untouched.

---

## Authoring & scheduling puzzles (Tenable & Networks)

- **Schedule by date.** Tenable questions and Networks boards each have a **release
  date**. Leave it as today to publish immediately, or set a future date to pre-write
  a puzzle that appears automatically on that day.
- **The Games dropdown opens the newest released one.** The Tenable and Networks links
  go to `/tenable/` and `/networks/`, which redirect to the latest released puzzle.
  Future-dated puzzles stay hidden (they 404) until their date arrives.
- **Per-puzzle description.** Each Tenable has an optional description shown under the
  question — good for bonus rules or an "as of <date>" note.
- **Answers feed the autocomplete automatically.** Every correct answer you save is
  added to the movie-title autocomplete list with its exact text, so suggested titles
  always match. To backfill answers added before this change (this fixes the
  "title doesn't match" bug), run once:

  ```
  python manage.py sync_movie_titles
  ```

- **Bulk-import a titles CSV.** To load a CSV of titles (e.g. a `MovieID,Title`
  export) into the autocomplete list:

  ```
  python manage.py import_title_csv path/to/your_titles.csv
  ```

  It reads the **Title** column (ignoring the id and the header row), copes with
  commas inside titles and odd encodings, and skips duplicates. If your title column
  has a different header, pass `--column "Name"`.

---

## Quizzes

There's a **Quizzes** tab in the navbar with its own homepage that looks just like
the blog feed — a featured quiz on top, preview cards below, each clicking through to
the quiz. You add quizzes in the admin under **Quizzes**.

Each quiz is **one type**, chosen on the quiz itself:

- **Multiple choice** — the reader clicks an option; the right one turns green, a wrong
  pick turns red (and the correct one is also shown). A live score sits at the top.
- **Click to reveal** — each question has a *Reveal answer* button that drops the answer
  in beneath it. No scoring.

**Adding a quiz:**

1. Admin → **Quizzes → Add**. Set the title, an optional tag/headline/hero image (these
   show on the preview card), pick the **type**, and tick **Is published** when ready.
2. Add **questions** right there on the same page — each has the question text and an
   optional image. Set the *order* number to control their sequence.
3. **For a multiple-choice question**, fill in two fields on that same question:
   - **Options** — type the answer choices, **one per line**.
   - **Correct option** — the line number of the right answer (1 = first line, 2 = second…).
4. **For a click-to-reveal question**, leave Options blank and fill in the **Reveal answer**
   box instead.

Everything for a question — including its multiple-choice options — is on the one quiz
page. There's no separate step.

Quizzes are ordered newest-first and hidden until **Is published** is ticked, exactly
like blog articles.

---

## What's branded vs. still to do

**On-brand (cream & maroon):** the blog homepage (with your logo masthead), article
pages, About, the top navigation (your logo replaces the popcorn glyph), and the
Tenable, Bingo, and Networks games.

**Higher or Lower** keeps its own dark, full-bleed playing area by design (the split
red/black actor panels). If you'd like that one matched to cream-and-maroon too, that's
a quick follow-up.

---

## Deploying later (not needed now)
Before going live you'll want to: set `DEBUG = False`, generate a new `SECRET_KEY`,
fill in `ALLOWED_HOSTS`, run `python manage.py collectstatic`, and move `media/` to
cloud storage. None of that is required to run locally.
