#!/usr/bin/env python3
"""Composite a localized AI edit while proving protected regions stay exact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--original", required=True)
    parser.add_argument("--edited", required=True)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--mask-out")
    parser.add_argument("--report-out")
    return parser.parse_args()


def point(pair: list[float], width: int, height: int) -> tuple[int, int]:
    return round(pair[0] * width), round(pair[1] * height)


def box(values: list[float], width: int, height: int) -> tuple[int, int, int, int]:
    if len(values) != 4:
        raise ValueError("box must contain [x1, y1, x2, y2]")
    x1, y1 = point(values[:2], width, height)
    x2, y2 = point(values[2:], width, height)
    return x1, y1, x2, y2


def draw_shapes(mask: Image.Image, shapes: list[dict], width: int, height: int) -> None:
    draw = ImageDraw.Draw(mask)
    for shape in shapes:
        kind = shape.get("type")
        if kind == "polygon":
            points = [point(p, width, height) for p in shape["points"]]
            if len(points) < 3:
                raise ValueError("polygon requires at least three points")
            draw.polygon(points, fill=255)
        elif kind == "rectangle":
            draw.rectangle(box(shape["box"], width, height), fill=255)
        elif kind == "ellipse":
            draw.ellipse(box(shape["box"], width, height), fill=255)
        else:
            raise ValueError(f"unsupported shape type: {kind!r}")


def region_identical(original: Image.Image, output: Image.Image, region: tuple[int, int, int, int]) -> bool:
    return original.crop(region).tobytes() == output.crop(region).tobytes()


def main() -> None:
    args = parse_args()
    spec = json.loads(Path(args.spec).read_text())
    original = Image.open(args.original).convert("RGB")
    edited = Image.open(args.edited).convert("RGB").resize(original.size, Image.Resampling.LANCZOS)
    width, height = original.size

    mask = Image.new("L", original.size, 0)
    draw_shapes(mask, spec.get("edit_shapes", []), width, height)
    feather = int(spec.get("feather_px", 0))
    if feather > 0:
        mask = mask.filter(ImageFilter.GaussianBlur(radius=feather))

    locks = []
    for item in spec.get("lock_regions", []):
        region = box(item["box"], width, height)
        extrema = mask.crop(region).getextrema()
        if extrema[1] != 0:
            raise SystemExit(
                f"edit mask overlaps locked region {item['name']!r}; tighten the mask before compositing"
            )
        locks.append((item["name"], region))

    output = Image.composite(edited, original, mask)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    output.save(args.out, format="PNG", optimize=True)

    if args.mask_out:
        Path(args.mask_out).parent.mkdir(parents=True, exist_ok=True)
        mask.save(args.mask_out, format="PNG", optimize=True)

    report = {
        "dimensions": {"width": width, "height": height},
        "source_output_dimensions_match": output.size == original.size,
        "locks": [
            {"name": name, "box_px": list(region), "identical": region_identical(original, output, region)}
            for name, region in locks
        ],
    }
    report["all_locks_identical"] = all(item["identical"] for item in report["locks"])

    if args.report_out:
        Path(args.report_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report_out).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

    if not report["source_output_dimensions_match"] or not report["all_locks_identical"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
