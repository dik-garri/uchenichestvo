# Bible Groups Course Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the third course on the `uchenichestvo` site — «Изучение Библии в малых группах» — covering 102 Bible-study topics (52 OT + 50 NT) with a three-tab topic view (Synodal text / questions in two editions / preparation media), plus searchable list pages.

**Architecture:** Static HTML/CSS/JS, no build step (consistent with existing `burnham/` and `7-shagov/` courses). Topics described in `bible-groups/topics.json`; questions are Markdown files rendered by marked.js; Synodal text rendered from the existing `data/synodal.json`. A one-off Python script extracts question content from the source PDFs into Markdown files.

**Tech Stack:** Plain HTML/CSS/vanilla JS, marked.js (CDN), Font Awesome (CDN), Montserrat + Lora (Google Fonts). One-off Python 3 with `pdfplumber` for extraction.

**Reference spec:** `docs/superpowers/specs/2026-05-13-bible-groups-course-design.md`

**Source materials (kept in repo, not served):**
- `groups/row_material/Вопросы_Ветхий_Завет_1-52.pdf`
- `groups/row_material/Вопросы_Новый_Завет_51-100.pdf`
- `groups/row_material/Изучение_Библии_в_малых_группах_для_лидеров.pdf`
- `groups/row_material/data example 43. Призвание Иеремии/` — example media

**Project notes:**
- No test framework exists in this project. Verification = manual checks + scripted assertions in the extraction code itself.
- Existing code uses Russian filenames in `burnham/` and `7-shagov/`. The new course uses **latin slugs** in filenames so URLs stay clean and media folders are CDN/Pages-safe.
- Use en dash `–` everywhere (`&ndash;` in HTML). Never em dash.

---

## File Structure

| Path | Purpose |
|---|---|
| `bible-groups/index.html` | Course hub: two cards (OT / NT) + description |
| `bible-groups/ot.html` | List of 52 OT topics with section headers + search |
| `bible-groups/nt.html` | List of 50 NT topics with section headers + search |
| `bible-groups/topic.html` | Topic view: 3 main tabs (text / questions / preparation), 2 sub-tabs in questions |
| `bible-groups/topics.json` | Metadata for all 102 topics (id, title, reference, refStructured, slug, media) |
| `bible-groups/ot/NN-slug-mine.md` | User's questions for each OT topic (52 files) |
| `bible-groups/ot/NN-slug-hagen.md` | Hagenhans questions for each OT topic (52 files) |
| `bible-groups/nt/NN-slug-mine.md` | User's questions for each NT topic (50 files) |
| `bible-groups/nt/NN-slug-hagen.md` | Hagenhans questions for each NT topic (50 files) |
| `bible-groups/media/NN-slug/*` | Audio/images per topic (only populated topics have folders) |
| `bible-groups/assets/synodal-render.js` | Reusable function to render Bible passage from `data/synodal.json` |
| `bible-groups/assets/theme-toggle.js` | Reusable theme toggle (extracted from existing pages) |
| `bible-groups/assets/styles.css` | Shared course styles (theme vars, list, tabs, lightbox) |
| `scripts/extract_bible_groups.py` | One-off PDF extractor — produces topics.json + all .md files |
| `scripts/scan_media.py` | Helper that updates `media` blocks in `topics.json` from on-disk files |
| `index.html` | Hub — add third card linking to `bible-groups/` |
| `CLAUDE.md` | Add a section documenting the new course |

---

## Task 1: Scaffold directory structure and shared assets

**Files:**
- Create: `bible-groups/index.html`
- Create: `bible-groups/assets/styles.css`
- Create: `bible-groups/assets/theme-toggle.js`
- Create: `bible-groups/ot/.gitkeep`
- Create: `bible-groups/nt/.gitkeep`
- Create: `bible-groups/media/.gitkeep`

- [ ] **Step 1: Create the directory layout**

```bash
mkdir -p bible-groups/{ot,nt,media,assets}
touch bible-groups/{ot,nt,media}/.gitkeep
```

- [ ] **Step 2: Extract the theme toggle into a shared script**

Create `bible-groups/assets/theme-toggle.js` with the exact body used in `burnham/index.html` (lines 277–292):

```javascript
(function () {
  const toggle = document.getElementById('themeToggle');
  if (!toggle) return;
  const icon = toggle.querySelector('i');
  const saved = localStorage.getItem('theme');

  if (saved !== 'dark') {
    document.documentElement.classList.add('light');
    icon.classList.replace('fa-sun', 'fa-moon');
  }

  toggle.addEventListener('click', () => {
    const isLight = document.documentElement.classList.toggle('light');
    icon.classList.replace(isLight ? 'fa-sun' : 'fa-moon', isLight ? 'fa-moon' : 'fa-sun');
    localStorage.setItem('theme', isLight ? 'light' : 'dark');
  });
})();
```

- [ ] **Step 3: Create the shared stylesheet**

Create `bible-groups/assets/styles.css` containing the theme variables (light + dark), body/header/back-link/theme-toggle/list-of-topics styles **identical to `burnham/index.html`** (lines 13–162), plus the tab and lightbox styles used in Tasks 8–11. For now, include the variables and the base styles — tab/lightbox styles will be appended in their tasks.

Use these additions (kept simple, vanilla CSS):

```css
/* Tabs */
.tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--border); margin: 24px 0 20px; }
.tab-btn {
  background: transparent; border: none; color: var(--text-muted);
  font-family: inherit; font-size: 15px; font-weight: 600;
  padding: 10px 16px; cursor: pointer; border-bottom: 2px solid transparent;
  transition: color 0.2s, border-color 0.2s;
}
.tab-btn:hover { color: var(--text); }
.tab-btn.active { color: var(--gold); border-bottom-color: var(--gold); }
.tab-panel { display: none; }
.tab-panel.active { display: block; }
.subtabs { display: flex; gap: 4px; margin-bottom: 16px; }
.subtab-btn {
  background: transparent; border: 1px solid var(--border); color: var(--text-muted);
  font-family: inherit; font-size: 13px; font-weight: 600;
  padding: 6px 14px; border-radius: 999px; cursor: pointer;
  transition: color 0.2s, border-color 0.2s, background 0.2s;
}
.subtab-btn.active { color: var(--gold); border-color: var(--gold); background: var(--hover-bg, rgba(212,168,67,0.08)); }

/* Search */
.search-input {
  width: 100%; box-sizing: border-box;
  background: transparent; border: 1px solid var(--border);
  color: var(--text); font-family: inherit; font-size: 15px;
  padding: 10px 14px; border-radius: 8px; margin: 12px 0 20px;
}
.search-input:focus { outline: none; border-color: var(--gold); }

/* Topic row icons */
.topic-icons { font-size: 12px; color: var(--text-muted); margin-left: 8px; display: flex; gap: 6px; }
.topic-icons i { color: var(--gold); }

/* Bible text */
.passage { font-family: "Lora", serif; font-size: 18px; line-height: 1.8; color: var(--text-secondary); }
.passage .verse-num { font-size: 11px; vertical-align: super; color: var(--gold); margin-right: 3px; font-weight: 700; font-family: "Montserrat", sans-serif; }
.passage .chapter-heading { font-family: "Montserrat", sans-serif; font-weight: 700; color: var(--gold); font-size: 14px; text-transform: uppercase; letter-spacing: 1.5px; margin: 28px 0 12px; }
.passage p { margin-bottom: 10px; }

/* Media tab */
.media-block { margin-bottom: 28px; }
.media-block h3 { font-size: 15px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 10px; }
.media-audio { width: 100%; margin-bottom: 8px; }
.media-image { max-width: 100%; border-radius: 8px; border: 1px solid var(--border); cursor: zoom-in; margin-bottom: 12px; }

/* Lightbox */
.lightbox { position: fixed; inset: 0; background: rgba(0,0,0,0.92); display: none; align-items: center; justify-content: center; padding: 24px; z-index: 1000; cursor: zoom-out; }
.lightbox.open { display: flex; }
.lightbox img { max-width: 100%; max-height: 100%; object-fit: contain; }
```

Theme variables block — copy verbatim from `burnham/index.html:13–31` and add `--hover-bg` (already present there).

- [ ] **Step 4: Build `bible-groups/index.html` (course hub)**

Two cards leading to `ot.html` and `nt.html`. Structure mirrors root `index.html` (cards layout), but inside the course. Use `<link rel="stylesheet" href="assets/styles.css">` and `<script src="assets/theme-toggle.js"></script>`.

Content:
- `<header>` with `<h1>Изучение Библии в малых группах</h1>` and a Lora-italic subtitle: `102 темы для разборов в группе &ndash; Ветхий и Новый Заветы`
- Two cards: «Ветхий Завет — 52 темы» (icon `fa-scroll`) and «Новый Завет — 50 тем» (icon `fa-cross`)
- Back link `← Все курсы` → `../`

- [ ] **Step 5: Manual verification**

Run a local server and open the hub:

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000/bible-groups/` — verify hub loads with both cards, theme toggle works, en dashes render correctly, OT/NT card links 404 (because the pages don't exist yet — that's expected).

- [ ] **Step 6: Commit**

```bash
git add bible-groups/ scripts/  # scripts/ added only if it exists
git commit -m "$(cat <<'EOF'
Scaffold bible-groups course directory and shared assets

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Extraction script — Bible reference parser

A pure-Python helper that takes `"Бытие 1:1–2:4"` / `"Исход 19—20"` / `"Иоанна 3; Ефесянам 2"` and returns the `refStructured` shape from the spec.

**Files:**
- Create: `scripts/__init__.py` (empty, so we can import as a package)
- Create: `scripts/bible_refs.py`
- Create: `scripts/test_bible_refs.py`

- [ ] **Step 1: Stub the module**

Create `scripts/bible_refs.py`:

```python
"""Parse Russian Bible references into structured form aligned with data/synodal.json abbrevs."""

# Map of Russian book names (and common short forms) -> abbrev in data/synodal.json.
# Fill in iteratively as the extractor finds new books.
BOOK_MAP = {
    "Бытие": "gn",
    "Исход": "ex",
    "Левит": "lv",
    "Числа": "nm",
    "Второзаконие": "dt",
    # ... extended as needed (full list to be filled in Step 3)
}


class RefParseError(ValueError):
    pass


def parse_reference(text: str) -> dict:
    """Return {'passages': [{'book': abbrev, 'from': [ch, v], 'to': [ch, v]}, ...]}.

    Always returns a list — single-passage refs are a list of length 1.
    Verse defaults: missing 'from' verse = 1; missing 'to' verse = last verse of chapter (sentinel -1).
    """
    raise NotImplementedError
```

- [ ] **Step 2: Write the test cases**

Create `scripts/test_bible_refs.py`. Use plain `assert` (no test framework needed):

```python
from bible_refs import parse_reference

def test_chapter_verse_range():
    r = parse_reference("Бытие 1:1–2:4")
    assert r == {"passages": [{"book": "gn", "from": [1, 1], "to": [2, 4]}]}, r

def test_single_chapter():
    r = parse_reference("Бытие 3")
    assert r == {"passages": [{"book": "gn", "from": [3, 1], "to": [3, -1]}]}, r

def test_chapter_range_en_dash():
    r = parse_reference("Исход 19–20")
    assert r == {"passages": [{"book": "ex", "from": [19, 1], "to": [20, -1]}]}, r

def test_chapter_range_em_dash():
    # PDFs occasionally use em dash; we accept either
    r = parse_reference("Исход 19—20")
    assert r == {"passages": [{"book": "ex", "from": [19, 1], "to": [20, -1]}]}, r

def test_multiple_passages_semicolon_same_book():
    r = parse_reference("Исход 1; 3; 12")
    assert r == {"passages": [
        {"book": "ex", "from": [1, 1], "to": [1, -1]},
        {"book": "ex", "from": [3, 1], "to": [3, -1]},
        {"book": "ex", "from": [12, 1], "to": [12, -1]},
    ]}, r

def test_multiple_passages_semicolon_different_books():
    r = parse_reference("Иоанна 3; Ефесянам 2")
    assert r == {"passages": [
        {"book": "jn", "from": [3, 1], "to": [3, -1]},
        {"book": "eph", "from": [2, 1], "to": [2, -1]},
    ]}, r

def test_verse_range_within_chapter():
    r = parse_reference("Бытие 2:5-25")
    assert r == {"passages": [{"book": "gn", "from": [2, 5], "to": [2, 25]}]}, r

def test_numbered_book():
    r = parse_reference("1 Царств 8")
    assert r == {"passages": [{"book": "1sm", "from": [8, 1], "to": [8, -1]}]}, r

if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ok  {name}")
    print("All bible_refs tests passed.")
```

- [ ] **Step 3: Implement `parse_reference` and complete `BOOK_MAP`**

Fill `BOOK_MAP` for all 66 books — derive abbrevs from `data/synodal.json` and pair them with Russian names from the existing `burnham/index.html` references plus commonly used forms.

Full list reference (Russian → abbrev): `Бытие→gn, Исход→ex, Левит→lv, Числа→nm, Второзаконие→dt, Иисус Навин→js, Судей→jud, Руфь→rt, 1 Царств→1sm, 2 Царств→2sm, 3 Царств→1kg, 4 Царств→2kg, 1 Паралипоменон→1ch, 2 Паралипоменон→2ch, Ездра→ezr, Неемия→ne, Есфирь→et, Иов→jb, Псалтирь→ps, Притчи→prv, Екклесиаст→ec, Песнь Песней→so, Исаия→is, Иеремия→jr, Плач Иеремии→lm, Иезекииль→ezk, Даниил→dn, Осия→ho, Иоиль→jl, Амос→am, Авдий→ob, Иона→jn (TODO: see note), Михей→mi, Наум→na, Аввакум→hk, Софония→zp, Аггей→hg, Захария→zc, Малахия→ml, Матфея→mt, Марка→mk, Луки→lk, Иоанна→jn, Деяния→act, Римлянам→rm, 1 Коринфянам→1co, 2 Коринфянам→2co, Галатам→gl, Ефесянам→eph, Филиппийцам→ph, Колоссянам→cl, 1 Фессалоникийцам→1ts, 2 Фессалоникийцам→2ts, 1 Тимофею→1tm, 2 Тимофею→2tm, Титу→tt, Филимону→phm, Евреям→hb, Иакова→jm, 1 Петра→1pe, 2 Петра→2pe, 1 Иоанна→1jn, 2 Иоанна→2jn, 3 Иоанна→3jn, Иуды→jd, Откровение→rev`

**Important:** the `jn` collision (Иона vs Иоанна) — verify against `data/synodal.json`. Run `python3 -c "import json; print([(b['abbrev'], len(b['chapters'])) for b in json.load(open('data/synodal.json'))])"` and reconcile. Use real abbrevs from that file.

Implementation:

```python
import re

# Normalize dashes
_DASHES = "–—−-"
_DASH_CLASS = f"[{_DASHES}]"

# Sort book names by length descending so "1 Иоанна" matches before "Иоанна"
def _sorted_book_names():
    return sorted(BOOK_MAP.keys(), key=len, reverse=True)


def _parse_single(text: str, last_book: str | None) -> dict:
    """Parse one passage segment like 'Бытие 1:1–2:4' or just '3' (using last_book)."""
    text = text.strip()
    book_abbrev = None
    rest = text
    for name in _sorted_book_names():
        if text.startswith(name):
            book_abbrev = BOOK_MAP[name]
            rest = text[len(name):].strip()
            break
    if book_abbrev is None:
        if last_book is None:
            raise RefParseError(f"No book in segment: {text!r}")
        book_abbrev = last_book

    # rest now looks like: "1:1–2:4" / "19–20" / "3" / "2:5-25" / "8"
    rest = re.sub(_DASH_CLASS, "-", rest)  # normalize
    m_range = re.match(r"^\s*(\d+)(?::(\d+))?(?:\s*-\s*(\d+)(?::(\d+))?)?\s*$", rest)
    if not m_range:
        raise RefParseError(f"Cannot parse chapter/verse part: {rest!r} (full: {text!r})")
    ch1 = int(m_range.group(1))
    v1 = int(m_range.group(2)) if m_range.group(2) else 1
    if m_range.group(3):
        ch2 = int(m_range.group(3))
        v2 = int(m_range.group(4)) if m_range.group(4) else -1
    else:
        ch2 = ch1
        v2 = int(m_range.group(2)) if m_range.group(2) else -1
        if m_range.group(2) and not m_range.group(3):
            v2 = v1  # single verse "Бытие 1:1"
    return {"book": book_abbrev, "from": [ch1, v1], "to": [ch2, v2]}


def parse_reference(text: str) -> dict:
    segments = [s for s in re.split(r";", text) if s.strip()]
    passages = []
    last_book = None
    for seg in segments:
        p = _parse_single(seg, last_book)
        passages.append(p)
        last_book = p["book"]
    return {"passages": passages}
```

- [ ] **Step 4: Run the tests**

```bash
cd scripts && python3 test_bible_refs.py
```

Expected: `All bible_refs tests passed.`

- [ ] **Step 5: Commit**

```bash
git add scripts/__init__.py scripts/bible_refs.py scripts/test_bible_refs.py
git commit -m "$(cat <<'EOF'
Add Bible reference parser for bible-groups extractor

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: PDF extractor — your questions (OT + NT)

**Files:**
- Create: `scripts/extract_bible_groups.py`
- Create: `bible-groups/ot/NN-slug-mine.md` × 52
- Create: `bible-groups/nt/NN-slug-mine.md` × 50
- Create: `bible-groups/topics.json` (initial version, mine only, no media yet)

- [ ] **Step 1: Install pdfplumber**

```bash
python3 -m pip install --user pdfplumber
```

Verify: `python3 -c "import pdfplumber; print(pdfplumber.__version__)"` prints a version.

- [ ] **Step 2: Write the extractor skeleton**

Create `scripts/extract_bible_groups.py`. Top-level structure:

```python
"""One-off extractor: read source PDFs into bible-groups/{ot,nt}/*.md and topics.json.

Idempotent — safe to re-run; overwrites generated files. Source PDFs in groups/row_material/.
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

import pdfplumber

from bible_refs import parse_reference

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "groups" / "row_material"
OUT = ROOT / "bible-groups"

OT_PDF = SRC / "Вопросы_Ветхий_Завет_1-52.pdf"
NT_PDF = SRC / "Вопросы_Новый_Завет_51-100.pdf"
HAGEN_PDF = SRC / "Изучение_Библии_в_малых_группах_для_лидеров.pdf"

# Russian → latin transliteration table (GOST-7.79 simplified)
_TR = {
    "а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"e","ж":"zh","з":"z",
    "и":"i","й":"y","к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r",
    "с":"s","т":"t","у":"u","ф":"f","х":"kh","ц":"ts","ч":"ch","ш":"sh","щ":"sch",
    "ъ":"","ы":"y","ь":"","э":"e","ю":"yu","я":"ya",
}

def slugify(num: int, title: str) -> str:
    s = title.lower()
    out = []
    for c in s:
        if c in _TR:
            out.append(_TR[c])
        elif c.isalnum():
            out.append(c)
        elif c in " -_":
            out.append("-")
    slug = "".join(out)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return f"{num:02d}-{slug}"
```

- [ ] **Step 3: Implement the OT/NT page parser**

Each page contains exactly one topic. Layout (from inspection of pages 1–3):

```
I. В НАЧАЛЕ                        ← section header (optional, appears once per section)

1. Пролог (Бытие 1:1 -- 2:4)       ← title line
ВВЕДЕНИЕ
— question
— question
НАБЛЮДЕНИЕ
— question
— ...
ПОНИМАНИЕ
— ...
ПРИМЕНЕНИЕ
— ...
```

Add to extractor:

```python
SECTION_RE = re.compile(r"^([IVXLCDM]+)\.\s+(.+?)$")
TITLE_RE = re.compile(r"^(\d+)\.\s+(.+?)\s*\((.+?)\)\s*$")
BLOCK_NAMES = ("ВВЕДЕНИЕ", "НАБЛЮДЕНИЕ", "ПОНИМАНИЕ", "ПРИМЕНЕНИЕ")
BLOCK_TITLES = {
    "ВВЕДЕНИЕ": "Введение",
    "НАБЛЮДЕНИЕ": "Наблюдение",
    "ПОНИМАНИЕ": "Понимание",
    "ПРИМЕНЕНИЕ": "Применение",
}

def _clean_line(s: str) -> str:
    # PDF uses "--" for en dash; convert to real en dash for display.
    return s.replace(" -- ", " – ").replace("--", "–").strip()

def _extract_topic_from_text(page_text: str) -> tuple[dict | None, str]:
    """Return (topic_dict_or_None, section_or_empty). Empty topic => skip page."""
    lines = [ln.rstrip() for ln in page_text.splitlines() if ln.strip()]
    section = ""
    idx = 0
    if lines and SECTION_RE.match(lines[0]):
        section = lines[0]
        idx = 1
    if idx >= len(lines):
        return None, section
    m = TITLE_RE.match(lines[idx])
    if not m:
        return None, section
    number = int(m.group(1))
    title = _clean_line(m.group(2))
    reference = _clean_line(m.group(3))

    # Parse remaining lines into blocks
    blocks: dict[str, list[str]] = {b: [] for b in BLOCK_NAMES}
    current = None
    buf: list[str] = []

    def flush():
        nonlocal buf
        if current and buf:
            text = " ".join(buf).strip()
            text = _clean_line(text)
            blocks[current].append(text)
        buf = []

    for ln in lines[idx + 1:]:
        upper = ln.strip()
        if upper in BLOCK_NAMES:
            flush()
            current = upper
            continue
        if ln.lstrip().startswith(("—", "–", "-", "•")):
            flush()
            buf = [ln.lstrip(" —–-•").strip()]
        else:
            buf.append(ln.strip())
    flush()

    return {
        "number": number,
        "title": title,
        "reference": reference,
        "blocks": blocks,
        "section": section,
    }, section
```

- [ ] **Step 4: Implement the per-testament loop**

```python
def extract_questions_pdf(pdf_path: Path, testament: str) -> list[dict]:
    """Open PDF, return list of topic dicts (one per page)."""
    topics = []
    current_section = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page_no, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            topic, section = _extract_topic_from_text(text)
            if section:
                current_section = section
            if not topic:
                print(f"  WARN: {pdf_path.name} p{page_no}: no topic parsed", file=sys.stderr)
                continue
            topic["section"] = topic["section"] or current_section
            topic["testament"] = testament
            topics.append(topic)
    return topics
```

- [ ] **Step 5: Write Markdown emitter**

```python
def write_mine_md(topic: dict, out_dir: Path) -> str:
    slug = slugify(topic["number"], topic["title"])
    path = out_dir / f"{slug}-mine.md"
    body = []
    for key in BLOCK_NAMES:
        items = topic["blocks"].get(key) or []
        if not items:
            continue
        body.append(f"## {BLOCK_TITLES[key]}\n")
        for q in items:
            body.append(f"- {q}")
        body.append("")  # blank line
    path.write_text("\n".join(body).rstrip() + "\n", encoding="utf-8")
    return slug
```

- [ ] **Step 6: Add `topics.json` builder + `main()`**

```python
def build_topic_record(topic: dict, slug: str) -> dict:
    testament = topic["testament"]
    n = topic["number"]
    try:
        ref_structured = parse_reference(topic["reference"])
    except Exception as e:
        print(f"  WARN: ref parse failed for {testament} {n} '{topic['reference']}': {e}", file=sys.stderr)
        ref_structured = None
    return {
        "id": f"{testament}-{n:02d}",
        "testament": testament,
        "number": n,
        "section": topic["section"],
        "title": topic["title"],
        "reference": topic["reference"],
        "refStructured": ref_structured,
        "slug": slug,
        "media": {"audio": [], "image": []},
    }


def main():
    (OUT / "ot").mkdir(parents=True, exist_ok=True)
    (OUT / "nt").mkdir(parents=True, exist_ok=True)

    all_topics = []
    for pdf, testament in [(OT_PDF, "ot"), (NT_PDF, "nt")]:
        print(f"Reading {pdf.name}...")
        topics = extract_questions_pdf(pdf, testament)
        out_dir = OUT / testament
        for t in topics:
            slug = write_mine_md(t, out_dir)
            all_topics.append(build_topic_record(t, slug))

    # Sort: OT first then NT, by number
    all_topics.sort(key=lambda r: (0 if r["testament"] == "ot" else 1, r["number"]))

    topics_path = OUT / "topics.json"
    topics_path.write_text(json.dumps(all_topics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {topics_path} ({len(all_topics)} topics)")

if __name__ == "__main__":
    main()
```

- [ ] **Step 7: Run extractor**

```bash
python3 scripts/extract_bible_groups.py
```

Expected:
- Prints `Reading Вопросы_Ветхий_Завет_1-52.pdf...` then `Reading Вопросы_Новый_Завет_51-100.pdf...`
- Possibly a few `WARN: ref parse failed` lines — note them
- Final line: `Wrote .../topics.json (102 topics)`

- [ ] **Step 8: Verify output sanity**

```bash
ls bible-groups/ot/*.md | wc -l   # expect 52
ls bible-groups/nt/*.md | wc -l   # expect 50
python3 -c "import json; t=json.load(open('bible-groups/topics.json')); print(len(t), t[0]['title'], t[-1]['title'])"
```

Open 2–3 generated `*-mine.md` files manually (e.g., `bible-groups/ot/01-prolog-mine.md`) and check that all four blocks render and questions look correct.

- [ ] **Step 9: Fix any warnings**

For each `WARN: ref parse failed` line from Step 7, extend `BOOK_MAP` in `scripts/bible_refs.py` (add the abbreviation/variant) or special-case the literal in `_clean_line`. Re-run extractor until **zero warnings** and **all 102 records have non-null `refStructured`**.

Sanity-check command:

```bash
python3 -c "import json; t=json.load(open('bible-groups/topics.json')); bad=[r['id'] for r in t if r['refStructured'] is None]; print('bad:', bad)"
```

Expected: `bad: []`

- [ ] **Step 10: Commit**

```bash
git add scripts/extract_bible_groups.py scripts/bible_refs.py bible-groups/ot/*.md bible-groups/nt/*.md bible-groups/topics.json
git commit -m "$(cat <<'EOF'
Extract user's OT and NT questions into bible-groups course

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: PDF extractor — Hagenhans questions

Same 102 topics but from a different PDF, starting at page 11 with the layout `a. Title (Ref)` and three icon blocks (☕ / 📖 / ❤️).

**Files:**
- Modify: `scripts/extract_bible_groups.py` (add `extract_hagen_pdf` and call it from `main`)
- Create: `bible-groups/ot/NN-slug-hagen.md` × 52
- Create: `bible-groups/nt/NN-slug-hagen.md` × 50

- [ ] **Step 1: Inspect Hagenhans pages programmatically**

```bash
python3 - <<'PY'
import pdfplumber, sys
with pdfplumber.open("groups/row_material/Изучение_Библии_в_малых_группах_для_лидеров.pdf") as pdf:
    for i in (10, 11, 12, 13, 30, 60):
        if i < len(pdf.pages):
            print(f"===== page {i+1} =====")
            print(pdf.pages[i].extract_text()[:600])
PY
```

Observe how `a. Пролог (Бытие 1:1 – 2:4)` and icon markers appear. The three blocks are introduced by tiny coffee/book/heart icons rendered as glyphs; `extract_text()` likely yields nothing for the icons themselves, or yields placeholder characters. Capture the actual delimiter you observe and adapt.

- [ ] **Step 2: Implement the Hagenhans parser**

Add to `scripts/extract_bible_groups.py`:

```python
# Hagenhans uses letters a, b, c, ... within roman sections. Same 102 topics in the same order.
HAGEN_TITLE_RE = re.compile(r"^([a-zа-я])\.\s+(.+?)\s*\((.+?)\)\s*$", re.IGNORECASE)

# Heuristic: the three Hagenhans blocks always appear in order
# introduction / observation / application. We don't rely on icon glyphs;
# we split the post-title text into three chunks by detecting bullets and
# assuming the first chunk = intro, second = obs, third = application.
# After running Step 1, refine this if the visual layout offers a clearer cue.

HAGEN_BLOCK_TITLES = ["☕ Введение", "📖 Наблюдение и понимание", "❤️ Применение"]


def _extract_hagen_topic(page_text: str) -> dict | None:
    lines = [ln.rstrip() for ln in page_text.splitlines() if ln.strip()]
    # Drop section header line if present (roman: "I. В начале")
    if lines and SECTION_RE.match(lines[0]):
        lines = lines[1:]
    if not lines:
        return None
    m = HAGEN_TITLE_RE.match(lines[0])
    if not m:
        return None
    title = _clean_line(m.group(2))
    reference = _clean_line(m.group(3))

    # Group lines into bullets; each bullet starts with • or — or - or a Cyrillic dash.
    bullets: list[str] = []
    buf: list[str] = []
    def flush():
        nonlocal buf
        if buf:
            bullets.append(_clean_line(" ".join(buf)))
            buf = []
    for ln in lines[1:]:
        stripped = ln.lstrip()
        if stripped.startswith(("•", "—", "–", "-")):
            flush()
            buf = [stripped.lstrip(" •—–-").strip()]
        else:
            buf.append(stripped)
    flush()

    # Split bullets across three blocks. We use page_text positions of any
    # detectable group breaks (blank lines between bullets in the raw text):
    # iterate raw text again and remember where blank gaps fell.
    # For robustness, fall back to "first 3 = intro, next 5 = obs, rest = app"
    # only if no gaps detected; print a warning so we can refine.
    if len(bullets) < 3:
        return None

    # Heuristic: even split by blank-line groups
    groups: list[list[str]] = []
    cur: list[str] = []
    blank_seen = False
    for raw in page_text.splitlines():
        s = raw.strip()
        if not s:
            blank_seen = True
            continue
        if s.startswith(("•", "—", "–", "-")) and blank_seen and cur:
            groups.append(cur)
            cur = []
        if s.startswith(("•", "—", "–", "-")):
            cur.append(_clean_line(s.lstrip(" •—–-").strip()))
        else:
            if cur:
                cur[-1] = cur[-1] + " " + s
        blank_seen = False
    if cur:
        groups.append(cur)

    if len(groups) != 3:
        # Fallback: leave a single block named "Вопросы" with all bullets
        return {"title": title, "reference": reference, "groups": [bullets], "fallback": True}

    return {"title": title, "reference": reference, "groups": groups, "fallback": False}
```

This is intentionally defensive — the fallback path emits a single-block `*-hagen.md` so the build never fails. After running, inspect any fallbacks and refine.

- [ ] **Step 3: Implement the page iterator**

```python
def extract_hagen_pdf(pdf_path: Path) -> list[dict]:
    topics = []
    with pdfplumber.open(pdf_path) as pdf:
        # Per Task 4 inspection: Hagenhans content starts at page index 10 (page 11 in viewer).
        START = 10
        for page_no, page in enumerate(pdf.pages[START:], start=START + 1):
            text = page.extract_text() or ""
            topic = _extract_hagen_topic(text)
            if topic is None:
                continue
            topics.append(topic)
    return topics


def write_hagen_md(slug: str, topic: dict, out_dir: Path) -> None:
    path = out_dir / f"{slug}-hagen.md"
    parts: list[str] = []
    if topic.get("fallback"):
        parts.append("## Вопросы\n")
        for q in topic["groups"][0]:
            parts.append(f"- {q}")
        parts.append("")
    else:
        for heading, items in zip(HAGEN_BLOCK_TITLES, topic["groups"]):
            parts.append(f"## {heading}\n")
            for q in items:
                parts.append(f"- {q}")
            parts.append("")
    path.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")
```

- [ ] **Step 4: Wire Hagenhans into `main`**

Update `main()`:

```python
def main():
    (OUT / "ot").mkdir(parents=True, exist_ok=True)
    (OUT / "nt").mkdir(parents=True, exist_ok=True)

    all_topics = []
    for pdf, testament in [(OT_PDF, "ot"), (NT_PDF, "nt")]:
        print(f"Reading {pdf.name}...")
        topics = extract_questions_pdf(pdf, testament)
        out_dir = OUT / testament
        for t in topics:
            slug = write_mine_md(t, out_dir)
            t["slug"] = slug
            all_topics.append(build_topic_record(t, slug))

    print(f"Reading {HAGEN_PDF.name} (Hagenhans)...")
    hagen_topics = extract_hagen_pdf(HAGEN_PDF)
    print(f"  parsed {len(hagen_topics)} Hagenhans topics")

    # Pair by order: Hagenhans topic[i] corresponds to all_topics[i]
    fallbacks: list[str] = []
    for i, h in enumerate(hagen_topics):
        if i >= len(all_topics):
            break
        rec = all_topics[i]
        out_dir = OUT / rec["testament"]
        write_hagen_md(rec["slug"], h, out_dir)
        if h.get("fallback"):
            fallbacks.append(rec["id"])
    if fallbacks:
        print(f"  WARN: {len(fallbacks)} Hagenhans topics used fallback layout: {fallbacks}", file=sys.stderr)

    all_topics.sort(key=lambda r: (0 if r["testament"] == "ot" else 1, r["number"]))
    (OUT / "topics.json").write_text(json.dumps(all_topics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote topics.json ({len(all_topics)} topics)")
```

- [ ] **Step 5: Run and verify**

```bash
python3 scripts/extract_bible_groups.py
ls bible-groups/ot/*-hagen.md | wc -l   # expect 52
ls bible-groups/nt/*-hagen.md | wc -l   # expect 50
```

- [ ] **Step 6: Spot-check pairing**

Open `bible-groups/ot/01-prolog-mine.md` and `bible-groups/ot/01-prolog-hagen.md` — confirm the Hagenhans file has 3 sections (or a fallback) and questions roughly match what we saw in Task 4 Step 1.

If `len(hagen_topics) != 102` or many fallbacks: fix the parser by inspecting specific failing pages with `pdfplumber` directly, then re-run. Iterate up to ~3 times; if still failing on edge pages, accept the fallback for those and move on (they remain editable Markdown).

- [ ] **Step 7: Commit**

```bash
git add scripts/extract_bible_groups.py bible-groups/ot/*-hagen.md bible-groups/nt/*-hagen.md bible-groups/topics.json
git commit -m "$(cat <<'EOF'
Extract Hagenhans questions into bible-groups course

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Seed example media (topic 43)

**Files:**
- Create: `bible-groups/media/43-prizvanie-ieremii/*` (audio + images)
- Modify: `bible-groups/topics.json` (only the topic 43 record)
- Create: `scripts/scan_media.py`

- [ ] **Step 1: Find topic 43's slug**

```bash
python3 -c "import json; t=json.load(open('bible-groups/topics.json')); print([r for r in t if r['number']==43])"
```

The `slug` should be like `43-prizvanie-ieremii`. If different — adjust the path accordingly in subsequent steps.

- [ ] **Step 2: Copy media files in**

```bash
mkdir -p "bible-groups/media/43-prizvanie-ieremii"
cp "groups/row_material/data example 43. Призвание Иеремии/Призвание_Иеремии_как_диалог_или_вердикт.m4a"   "bible-groups/media/43-prizvanie-ieremii/audio-1.m4a"
cp "groups/row_material/data example 43. Призвание Иеремии/Синдром_самозванца_и_разбитые_водоемы_Иеремии.m4a" "bible-groups/media/43-prizvanie-ieremii/audio-2.m4a"
cp "groups/row_material/data example 43. Призвание Иеремии/unnamed.png"    "bible-groups/media/43-prizvanie-ieremii/image-1.png"
cp "groups/row_material/data example 43. Призвание Иеремии/unnamed(1).png" "bible-groups/media/43-prizvanie-ieremii/image-2.png"
cp "groups/row_material/data example 43. Призвание Иеремии/unnamed(2).png" "bible-groups/media/43-prizvanie-ieremii/image-3.png"
```

- [ ] **Step 3: Write the media scanner**

Create `scripts/scan_media.py`:

```python
"""Scan bible-groups/media/*/ and update the `media` block of each topic in topics.json.

Idempotent. Image extensions: .png .jpg .jpeg .webp .gif. Audio: .m4a .mp3 .ogg .wav.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "bible-groups"
MEDIA = OUT / "media"
TOPICS = OUT / "topics.json"

AUDIO_EXT = {".m4a", ".mp3", ".ogg", ".wav"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def collect(folder: Path) -> dict[str, list[str]]:
    audio, image = [], []
    if not folder.is_dir():
        return {"audio": [], "image": []}
    for f in sorted(folder.iterdir()):
        if not f.is_file():
            continue
        ext = f.suffix.lower()
        if ext in AUDIO_EXT:
            audio.append(f.name)
        elif ext in IMAGE_EXT:
            image.append(f.name)
    return {"audio": audio, "image": image}


def main():
    topics = json.loads(TOPICS.read_text(encoding="utf-8"))
    for rec in topics:
        rec["media"] = collect(MEDIA / rec["slug"])
    TOPICS.write_text(json.dumps(topics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("topics.json media blocks updated.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the scanner**

```bash
python3 scripts/scan_media.py
python3 -c "import json; t=json.load(open('bible-groups/topics.json')); r=[x for x in t if x['number']==43][0]; print(r['media'])"
```

Expected: `{'audio': ['audio-1.m4a', 'audio-2.m4a'], 'image': ['image-1.png', 'image-2.png', 'image-3.png']}`

- [ ] **Step 5: Commit**

```bash
git add bible-groups/media/ bible-groups/topics.json scripts/scan_media.py
git commit -m "$(cat <<'EOF'
Add example media for bible-groups topic 43 + media scanner script

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Synodal text renderer

Browser-side module that takes a `refStructured` record and returns rendered HTML using `data/synodal.json`.

**Files:**
- Create: `bible-groups/assets/synodal-render.js`

- [ ] **Step 1: Implement the renderer**

```javascript
// bible-groups/assets/synodal-render.js
// Renders one or more Bible passages from data/synodal.json (cached after first load).

let _synodalCache = null;

async function loadSynodal() {
  if (_synodalCache) return _synodalCache;
  const res = await fetch('../data/synodal.json');
  if (!res.ok) throw new Error('Failed to load synodal.json');
  _synodalCache = await res.json();
  return _synodalCache;
}

function findBook(synodal, abbrev) {
  return synodal.find(b => b.abbrev === abbrev);
}

function bookTitleRu(abbrev) {
  // Minimal map for chapter headings. Falls back to abbrev if unknown.
  const M = {
    gn:'Бытие', ex:'Исход', lv:'Левит', nm:'Числа', dt:'Второзаконие',
    js:'Иисус Навин', jud:'Книга Судей', rt:'Руфь',
    '1sm':'1 Царств','2sm':'2 Царств','1kg':'3 Царств','2kg':'4 Царств',
    '1ch':'1 Паралипоменон','2ch':'2 Паралипоменон',
    ezr:'Ездра', ne:'Неемия', et:'Есфирь', jb:'Иов', ps:'Псалтирь',
    prv:'Притчи', ec:'Екклесиаст', so:'Песнь Песней',
    is:'Исаия', jr:'Иеремия', lm:'Плач Иеремии', ezk:'Иезекииль',
    dn:'Даниил', ho:'Осия', jl:'Иоиль', am:'Амос', ob:'Авдий',
    jon:'Иона', mi:'Михей', na:'Наум', hk:'Аввакум', zp:'Софония',
    hg:'Аггей', zc:'Захария', ml:'Малахия',
    mt:'Матфея', mk:'Марка', lk:'Луки', jn:'Иоанна', act:'Деяния',
    rm:'Римлянам','1co':'1 Коринфянам','2co':'2 Коринфянам',
    gl:'Галатам', eph:'Ефесянам', ph:'Филиппийцам', cl:'Колоссянам',
    '1ts':'1 Фессалоникийцам','2ts':'2 Фессалоникийцам',
    '1tm':'1 Тимофею','2tm':'2 Тимофею', tt:'Титу', phm:'Филимону',
    hb:'Евреям', jm:'Иакова','1pe':'1 Петра','2pe':'2 Петра',
    '1jn':'1 Иоанна','2jn':'2 Иоанна','3jn':'3 Иоанна', jd:'Иуды',
    rev:'Откровение'
  };
  return M[abbrev] || abbrev;
}

function renderPassage(synodal, p) {
  const book = findBook(synodal, p.book);
  if (!book) return `<p class="error">Книга «${p.book}» не найдена.</p>`;
  const [ch1, v1Raw] = p.from;
  const [ch2, v2Raw] = p.to;
  let html = '';
  for (let ch = ch1; ch <= ch2; ch++) {
    const chapter = book.chapters[ch - 1];
    if (!chapter) continue;
    const vStart = (ch === ch1) ? Math.max(1, v1Raw) : 1;
    const vEnd = (ch === ch2) ? (v2Raw === -1 ? chapter.length : Math.min(v2Raw, chapter.length)) : chapter.length;
    html += `<div class="chapter-heading">${bookTitleRu(p.book)} ${ch}</div>`;
    html += '<p>';
    for (let v = vStart; v <= vEnd; v++) {
      const verse = chapter[v - 1];
      if (!verse) continue;
      html += `<span class="verse-num">${v}</span>${escapeHtml(verse)} `;
    }
    html += '</p>';
  }
  return html;
}

function escapeHtml(s) {
  return s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

window.renderSynodal = async function renderSynodal(target, refStructured) {
  if (!refStructured || !refStructured.passages) {
    target.innerHTML = '<p class="error">Ссылка отсутствует.</p>';
    return;
  }
  try {
    const synodal = await loadSynodal();
    target.classList.add('passage');
    target.innerHTML = refStructured.passages.map(p => renderPassage(synodal, p)).join('');
  } catch (e) {
    target.innerHTML = `<p class="error">Не удалось загрузить текст: ${e.message}</p>`;
  }
};
```

- [ ] **Step 2: Smoke-test in browser**

Add a temporary test page `bible-groups/test-render.html`:

```html
<!doctype html><html><head><link rel="stylesheet" href="assets/styles.css"></head>
<body><div class="container"><div id="t"></div></div>
<script src="assets/synodal-render.js"></script>
<script>
  renderSynodal(document.getElementById('t'),
    {passages:[{book:'gn', from:[1,1], to:[2,4]}]});
</script></body></html>
```

Open `http://localhost:8000/bible-groups/test-render.html` — verify Genesis 1–2:4 renders correctly with verse numbers.

- [ ] **Step 3: Remove test page and commit**

```bash
rm bible-groups/test-render.html
git add bible-groups/assets/synodal-render.js
git commit -m "$(cat <<'EOF'
Add Synodal text renderer for bible-groups

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: List pages — `ot.html` and `nt.html`

Both pages share 95% of their markup, differing only in the testament filter, title, and back-link target. Use a single template, parameterized by a `data-testament` attribute or by URL-hash detection. Simpler: two near-identical files.

**Files:**
- Create: `bible-groups/ot.html`
- Create: `bible-groups/nt.html`
- Create: `bible-groups/assets/list.js` (shared list-rendering logic)

- [ ] **Step 1: Implement `list.js`**

```javascript
// bible-groups/assets/list.js
async function initList(testament) {
  const root = document.getElementById('topicList');
  const search = document.getElementById('search');
  const res = await fetch('topics.json');
  const topics = (await res.json()).filter(t => t.testament === testament);

  function render(filter) {
    const q = (filter || '').trim().toLowerCase();
    root.innerHTML = '';
    let currentSection = null;
    let sectionUl = null;
    for (const t of topics) {
      const matches = !q
        || String(t.number).includes(q)
        || t.title.toLowerCase().includes(q)
        || t.reference.toLowerCase().includes(q);
      if (!matches) continue;
      if (t.section !== currentSection) {
        currentSection = t.section;
        const h = document.createElement('div');
        h.className = 'section-title';
        h.textContent = t.section;
        root.appendChild(h);
        sectionUl = document.createElement('ul');
        sectionUl.className = 'topics';
        root.appendChild(sectionUl);
      }
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = `topic.html?id=${t.id}`;
      a.innerHTML = `
        <span class="topic-num">${t.number}</span>
        <span class="topic-title">${escapeHtml(t.title)}</span>
        <span class="topic-ref">${escapeHtml(t.reference)}</span>
        <span class="topic-icons">${iconsFor(t.media)}</span>
      `;
      li.appendChild(a);
      sectionUl.appendChild(li);
    }
    if (!root.children.length) {
      root.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:40px 0;">Ничего не найдено</p>';
    }
  }

  function iconsFor(media) {
    const out = [];
    if (media.audio && media.audio.length) out.push('<i class="fa-solid fa-headphones" title="Аудио"></i>');
    if (media.image && media.image.length) out.push('<i class="fa-solid fa-image" title="Картинки"></i>');
    return out.join('');
  }

  function escapeHtml(s){return s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}

  render('');
  search.addEventListener('input', e => render(e.target.value));
}
```

- [ ] **Step 2: Create `bible-groups/ot.html`**

Mirror `burnham/index.html` structure but reference shared assets. Body contents:

```html
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ветхий Завет &ndash; Изучение Библии</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
  <div class="container">
    <div class="top-bar">
      <a class="back-link" href="./"><i class="fas fa-arrow-left"></i> К курсу</a>
      <button class="theme-toggle" id="themeToggle" title="Сменить тему"><i class="fas fa-sun"></i></button>
    </div>
    <header>
      <h1>Ветхий Завет</h1>
      <p>52 темы для разборов в малых группах</p>
    </header>
    <input id="search" type="search" class="search-input" placeholder="Поиск по номеру, названию или ссылке…">
    <div id="topicList"></div>
  </div>
  <script src="assets/theme-toggle.js"></script>
  <script src="assets/list.js"></script>
  <script>initList('ot');</script>
</body>
</html>
```

- [ ] **Step 3: Create `bible-groups/nt.html`**

Identical to `ot.html`, but: `<title>Новый Завет</title>`, `<h1>Новый Завет</h1>`, `<p>50 тем для разборов в малых группах</p>`, `initList('nt')`.

- [ ] **Step 4: Manual verification**

Open `http://localhost:8000/bible-groups/ot.html`:
- 52 topics grouped under section headers
- Topic 43 shows headphones + image icons
- Typing `43` filters to one row
- Typing `завет` (case-insensitive) shows matching titles
- Theme toggle works
- Mobile: `topic-ref` hides at ≤600px (already in shared CSS)

Repeat for `nt.html`.

- [ ] **Step 5: Commit**

```bash
git add bible-groups/ot.html bible-groups/nt.html bible-groups/assets/list.js bible-groups/assets/styles.css
git commit -m "$(cat <<'EOF'
Add OT/NT list pages for bible-groups with search

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Topic view — main tabs + text rendering

**Files:**
- Create: `bible-groups/topic.html`

- [ ] **Step 1: HTML skeleton**

```html
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Тема &ndash; Изучение Библии</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <link rel="stylesheet" href="assets/styles.css">
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
  <div class="container">
    <div class="top-bar">
      <a class="back-link" id="backLink" href="ot.html"><i class="fas fa-arrow-left"></i> К списку</a>
      <button class="theme-toggle" id="themeToggle" title="Сменить тему"><i class="fas fa-sun"></i></button>
    </div>

    <header id="topicHeader">
      <h1 id="topicTitle">Загрузка…</h1>
      <p id="topicRef"></p>
    </header>

    <div class="tabs" role="tablist">
      <button class="tab-btn" data-tab="text"><i class="fa-solid fa-book-open"></i> Текст</button>
      <button class="tab-btn" data-tab="questions"><i class="fa-regular fa-circle-question"></i> Вопросы</button>
      <button class="tab-btn" data-tab="prep"><i class="fa-solid fa-headphones"></i> Подготовка</button>
    </div>

    <section class="tab-panel" id="panel-text"></section>

    <section class="tab-panel" id="panel-questions">
      <div class="subtabs">
        <button class="subtab-btn" data-subtab="mine">Мои</button>
        <button class="subtab-btn" data-subtab="hagen">Гагенганс</button>
      </div>
      <div id="questionsMine"></div>
      <div id="questionsHagen" style="display:none"></div>
    </section>

    <section class="tab-panel" id="panel-prep"></section>
  </div>

  <div class="lightbox" id="lightbox"><img id="lightboxImg" alt=""></div>

  <script src="assets/theme-toggle.js"></script>
  <script src="assets/synodal-render.js"></script>
  <script src="assets/topic.js"></script>
</body>
</html>
```

- [ ] **Step 2: Implement `bible-groups/assets/topic.js` — load + tabs + text panel**

Create the file with:

```javascript
(async function () {
  const params = new URLSearchParams(location.search);
  const id = params.get('id');
  if (!id) { document.getElementById('topicTitle').textContent = 'Тема не указана'; return; }

  const topics = await fetch('topics.json').then(r => r.json());
  const topic = topics.find(t => t.id === id);
  if (!topic) { document.getElementById('topicTitle').textContent = 'Тема не найдена'; return; }

  // Header
  document.title = `${topic.number}. ${topic.title} – Изучение Библии`;
  document.getElementById('topicTitle').textContent = `${topic.number}. ${topic.title}`;
  document.getElementById('topicRef').textContent = topic.reference;
  document.getElementById('backLink').href = topic.testament === 'ot' ? 'ot.html' : 'nt.html';

  // Text panel — render lazily on first activation
  let textRendered = false;
  async function ensureText() {
    if (textRendered) return;
    await renderSynodal(document.getElementById('panel-text'), topic.refStructured);
    textRendered = true;
  }

  // Main tabs
  const mainTabs = document.querySelectorAll('.tab-btn');
  const panels = { text: 'panel-text', questions: 'panel-questions', prep: 'panel-prep' };
  function activateTab(name) {
    mainTabs.forEach(b => b.classList.toggle('active', b.dataset.tab === name));
    for (const [k, id] of Object.entries(panels)) {
      document.getElementById(id).classList.toggle('active', k === name);
    }
    localStorage.setItem('bibleGroupsMainTab', name);
    if (name === 'text') ensureText();
    if (name === 'questions') ensureQuestions();
    if (name === 'prep') ensurePrep();
  }
  mainTabs.forEach(b => b.addEventListener('click', () => activateTab(b.dataset.tab)));

  const initialTab = localStorage.getItem('bibleGroupsMainTab') || 'text';
  activateTab(initialTab);

  // Question and prep loaders are filled in Tasks 9 and 10.
  async function ensureQuestions() { /* Task 9 */ }
  async function ensurePrep() { /* Task 10 */ }

  // Expose for other tasks to extend without duplicating fetches
  window._topic = topic;
  window._ensureQuestions = ensureQuestions;
  window._ensurePrep = ensurePrep;
})();
```

- [ ] **Step 3: Manual verification (text tab only)**

Open `http://localhost:8000/bible-groups/topic.html?id=ot-01`:
- Title shows `1. Пролог`
- Reference line shows `Бытие 1:1–2:4`
- Text tab is active by default and shows the passage
- Clicking «Вопросы» / «Подготовка» switches active tab (panels empty — expected)
- localStorage persists active tab across reloads

- [ ] **Step 4: Commit**

```bash
git add bible-groups/topic.html bible-groups/assets/topic.js
git commit -m "$(cat <<'EOF'
Add topic view with main tabs and Synodal text rendering

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: Topic view — Questions tab (Mine / Hagenhans)

**Files:**
- Modify: `bible-groups/assets/topic.js` (fill `ensureQuestions`)

- [ ] **Step 1: Implement `ensureQuestions`**

Replace the empty stub:

```javascript
let questionsLoaded = false;
async function ensureQuestions() {
  if (questionsLoaded) return;
  questionsLoaded = true;
  const dir = topic.testament; // 'ot' or 'nt'
  const [mineMd, hagenMd] = await Promise.all([
    fetch(`${dir}/${topic.slug}-mine.md`).then(r => r.ok ? r.text() : '_Вопросы недоступны._'),
    fetch(`${dir}/${topic.slug}-hagen.md`).then(r => r.ok ? r.text() : '_Вопросы Гагенганса недоступны._'),
  ]);
  document.getElementById('questionsMine').innerHTML = marked.parse(mineMd);
  document.getElementById('questionsHagen').innerHTML = marked.parse(hagenMd);

  // Subtabs
  const subtabs = document.querySelectorAll('.subtab-btn');
  function activateSub(name) {
    subtabs.forEach(b => b.classList.toggle('active', b.dataset.subtab === name));
    document.getElementById('questionsMine').style.display = name === 'mine' ? '' : 'none';
    document.getElementById('questionsHagen').style.display = name === 'hagen' ? '' : 'none';
    localStorage.setItem('bibleGroupsQuestionsTab', name);
  }
  subtabs.forEach(b => b.addEventListener('click', () => activateSub(b.dataset.subtab)));
  activateSub(localStorage.getItem('bibleGroupsQuestionsTab') || 'mine');
}
```

Re-export it: replace the placeholder `async function ensureQuestions()` block above. Note `topic` is in closure scope.

- [ ] **Step 2: Manual verification**

Open `http://localhost:8000/bible-groups/topic.html?id=ot-01` → «Вопросы»:
- «Мои» active by default — shows 4 sections (Введение / Наблюдение / Понимание / Применение) with bullets
- Click «Гагенганс» — shows the 3 Hagenhans sections (or fallback for affected topics)
- Reload — last active subtab preserved
- Switch to topic `ot-43` and back — subtab state persists across topics

- [ ] **Step 3: Commit**

```bash
git add bible-groups/assets/topic.js
git commit -m "$(cat <<'EOF'
Render questions tab with Mine/Hagenhans sub-tabs

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: Topic view — Preparation tab (media + lightbox)

**Files:**
- Modify: `bible-groups/assets/topic.js` (fill `ensurePrep`)

- [ ] **Step 1: Implement `ensurePrep`**

```javascript
let prepLoaded = false;
function ensurePrep() {
  if (prepLoaded) return;
  prepLoaded = true;
  const target = document.getElementById('panel-prep');
  const { audio = [], image = [] } = topic.media || {};
  if (!audio.length && !image.length) {
    target.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:40px 0;">Подготовительные материалы пока не добавлены.</p>';
    return;
  }
  const base = `media/${topic.slug}/`;
  const parts = [];
  if (audio.length) {
    parts.push('<div class="media-block"><h3><i class="fa-solid fa-headphones"></i> Аудио</h3>');
    for (const name of audio) {
      parts.push(`<div class="media-item"><div style="font-size:13px;color:var(--text-muted);margin-bottom:4px;">${escapeHtml(name)}</div>`);
      parts.push(`<audio class="media-audio" controls preload="none" src="${base}${encodeURIComponent(name)}"></audio></div>`);
    }
    parts.push('</div>');
  }
  if (image.length) {
    parts.push('<div class="media-block"><h3><i class="fa-solid fa-image"></i> Картинки</h3>');
    for (const name of image) {
      parts.push(`<img class="media-image" loading="lazy" src="${base}${encodeURIComponent(name)}" alt="${escapeHtml(name)}">`);
    }
    parts.push('</div>');
  }
  target.innerHTML = parts.join('');

  // Lightbox wiring
  const lb = document.getElementById('lightbox');
  const lbImg = document.getElementById('lightboxImg');
  target.querySelectorAll('.media-image').forEach(img => {
    img.addEventListener('click', () => { lbImg.src = img.src; lb.classList.add('open'); });
  });
  lb.addEventListener('click', () => lb.classList.remove('open'));

  function escapeHtml(s){return s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
}
```

- [ ] **Step 2: Manual verification**

- Open `topic.html?id=ot-43` → «Подготовка» — 2 audio players, 3 images
- Click an image → fullscreen lightbox; click anywhere to close
- Audio plays from each player
- Open `topic.html?id=ot-01` → «Подготовка» shows the placeholder
- Direct-load `topic.html?id=ot-43` with `localStorage.setItem('bibleGroupsMainTab','prep')` then refresh — prep tab is preselected and content loads

- [ ] **Step 3: Commit**

```bash
git add bible-groups/assets/topic.js
git commit -m "$(cat <<'EOF'
Add preparation tab with audio, images, and lightbox

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: Update root hub and project documentation

**Files:**
- Modify: `index.html` (add third card)
- Modify: `CLAUDE.md` (add a section for the new course)

- [ ] **Step 1: Edit root `index.html`**

Inside the `.cards` grid (after the `7-shagov/` card), add:

```html
<a class="card" href="bible-groups/">
  <div class="card-icon"><i class="fa-solid fa-users"></i></div>
  <div class="card-title">Изучение Библии в малых группах</div>
  <div class="card-desc">102 темы &ndash; Ветхий и Новый Заветы</div>
</a>
```

If three cards make the 2-column grid awkward, leave it — the existing media query collapses to one column at ≤650px, and on desktop three cards in a 2-col grid simply wrap. Acceptable.

- [ ] **Step 2: Update `CLAUDE.md`**

Add a third course section (after «Курс 2: Семь шагов…» before «Bible Quotes»):

```markdown
## Курс 3: Изучение Библии в малых группах (bible-groups/)

102 темы для разборов в малых группах: 52 ВЗ + 50 НЗ. Источники: PDF-сборники
вопросов автора + справочник Эдуарда Гагенганса (Bible Mission, 2024).

### Структура
- `bible-groups/index.html` &ndash; хаб курса (ВЗ / НЗ)
- `bible-groups/{ot,nt}.html` &ndash; списки тем с поиском
- `bible-groups/topic.html?id={ot|nt}-NN` &ndash; вкладки: Текст / Вопросы (Мои + Гагенганс) / Подготовка
- `bible-groups/topics.json` &ndash; метаданные всех тем
- `bible-groups/{ot,nt}/NN-slug-{mine,hagen}.md` &ndash; вопросы
- `bible-groups/media/NN-slug/` &ndash; аудио и картинки
- `bible-groups/assets/` &ndash; общие CSS/JS

### Регенерация
- `python3 scripts/extract_bible_groups.py` &ndash; повторная сборка вопросов из PDF
- `python3 scripts/scan_media.py` &ndash; обновить блоки `media` в topics.json по содержимому папок
```

- [ ] **Step 3: Manual verification end-to-end**

Run through the full checklist from the spec (section «Тестирование»):

1. `http://localhost:8000/` — three cards visible, third leads to bible-groups
2. `bible-groups/` — hub with OT/NT cards
3. `bible-groups/ot.html` — 52 topics, sections, search works
4. `bible-groups/nt.html` — 50 topics, sections, search works
5. `topic.html?id=ot-01` — text, both question sets, prep placeholder
6. `topic.html?id=ot-43` — prep tab shows 2 audio + 3 images, icons appear in list
7. Theme toggle works on all new pages
8. Mobile width: layouts hold up

Fix any visual or functional issues found.

- [ ] **Step 4: Commit**

```bash
git add index.html CLAUDE.md
git commit -m "$(cat <<'EOF'
Link bible-groups course from root hub and document in CLAUDE.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Final Verification Checklist

Run after the last commit, on the local server:

- [ ] Root hub shows three course cards; en dashes render
- [ ] `bible-groups/index.html` loads, both OT/NT cards link correctly
- [ ] `bible-groups/ot.html` shows exactly 52 topics in correct sections
- [ ] `bible-groups/nt.html` shows exactly 50 topics in correct sections
- [ ] Search by number (`43`), title (substring), reference (substring) filters live
- [ ] Topic 43 row shows 🎧 and 🖼 icons
- [ ] `topic.html?id=ot-01` text tab shows Genesis 1:1–2:4 in full
- [ ] Questions tab: «Мои» shows 4 blocks; «Гагенганс» shows 3 (or fallback)
- [ ] `topic.html?id=ot-43` prep tab: 2 audio + 3 images; lightbox works
- [ ] Active main tab and questions sub-tab survive page reloads via localStorage
- [ ] Dark/light toggle works on every new page
- [ ] At ≤600px width, no layout breakage
- [ ] No console errors on any page
- [ ] `topics.json` has 102 entries, each with non-null `refStructured`

If any item fails: open a follow-up task, fix it, commit, re-verify.

---

## Notes for the implementer

- Frequent commits are required between tasks; do not batch multiple tasks into one commit.
- Source PDFs in `groups/row_material/` are **inputs**, not outputs. Don't modify them; don't delete the folder.
- If you discover a Bible reference the parser can't handle (warning in Task 3), prefer fixing `BOOK_MAP` over hardcoding around it.
- Hagenhans parsing is heuristic; some topics may land in fallback. That's acceptable — the `.md` files are editable and the system still functions. The user can curate them later.
- Do not introduce a build step, bundler, or framework. This project is intentionally static.
