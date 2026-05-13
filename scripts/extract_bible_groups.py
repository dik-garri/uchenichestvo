"""One-off extractor: read source PDFs into bible-groups/{ot,nt}/*.md and topics.json.

Idempotent — safe to re-run; overwrites generated files. Source PDFs in groups/row_material/.
"""

import json
import re
import sys
from pathlib import Path

import pdfplumber

from bible_refs import parse_reference

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "groups" / "row_material"
OUT = ROOT / "bible-groups"

OT_PDF = SRC / "Вопросы_Ветхий_Завет_1-52.pdf"
NT_PDF = SRC / "Вопросы_Новый_Завет_51-100.pdf"
HAGEN_PDF = SRC / "Изучение_Библии_в_малых_группах_для_лидеров.pdf"
HAGEN_START_PAGE = 10  # 0-indexed; page 11 in viewer — first topic "a. Пролог"
HAGEN_BLOCK_TITLES = ["☕ Введение", "📖 Наблюдение и понимание", "❤️ Применение"]
HAGEN_TITLE_RE = re.compile(r"^([a-zа-я])\.\s+(.+?)\s*$", re.IGNORECASE)
HAGEN_BLOCK_GAP = 28  # vertical gap (in pts) between bullets that signals a block boundary

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
    return s.replace(" -- ", " – ").replace("--", "–").replace("—", "–").strip()


def _extract_topic_from_text(page_text: str):
    """Return (topic_dict_or_None, section_or_empty)."""
    lines = [ln.rstrip() for ln in page_text.splitlines() if ln.strip()]
    section = ""
    idx = 0
    if lines and SECTION_RE.match(lines[0]):
        section = lines[0].strip()
        idx = 1
    if idx >= len(lines):
        return None, section
    m = TITLE_RE.match(lines[idx])
    if not m:
        return None, section
    number = int(m.group(1))
    title = _clean_line(m.group(2))
    reference = _clean_line(m.group(3))

    blocks = {b: [] for b in BLOCK_NAMES}
    current = None
    buf = []

    def flush():
        nonlocal buf
        if current and buf:
            text = _clean_line(" ".join(buf))
            blocks[current].append(text)
        buf = []

    for ln in lines[idx + 1:]:
        upper = ln.strip()
        if upper in BLOCK_NAMES:
            flush()
            current = upper
            continue
        stripped = ln.lstrip()
        if stripped.startswith(("—", "–", "-", "•")):
            flush()
            buf = [stripped.lstrip(" —–-•").strip()]
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


def extract_questions_pdf(pdf_path: Path, testament: str):
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
        body.append("")
    path.write_text("\n".join(body).rstrip() + "\n", encoding="utf-8")
    return slug


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


def _extract_hagen_page(page):
    """Parse one Hagenhans page using char-level bbox info.

    Returns dict {"title", "reference", "groups": [[bullet_str, ...], ...], "fallback": bool}
    or None if the page doesn't look like a topic page.
    """
    chars = page.chars
    rows = {}
    for c in chars:
        k = round(c["top"], 0)
        rows.setdefault(k, []).append(c)
    lines = []
    for k in sorted(rows):
        txt = "".join(c["text"] for c in sorted(rows[k], key=lambda c: c["x0"])).rstrip()
        if txt.strip():
            lines.append((k, txt))
    # Drop trailing page number line
    if lines and lines[-1][1].strip().isdigit():
        lines = lines[:-1]
    if not lines:
        return None

    # Optional Roman section header on first line
    idx = 0
    if SECTION_RE.match(lines[0][1].strip()):
        idx = 1
    if idx >= len(lines):
        return None
    title_line = lines[idx][1].strip()
    m = HAGEN_TITLE_RE.match(title_line)
    if not m:
        return None
    raw = m.group(2).strip()
    # Reference detection: trailing parens, or trailing "Book Ch:Vs[ ... ]"
    pm = re.match(r"^(.+?)\s*\((.+?)\)\s*$", raw)
    if pm:
        title = _clean_line(pm.group(1))
        reference = _clean_line(pm.group(2))
    else:
        # Try splitting at first occurrence of a book/number reference pattern
        rm = re.search(r"\s+((?:\d\s+)?[А-ЯA-Z][а-яa-zё]+(?:\s+Навин)?\s+\d.*)$", raw)
        if rm:
            title = _clean_line(raw[: rm.start()])
            reference = _clean_line(rm.group(1))
        else:
            title = _clean_line(raw)
            reference = ""

    # Group bullets using vertical-gap heuristic
    bullet_lines = []
    first_bullet_idx = next((i for i, (_, t) in enumerate(lines) if t.lstrip().startswith("•")), None)
    if first_bullet_idx is None:
        return {"title": title, "reference": reference, "groups": [], "fallback": True}

    blocks = []  # list of list of bullets (each bullet = str)
    cur_block = []
    cur_bullet_lines = None  # list of (top, text)

    def finalize_bullet():
        nonlocal cur_bullet_lines
        if cur_bullet_lines is None:
            return None
        text = " ".join(t for _, t in cur_bullet_lines).strip()
        # strip leading bullet marker variations
        text = re.sub(r"^[•\-–—]\s*", "", text)
        cur_bullet_lines = None
        return _clean_line(text)

    for top, t in lines[first_bullet_idx:]:
        stripped = t.lstrip()
        is_bullet = stripped.startswith("•")
        if is_bullet:
            if cur_bullet_lines is not None:
                # gap from last wrap line top of prev bullet
                gap = top - cur_bullet_lines[-1][0]
                bullet_text = finalize_bullet()
                if bullet_text:
                    cur_block.append(bullet_text)
                if gap > HAGEN_BLOCK_GAP:
                    if cur_block:
                        blocks.append(cur_block)
                        cur_block = []
            cur_bullet_lines = [(top, t)]
        else:
            if cur_bullet_lines is not None:
                cur_bullet_lines.append((top, t))
            # else: stray line between title and first bullet — ignore
    bullet_text = finalize_bullet()
    if bullet_text:
        cur_block.append(bullet_text)
    if cur_block:
        blocks.append(cur_block)

    fallback = len(blocks) != 3
    return {"title": title, "reference": reference, "groups": blocks, "fallback": fallback}


def extract_hagen_pdf(pdf_path: Path, start_page: int):
    topics = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_no, page in enumerate(pdf.pages[start_page:], start=start_page + 1):
            topic = _extract_hagen_page(page)
            if topic is None:
                continue
            topics.append(topic)
    return topics


def write_hagen_md(slug: str, topic: dict, out_dir: Path) -> None:
    path = out_dir / f"{slug}-hagen.md"
    parts = []
    if topic["fallback"] or len(topic["groups"]) != 3:
        parts.append("## Вопросы\n")
        all_bullets = [b for grp in topic["groups"] for b in grp]
        for q in all_bullets:
            parts.append(f"- {q}")
        parts.append("")
    else:
        for heading, items in zip(HAGEN_BLOCK_TITLES, topic["groups"]):
            parts.append(f"## {heading}\n")
            for q in items:
                parts.append(f"- {q}")
            parts.append("")
    path.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")


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

    all_topics.sort(key=lambda r: (0 if r["testament"] == "ot" else 1, r["number"]))
    (OUT / "topics.json").write_text(json.dumps(all_topics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote topics.json ({len(all_topics)} topics)")

    print(f"Reading {HAGEN_PDF.name} (Hagenhans)...")
    hagen_topics = extract_hagen_pdf(HAGEN_PDF, start_page=HAGEN_START_PAGE)
    print(f"  parsed {len(hagen_topics)} Hagenhans topics")

    fallbacks = []
    written = 0
    for i, h in enumerate(hagen_topics):
        if i >= len(all_topics):
            print(f"  WARN: extra Hagenhans topic at index {i}, ignoring", file=sys.stderr)
            break
        rec = all_topics[i]
        out_dir = OUT / rec["testament"]
        write_hagen_md(rec["slug"], h, out_dir)
        written += 1
        if h["fallback"]:
            fallbacks.append(rec["id"])
    if len(hagen_topics) < len(all_topics):
        missing = [r["id"] for r in all_topics[len(hagen_topics):]]
        print(f"  WARN: {len(missing)} topics missing Hagenhans questions: {missing}", file=sys.stderr)
    if fallbacks:
        print(f"  WARN: {len(fallbacks)} Hagenhans topics used fallback layout: {fallbacks}", file=sys.stderr)
    print(f"  wrote {written} Hagenhans files")


if __name__ == "__main__":
    main()
