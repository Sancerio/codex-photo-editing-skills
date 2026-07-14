#!/usr/bin/env python3
"""Conservatively upscale a photograph without generative face restoration."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter, ImageStat


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out-png", required=True, type=Path)
    parser.add_argument("--out-jpg", type=Path)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--scale", type=float)
    parser.add_argument("--no-sharpen", action="store_true")
    parser.add_argument("--sharpen-radius", type=float, default=0.9)
    parser.add_argument("--sharpen-percent", type=int, default=55)
    parser.add_argument("--sharpen-threshold", type=int, default=4)
    parser.add_argument("--jpeg-quality", type=int, default=96)
    parser.add_argument("--allow-aspect-change", action="store_true")
    parser.add_argument("--report", type=Path)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def target_size(args: argparse.Namespace, source: Image.Image) -> tuple[int, int]:
    explicit = args.width is not None or args.height is not None
    if args.scale is not None and explicit:
        raise SystemExit("use --scale or --width/--height, not both")
    if args.scale is not None:
        if args.scale <= 0:
            raise SystemExit("--scale must be positive")
        return round(source.width * args.scale), round(source.height * args.scale)
    if args.width is None or args.height is None:
        raise SystemExit("provide --scale or both --width and --height")
    if args.width <= 0 or args.height <= 0:
        raise SystemExit("target dimensions must be positive")
    return args.width, args.height


def roundtrip_psnr(source: Image.Image, output: Image.Image) -> tuple[float, float]:
    roundtrip = output.resize(source.size, Image.Resampling.LANCZOS)
    difference = ImageChops.difference(source, roundtrip)
    rms = ImageStat.Stat(difference).rms
    mse = sum(value * value for value in rms) / len(rms)
    psnr = math.inf if mse == 0 else 20 * math.log10(255.0 / math.sqrt(mse))
    return mse, psnr


def main() -> None:
    args = parse_args()
    source = Image.open(args.input).convert("RGB")
    size = target_size(args, source)
    source_ratio = source.width / source.height
    target_ratio = size[0] / size[1]
    if not args.allow_aspect_change and abs(source_ratio - target_ratio) > 0.0005:
        raise SystemExit("target aspect ratio differs; pass --allow-aspect-change to override")

    output = source.resize(size, Image.Resampling.LANCZOS)
    method = "Lanczos resampling"
    if not args.no_sharpen:
        output = output.filter(
            ImageFilter.UnsharpMask(
                radius=args.sharpen_radius,
                percent=args.sharpen_percent,
                threshold=args.sharpen_threshold,
            )
        )
        method += " with restrained unsharp masking"

    args.out_png.parent.mkdir(parents=True, exist_ok=True)
    output.save(args.out_png, optimize=True)
    if args.out_jpg:
        args.out_jpg.parent.mkdir(parents=True, exist_ok=True)
        output.save(
            args.out_jpg,
            quality=args.jpeg_quality,
            subsampling=0,
            optimize=True,
        )

    mse, psnr = roundtrip_psnr(source, output)
    report = {
        "input": str(args.input),
        "input_sha256": sha256(args.input),
        "source_dimensions": [source.width, source.height],
        "output_dimensions": [output.width, output.height],
        "scale_factors": [output.width / source.width, output.height / source.height],
        "method": method,
        "generative_face_restoration": False,
        "aspect_ratio_changed": abs(source_ratio - target_ratio) > 0.0005,
        "roundtrip_mse": mse,
        "roundtrip_psnr_db": psnr,
        "outputs": {
            "png": {"path": str(args.out_png), "sha256": sha256(args.out_png)},
            "jpg": (
                {"path": str(args.out_jpg), "sha256": sha256(args.out_jpg)}
                if args.out_jpg
                else None
            ),
        },
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
