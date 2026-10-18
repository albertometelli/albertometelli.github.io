#!/usr/bin/env python3
"""Download and optimize every local site asset from one command.

Team portrait sources and destinations live in ``data/team.json``, the same
manifest used to render ``team.html``. Pillow is used to normalize portraits
to compact square WebP files suitable for the displayed avatar size.
"""
from __future__ import annotations

import argparse
from io import BytesIO
import json
from pathlib import Path
import sys
import urllib.error
import urllib.request

from PIL import Image, ImageOps, UnidentifiedImageError


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = "https://raw.githubusercontent.com/albertometelli/albertometelli.github.io/master"
SITE = "https://albertometelli.github.io"
MAX_BYTES = 20_000_000

# Historical assets that are not represented by the team manifest.
ASSETS = {
    "images/DSC_15402.jpeg": "assets/img/portrait.jpeg",
    "files/cv.pdf": "assets/cv.pdf",
    "files/theses0626.pdf": "assets/theses0626.pdf",
    "images/all_logos.jpeg": "assets/all_logos.jpeg",
}


def download(urls: list[str]) -> tuple[bytes, str]:
    errors = []
    for url in urls:
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "MetelliStaticSiteAssetImport/2.0"})
            with urllib.request.urlopen(request, timeout=25) as response:
                data = response.read(MAX_BYTES + 1)
            if not data or len(data) > MAX_BYTES:
                raise ValueError("empty or oversized response")
            return data, url
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError("; ".join(errors))


def atomic_write(destination: Path, data: bytes) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(destination)


def import_asset(source: str, target: str) -> None:
    data, used_url = download([f"{ORIGINAL}/{source}", f"{SITE}/{source}"])
    if target.lower().endswith(".pdf") and not data.startswith(b"%PDF"):
        raise RuntimeError(f"invalid PDF returned by {used_url}")
    if target.lower().endswith((".jpg", ".jpeg")) and not data.startswith(b"\xff\xd8\xff"):
        raise RuntimeError(f"invalid JPEG returned by {used_url}")
    atomic_write(ROOT / target, data)


def import_portrait(url: str, target: str) -> None:
    data, used_url = download([url])
    try:
        with Image.open(BytesIO(data)) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            image = ImageOps.fit(image, (384, 384), method=Image.Resampling.LANCZOS)
            output = BytesIO()
            image.save(output, format="WEBP", quality=82, method=6)
    except (UnidentifiedImageError, OSError) as exc:
        raise RuntimeError(f"invalid image returned by {used_url}: {exc}") from exc
    atomic_write(ROOT / target, output.getvalue())


def team_members() -> list[dict]:
    model = json.loads((ROOT / "data" / "team.json").read_text(encoding="utf-8"))
    return [member for section in model["sections"] for member in section["members"]]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Overwrite assets that already exist")
    args = parser.parse_args()
    failures = []

    for source, target in ASSETS.items():
        destination = ROOT / target
        if destination.exists() and not args.force:
            print(f"Already exists: {target}")
            continue
        try:
            import_asset(source, target)
            print(f"Imported: {target}")
        except RuntimeError as exc:
            failures.append(source)
            print(f"WARNING: {source}: {exc}", file=sys.stderr)

    for member in team_members():
        target = member["photo"]
        destination = ROOT / target
        if destination.exists() and not args.force:
            print(f"Already exists: {target}")
            continue
        try:
            import_portrait(member["photo_source"], target)
            print(f"Imported and optimized: {target}")
        except RuntimeError as exc:
            failures.append(member["photo_source"])
            print(f"WARNING: {member['name']}: {exc}", file=sys.stderr)

    if failures:
        print(f"Failed to update {len(failures)} asset(s).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
