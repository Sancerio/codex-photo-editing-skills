# Codex Photo Editing Skills

Reusable Codex skills for professional photo editing with explicit identity and pixel-preservation safeguards.

## Included skills

- `identity-safe-photo-retouching` — localized retouching, masking, deterministic compositing, color grading, and protected-pixel verification.
- `conservative-photo-upscaling` — non-generative resolution enlargement and upscale verification.
- `photo-delivery-export` — verified web/full-size folders, camera filenames, and upload readback.
- `identity-safe-photo-editing` — lightweight router for workflows spanning multiple focused skills.

## Install

Copy the skill directories into your Codex skills folder:

```bash
cp -R skills/* "${CODEX_HOME:-$HOME/.codex}/skills/"
```

The bundled scripts require Python 3 and Pillow.

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
