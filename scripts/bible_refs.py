"""Parse Russian Bible references into structured form aligned with data/synodal.json abbrevs."""

import re

BOOK_MAP = {
    # Ветхий Завет
    "Бытие": "gn",
    "Исход": "ex",
    "Левит": "lv",
    "Числа": "nm",
    "Второзаконие": "dt",
    "Иисус Навин": "js",
    "Книга Судей": "jud",
    "Судей": "jud",
    "Руфь": "rt",
    "1 Царств": "1sm",
    "2 Царств": "2sm",
    "3 Царств": "1kgs",
    "4 Царств": "2kgs",
    "1 Паралипоменон": "1ch",
    "2 Паралипоменон": "2ch",
    "Ездра": "ezr",
    "Неемия": "ne",
    "Есфирь": "et",
    "Иов": "job",
    "Псалтирь": "ps",
    "Притчи": "prv",
    "Екклесиаст": "ec",
    "Песнь Песней": "so",
    "Исаия": "is",
    "Иеремия": "jr",
    "Плач Иеремии": "lm",
    "Иезекииль": "ez",
    "Даниил": "dn",
    "Осия": "ho",
    "Иоиль": "jl",
    "Амос": "am",
    "Авдий": "ob",
    "Иона": "jn",
    "Михей": "mi",
    "Наум": "na",
    "Аввакум": "hk",
    "Софония": "zp",
    "Аггей": "hg",
    "Захария": "zc",
    "Малахия": "ml",
    # Новый Завет
    "Матфея": "mt",
    "Марка": "mk",
    "Луки": "lk",
    "Иоанна": "jo",
    "Деяния": "act",
    "Римлянам": "rm",
    "1 Коринфянам": "1co",
    "2 Коринфянам": "2co",
    "Галатам": "gl",
    "Ефесянам": "eph",
    "Филиппийцам": "ph",
    "Колоссянам": "cl",
    "1 Фессалоникийцам": "1ts",
    "2 Фессалоникийцам": "2ts",
    "1 Тимофею": "1tm",
    "2 Тимофею": "2tm",
    "Титу": "tt",
    "Филимону": "phm",
    "Евреям": "hb",
    "Иакова": "jm",
    "1 Петра": "1pe",
    "2 Петра": "2pe",
    "1 Иоанна": "1jo",
    "2 Иоанна": "2jo",
    "3 Иоанна": "3jo",
    "Иуды": "jd",
    "Откровение": "re",
}


class RefParseError(ValueError):
    pass


_DASHES = "–—−-"
_DASH_CLASS = f"[{_DASHES}]"


def _sorted_book_names():
    return sorted(BOOK_MAP.keys(), key=len, reverse=True)


def _parse_single(text: str, last_book):
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

    rest = re.sub(_DASH_CLASS, "-", rest)
    m = re.match(r"^\s*(\d+)(?::(\d+))?(?:\s*-\s*(\d+)(?::(\d+))?)?\s*$", rest)
    if not m:
        raise RefParseError(f"Cannot parse chapter/verse part: {rest!r} (full: {text!r})")
    ch1 = int(m.group(1))
    v1 = int(m.group(2)) if m.group(2) else 1
    if m.group(3):
        if m.group(4):
            ch2 = int(m.group(3))
            v2 = int(m.group(4))
        elif m.group(2):
            # "ch:v1-v2" within same chapter
            ch2 = ch1
            v2 = int(m.group(3))
        else:
            ch2 = int(m.group(3))
            v2 = -1
    else:
        ch2 = ch1
        if m.group(2):
            v2 = v1
        else:
            v2 = -1
    return {"book": book_abbrev, "from": [ch1, v1], "to": [ch2, v2]}


def parse_reference(text: str) -> dict:
    """Return {'passages': [{'book': abbrev, 'from': [ch, v], 'to': [ch, v]}, ...]}.
    Always a list; missing 'from' verse defaults to 1; missing 'to' verse uses sentinel -1 (last verse)."""
    segments = [s for s in re.split(r";", text) if s.strip()]
    passages = []
    last_book = None
    for seg in segments:
        p = _parse_single(seg, last_book)
        passages.append(p)
        last_book = p["book"]
    return {"passages": passages}
