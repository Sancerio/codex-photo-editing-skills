---
name: conservative-photo-upscaling
description: Enlarge an approved raster photograph to requested pixel dimensions without generative face restoration or identity-changing detail synthesis. Use when a user approves a lower-resolution edit or AI preview and wants original-size dimensions, print dimensions, or a restrained high-resolution JPEG or PNG while preserving its exact visual appearance.
---

# Conservative Photo Upscaling

Restore dimensions with deterministic interpolation. Do not perform retouching or create delivery-folder variants in this skill.

## Rules

- Use the exact user-approved image as input and preserve its aspect ratio.
- Explain that resizing restores pixel dimensions, not genuine camera detail.
- Do not use generative enhancement, face restoration, or identity-changing synthesis unless the user explicitly accepts that risk.
- Keep the clean Lanczos result and restrained-sharpened result distinct.
- Reject halos, crunchy skin, ringing, oversharpened hair, or altered facial structure.

## Run the upscaler

```bash
python scripts/upscale_photo.py \
  --input approved.png \
  --out-png approved-2560x3840.png \
  --out-jpg approved-2560x3840.jpg \
  --width 2560 --height 3840 \
  --report upscale-verification.json
```

Use `--no-sharpen` when sharpening creates artifacts. Prompt wording such as "high resolution" never proves output dimensions; inspect the actual file.

## Verify the upscale

1. Confirm the target dimensions and unchanged aspect ratio.
2. Confirm the report records `generative_face_restoration: false`.
3. Inspect the full frame and 100% crops of faces, hair, hands, high-contrast edges, and edited boundaries.
4. Compare clean and sharpened variants; prefer clean Lanczos when the sharpened result introduces artifacts.
5. Reopen the exact JPEG or PNG intended for delivery and record its size and SHA-256 hash.
6. Describe the method as conservative interpolation, not recovered original detail.

Hand the approved upscale to a separate delivery-export skill only when packaging or uploading is requested.
