# Codex Photo Editing Skills

Reusable Codex skills for professional photo editing with explicit identity and pixel-preservation safeguards.

## Included skills

- `identity-safe-photo-retouching` — localized retouching, masking, deterministic compositing, color grading, and protected-pixel verification.
- `conservative-photo-upscaling` — non-generative resolution enlargement and upscale verification.
- `photo-delivery-export` — verified web/full-size folders, camera filenames, and upload readback.
- `identity-safe-photo-editing` — lightweight router for workflows spanning multiple focused skills.

## Choosing a skill

Use the narrow skill directly for a single-stage request:

| Task | Skill |
| --- | --- |
| Remove objects or people, adjust hair, replace a background, or color-grade | `identity-safe-photo-retouching` |
| Enlarge an approved result without generative face restoration | `conservative-photo-upscaling` |
| Create `EDITED WEB SIZE` and `EDITED FULL SIZE`, preserve camera filenames, or upload and verify delivery files | `photo-delivery-export` |
| Coordinate two or more of the above stages | `identity-safe-photo-editing` |

The composition order is retouch and verify, optionally upscale the exact approved result, then package and upload it. Each handoff retains explicit dimensions, file size, and SHA-256 lineage.

## Install

Copy the skill directories into your Codex skills folder:

```bash
cp -R skills/* "${CODEX_HOME:-$HOME/.codex}/skills/"
```

To install only one focused capability, copy its individual directory instead.

The three focused skills each own one deterministic Python script. They require Python 3 and Pillow; the composition skill contains no executable scripts.

## Repository layout

```text
skills/
├── identity-safe-photo-editing/       # composition only
├── identity-safe-photo-retouching/    # composite_local_edit.py
├── conservative-photo-upscaling/      # upscale_photo.py
└── photo-delivery-export/             # export_delivery_sizes.py
```

## License

MIT
