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
    return s.replace(" -- ", " – ").replace("--", "–").strip()


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


if __name__ == "__main__":
    main()
