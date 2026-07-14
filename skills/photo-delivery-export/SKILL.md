---
name: photo-delivery-export
description: Package approved photographer JPEG masters into verified web-size and full-size delivery folders. Use when creating `EDITED WEB SIZE` and `EDITED FULL SIZE`, matching an existing gallery convention, retaining original camera filenames, producing 2,500-pixel-long-edge web JPEGs, uploading final photos to Google Drive, or verifying uploaded names, dimensions, byte sizes, and hashes.
---

# Photo Delivery Export

Package already-approved masters. Do not retouch, regenerate, or upscale images in this skill.

## Default convention

- Create sibling folders named `EDITED WEB SIZE` and `EDITED FULL SIZE`.
- Use the original photo basename in both folders, such as `PRG03847.jpg`.
- Copy the approved JPEG master into `EDITED FULL SIZE` byte-for-byte. Do not re-encode, resize, sharpen, or substitute it.
- Export `EDITED WEB SIZE` from that exact master as an sRGB JPEG with a 2,500-pixel long edge.
- Round the other dimension to the nearest pixel while preserving aspect ratio; typical 3:2 outputs are `2500x1667` and `1667x2500`.
- Use deterministic resizing only. Never apply generative enhancement or face restoration.
- When an existing delivery is available, inspect and match its folder names, long-edge size, color profile, and compression instead of assuming defaults.

## Export the bundle

```bash
python scripts/export_delivery_sizes.py \
  --input approved-edit-1.jpg approved-edit-2.jpg \
  --name PRG03847.jpg PRG04224.jpg \
  --output-root delivery \
  --report delivery/export-verification.json
```

Provide one safe JPEG `--name` per input when workflow filenames contain suffixes but delivery filenames must retain camera basenames. If a master is not JPEG, create and approve a full-size JPEG before running this workflow; do not claim a converted file is byte-identical.

## Verify local delivery

1. Confirm each full-size SHA-256 equals its approved input.
2. Confirm each web long edge is exactly 2,500 pixels.
3. Confirm sRGB, expected orientation, filename, format, and byte size.
4. Reopen the exact exports and inspect them visually.

## Upload and verify

1. Ground the destination folder and check whether matching subfolders already exist.
2. Reuse matching folders or create `EDITED WEB SIZE` and `EDITED FULL SIZE` under the requested parent.
3. Upload only the verified JPEGs from each local folder.
4. List both destination folders after upload.
5. Compare uploaded filenames and byte sizes with local files; compare checksums when the destination exposes them.
6. Return destination folder links and report any verification limitation explicitly.
