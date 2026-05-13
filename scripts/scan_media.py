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


def collect(folder: Path) -> dict:
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
