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
    # Determine the correct abbrev for Иоанна via data/synodal.json — may be "jn" or another value
    assert r["passages"][0]["from"] == [3, 1] and r["passages"][0]["to"] == [3, -1]
    assert r["passages"][1] == {"book": "eph", "from": [2, 1], "to": [2, -1]}, r

def test_verse_range_within_chapter():
    r = parse_reference("Бытие 2:5-25")
    assert r == {"passages": [{"book": "gn", "from": [2, 5], "to": [2, 25]}]}, r

def test_numbered_book():
    r = parse_reference("1 Царств 8")
    # Determine correct abbrev (likely "1sm")
    p = r["passages"][0]
    assert p["from"] == [8, 1] and p["to"] == [8, -1]
    assert p["book"] in {"1sm", "1sam"}, p

if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ok  {name}")
    print("All bible_refs tests passed.")
