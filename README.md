# MovieKernel

A Django-powered movie blog combining data-driven articles with a suite of custom
browser games and quizzes, built around a hand-designed cream-and-maroon visual
identity.

---

## Overview

MovieKernel pairs a Markdown-authored blog about film, data, and box office trends
with four purpose-built trivia games — **Tenable**, **Bingo**, **Higher or Lower**,
and **Networks** and plus a separate **Quizzes** section. All of it is content-managed
entirely through Django's admin: articles, puzzles, and quizzes are written,
scheduled, and published without touching code.

---

## Features

- **Blog** — Markdown articles with drag-and-drop inline image uploads, tags, hero
  images, and a featured-post homepage.
- **Four games:**
  - **Tenable** — guess-the-title trivia with limited lives and autocomplete input.
  - **Bingo** — image-based guessing board.
  - **Higher or Lower** — head-to-head battles comparing film/actor stats.
  - **Networks** — a Connections-style puzzle: pick one linked tile from each of
    five columns to trace a valid path.
- **Scheduled releases** — Tenable questions and Networks boards each carry a
  release date, so puzzles can be written well in advance and go live
  automatically, with future-dated puzzles staying hidden until then.
- **Self-building autocomplete** — every correct Tenable/Networks answer is added
  to a shared title-matching list, keeping player input consistent with what each
  puzzle expects.
- **Quizzes** — a separate content type supporting two formats: scored
  multiple-choice, and click-to-reveal.
- **Custom visual identity** — a consistent cream-and-maroon theme across the blog
  and most games. Higher or Lower deliberately keeps its own dark, cinematic
  full-bleed look, fitting its head-to-head battle format.

---

## Tech stack

- **Python / Django** (5.2)
- **SQLite**
- **Markdown authoring** via `markdownx`, with support for pasting self-contained
  interactive Plotly/Altair chart exports directly into article bodies
- **Vanilla CSS/JS** for the game front-ends

---

## Project structure

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
├── data/                   ← seed data (e.g. movie_titles.csv)
├── media/                  ← uploaded images
├── blog/                   ← articles (the homepage)
├── tenable/                ← game
├── bingo/                  ← game
├── higherorlower/          ← game
└── networks/                ← game
```

**Routes:** `/` blog feed · `/article/<slug>/` an article · `/about/` ·
`/tenable/` · `/bingo/` · `/higherorlower/` · `/networks/` · `/admin/`.
The four games are reached from the **Games** dropdown in the top navigation.

---

## Running it locally

**1. Clone and enter the project**
```bash
git clone <repo-url>
cd moviekernel
```

**2. Create a virtual environment**
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Apply migrations**
```bash
python manage.py migrate
```

**5. Create an admin account**
```bash
python manage.py createsuperuser
```

**6. (Optional) Seed the Tenable autocomplete list**

With `data/movie_titles.csv` in place:
```bash
python manage.py import_movie_titles data/movie_titles.csv
```

**7. Run the server**
```bash
python manage.py runserver
```
Open <http://127.0.0.1:8000/> for the blog homepage, or
<http://127.0.0.1:8000/admin/> for the admin.

**8. Add a first article**

In the admin, open **Articles → Add article**: set a title, tag (e.g. "Box
office"), hero image, and a Markdown body — images can be dragged directly into
the body field to upload. Tick **Is published** and save.

---

## Content authoring

### Articles (Markdown)

```markdown
## A section heading

A paragraph with **bold**, *italics*, and a [link](https://example.com).

> A pull quote.

| Year | Films |
|------|-------|
| 2010 |   12  |
```

Raw HTML is passed through untouched, which is how interactive Plotly/Altair
chart exports get embedded directly in a post body.

### Puzzles (Tenable & Networks)

- Each Tenable question and Networks board has a **release date** — set it to
  today to publish immediately, or a future date to schedule it. The `/tenable/`
  and `/networks/` links always redirect to the most recently released puzzle;
  future-dated ones return a 404 until their date arrives.
- Tenable questions support an optional description field, shown beneath the
  question — useful for bonus rules or an "as of &lt;date&gt;" note.
- Saved answers automatically feed the autocomplete list. To backfill answers
  added before this existed:
  ```bash
  python manage.py sync_movie_titles
  ```
- To bulk-import a titles CSV (reads a **Title** column, skips duplicates,
  handles commas/encoding quirks):
  ```bash
  python manage.py import_title_csv path/to/your_titles.csv
  ```
  Pass `--column "Name"` if the title column has a different header.

### Quizzes

Each quiz is one of two types, set on the quiz itself:

- **Multiple choice** — the reader clicks an option; correct turns green, wrong
  turns red (with the correct answer also revealed). A live score tracks
  progress.
- **Click to reveal** — each question has a *Reveal answer* button; no scoring.

**Adding a quiz:** Admin → **Quizzes → Add** — set a title, optional
tag/headline/hero image, choose the type, and tick **Is published**. Questions
are added on the same page, each with its own text, optional image, and an
*order* number. Multiple-choice questions take their **Options** one per line
plus a **Correct option** line number; click-to-reveal questions use the
**Reveal answer** field instead.

Quizzes are ordered newest-first and stay hidden until **Is published** is
ticked, matching how articles behave.

---

## Deployment checklist

Before deploying: set `DEBUG = False`, generate a fresh `SECRET_KEY`, populate
`ALLOWED_HOSTS`, run `python manage.py collectstatic`, and move `media/` to
persistent/cloud storage if the hosting environment's filesystem isn't durable.
