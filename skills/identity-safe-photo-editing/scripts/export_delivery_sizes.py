#!/usr/bin/env python3
"""Create byte-identical full-size and deterministic web-size photo deliveries."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageOps


WEB_FOLDER = "EDITED WEB SIZE"
FULL_FOLDER = "EDITED FULL SIZE"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", nargs="+", required=True, type=Path)
    parser.add_argument(
        "--name",
        nargs="+",
        help="delivery JPEG names corresponding one-for-one with --input",
    )
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--long-edge", type=int, default=2500)
    parser.add_argument("--jpeg-quality", type=int, default=90)
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dimensions(path: Path) -> list[int]:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image)
        return [image.width, image.height]


def web_size(width: int, height: int, long_edge: int) -> tuple[int, int]:
    scale = long_edge / max(width, height)
    return max(1, round(width * scale)), max(1, round(height * scale))


def export_one(
    source: Path,
    delivery_name: str,
    web_dir: Path,
    full_dir: Path,
    args: argparse.Namespace,
) -> dict:
    if not source.is_file():
        raise SystemExit(f"input does not exist: {source}")
    if source.suffix.lower() not in {".jpg", ".jpeg"}:
        raise SystemExit(f"approved full-size master must be JPEG for byte-identical delivery: {source}")

    name_path = Path(delivery_name)
    if name_path.name != delivery_name or name_path.suffix.lower() not in {".jpg", ".jpeg"}:
        raise SystemExit(f"delivery name must be a safe JPEG basename: {delivery_name}")
    full_path = full_dir / delivery_name
    web_path = web_dir / delivery_name
    if source.resolve() == full_path.resolve():
        raise SystemExit(f"input cannot already be the destination: {source}")

    shutil.copy2(source, full_path)
    input_hash = sha256(source)
    full_hash = sha256(full_path)
    if input_hash != full_hash:
        raise SystemExit(f"full-size copy verification failed: {source}")

    with Image.open(source) as opened:
        icc_profile = opened.info.get("icc_profile")
        exif = opened.getexif()
        image = ImageOps.exif_transpose(opened).convert("RGB")
        target = web_size(image.width, image.height, args.long_edge)
        web = image.resize(target, Image.Resampling.LANCZOS)
        save_args: dict[str, object] = {
            "format": "JPEG",
            "quality": args.jpeg_quality,
            "optimize": True,
        }
        if icc_profile:
            save_args["icc_profile"] = icc_profile
        if exif:
            exif[274] = 1
            save_args["exif"] = exif.tobytes()
        web.save(web_path, **save_args)

    return {
        "input": str(source),
        "delivery_name": delivery_name,
        "input_dimensions": dimensions(source),
        "input_size_bytes": source.stat().st_size,
        "input_sha256": input_hash,
        "full_size": {
            "path": str(full_path),
            "dimensions": dimensions(full_path),
            "size_bytes": full_path.stat().st_size,
            "sha256": full_hash,
            "byte_identical_to_input": True,
        },
        "web_size": {
            "path": str(web_path),
            "dimensions": dimensions(web_path),
            "size_bytes": web_path.stat().st_size,
            "sha256": sha256(web_path),
            "long_edge": args.long_edge,
            "method": "Lanczos resize; no generative enhancement or face restoration",
        },
    }


def main() -> None:
    args = parse_args()
    if args.long_edge <= 0:
        raise SystemExit("--long-edge must be positive")
    if not 1 <= args.jpeg_quality <= 100:
        raise SystemExit("--jpeg-quality must be between 1 and 100")
    names = args.name or [f"{source.stem}.jpg" for source in args.input]
    if len(names) != len(args.input):
        raise SystemExit("--name must provide exactly one delivery name per --input")
    if len(set(names)) != len(names):
        raise SystemExit("delivery names must be unique")

    web_dir = args.output_root / WEB_FOLDER
    full_dir = args.output_root / FULL_FOLDER
    web_dir.mkdir(parents=True, exist_ok=True)
    full_dir.mkdir(parents=True, exist_ok=True)

    records = [
        export_one(source, name, web_dir, full_dir, args)
        for source, name in zip(args.input, names, strict=True)
    ]
    report = {
        "convention": {
            "web_folder": WEB_FOLDER,
            "full_folder": FULL_FOLDER,
            "web_long_edge": args.long_edge,
            "jpeg_quality": args.jpeg_quality,
        },
        "files": records,
    }
    report_path = args.report or args.output_root / "export-verification.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
