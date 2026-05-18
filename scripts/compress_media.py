"""Compress audio and images in bible-groups/media/ for the static site.

Audio: m4a/mp3/wav  → mono AAC 64 kbps in .m4a (re-encoded, same name)
Images: png/jpg/jpeg → WebP quality 82, max width 1600 px (renamed to .webp)

Originals are moved to bible-groups/media/_originals/{slug}/ (gitignored) before
replacement, so the script is safe to re-run and the lossless source stays
recoverable. Already-compressed files (matching target codec/extension and
within size threshold) are skipped, so the script is idempotent.

After running, execute `python3 scripts/scan_media.py` to refresh
bible-groups/topics.json with the new filenames.

Requires ffmpeg in PATH (audio) and Pillow (images: `pip install --user Pillow`).

Usage:
    python3 scripts/compress_media.py                # process every slug
    python3 scripts/compress_media.py --dry-run      # show what would be done
    python3 scripts/compress_media.py --slug 43-prizvanie-ieremii  # one slug
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MEDIA = ROOT / "bible-groups" / "media"
BACKUP = MEDIA / "_originals"

AUDIO_EXT = {".m4a", ".mp3", ".wav", ".ogg"}
IMAGE_EXT = {".png", ".jpg", ".jpeg"}

AUDIO_BITRATE = "64k"
IMAGE_QUALITY = 82
IMAGE_MAX_WIDTH = 1600


def human_size(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if num_bytes < 1024:
            return f"{num_bytes:.1f}{unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f}TB"


def run_ffmpeg(args: list[str]) -> None:
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-hide_banner", *args]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {' '.join(cmd)}\n{res.stderr}")


def already_compressed_audio(path: Path) -> bool:
    """Heuristic: file is small enough (≤ ~80kbps avg) → assume already compressed."""
    if path.suffix.lower() != ".m4a":
        return False
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=bit_rate,channels",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True, check=True,
        )
        lines = [ln.strip() for ln in probe.stdout.splitlines() if ln.strip()]
        if len(lines) < 2:
            return False
        channels = int(lines[0])
        bitrate = int(lines[1])
        return channels == 1 and bitrate <= 80_000
    except Exception:
        return False


def compress_audio(src: Path, backup_dir: Path, dry_run: bool) -> tuple[int, int] | None:
    """Return (orig_size, new_size) on success, None if skipped."""
    if already_compressed_audio(src):
        print(f"  skip  audio  {src.name} (already mono ≤80k)")
        return None
    orig_size = src.stat().st_size
    if dry_run:
        print(f"  AUDIO {src.name}  {human_size(orig_size)} → ~{human_size(orig_size // 6)} (est)")
        return None

    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / src.name
    if not backup_path.exists():
        shutil.copy2(src, backup_path)

    tmp = src.with_suffix(src.suffix + ".tmp.m4a")
    run_ffmpeg([
        "-i", str(src),
        "-ac", "1",
        "-c:a", "aac",
        "-b:a", AUDIO_BITRATE,
        "-movflags", "+faststart",
        str(tmp),
    ])
    final = src.with_suffix(".m4a")
    if src != final and src.exists():
        src.unlink()
    tmp.replace(final)
    new_size = final.stat().st_size
    print(f"  audio  {src.name} → {final.name}  {human_size(orig_size)} → {human_size(new_size)}  ({new_size * 100 // orig_size}%)")
    return orig_size, new_size


def compress_image(src: Path, backup_dir: Path, dry_run: bool) -> tuple[int, int] | None:
    if src.suffix.lower() == ".webp":
        return None  # already in target format
    orig_size = src.stat().st_size
    if dry_run:
        print(f"  IMAGE {src.name}  {human_size(orig_size)} → ~{human_size(orig_size // 8)} (est)")
        return None

    try:
        from PIL import Image
    except ImportError:
        raise RuntimeError("Pillow not installed. Run: python3 -m pip install --user Pillow")

    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / src.name
    if not backup_path.exists():
        shutil.copy2(src, backup_path)

    final = src.with_suffix(".webp")
    with Image.open(src) as im:
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
        w, h = im.size
        if w > IMAGE_MAX_WIDTH:
            new_h = round(h * IMAGE_MAX_WIDTH / w)
            im = im.resize((IMAGE_MAX_WIDTH, new_h), Image.LANCZOS)
        im.save(final, format="WEBP", quality=IMAGE_QUALITY, method=6)

    if src.exists() and src != final:
        src.unlink()
    new_size = final.stat().st_size
    print(f"  image  {src.name} → {final.name}  {human_size(orig_size)} → {human_size(new_size)}  ({new_size * 100 // orig_size}%)")
    return orig_size, new_size


def process_slug(slug_dir: Path, dry_run: bool) -> tuple[int, int]:
    print(f"\n→ {slug_dir.name}")
    backup_dir = BACKUP / slug_dir.name
    saved_before = 0
    saved_after = 0
    for entry in sorted(slug_dir.iterdir()):
        if not entry.is_file():
            continue
        ext = entry.suffix.lower()
        if ext in AUDIO_EXT:
            result = compress_audio(entry, backup_dir, dry_run)
        elif ext in IMAGE_EXT:
            result = compress_image(entry, backup_dir, dry_run)
        else:
            continue
        if result is not None:
            saved_before += result[0]
            saved_after += result[1]
    return saved_before, saved_after


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print plan without modifying files")
    parser.add_argument("--slug", help="Process only this slug (folder name under bible-groups/media/)")
    args = parser.parse_args()

    if not shutil.which("ffmpeg"):
        print("ERROR: ffmpeg not found in PATH. Install it (e.g. `brew install ffmpeg`).", file=sys.stderr)
        return 1
    if not MEDIA.is_dir():
        print(f"ERROR: media root not found: {MEDIA}", file=sys.stderr)
        return 1

    slugs = []
    if args.slug:
        target = MEDIA / args.slug
        if not target.is_dir():
            print(f"ERROR: slug not found: {target}", file=sys.stderr)
            return 1
        slugs = [target]
    else:
        slugs = sorted(d for d in MEDIA.iterdir() if d.is_dir() and not d.name.startswith("_"))

    total_before = total_after = 0
    for slug_dir in slugs:
        before, after = process_slug(slug_dir, args.dry_run)
        total_before += before
        total_after += after

    if total_before:
        ratio = total_after * 100 // total_before
        print(f"\nTotal: {human_size(total_before)} → {human_size(total_after)}  ({ratio}%)")
        print(f"Originals backed up to: {BACKUP}")
        print("Next step: run `python3 scripts/scan_media.py` to refresh topics.json.")
    elif args.dry_run:
        print("\n(dry run — no files modified)")
    else:
        print("\nNothing to compress.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
