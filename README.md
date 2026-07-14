# Codex Photo Editing Skills

Reusable Codex skills for professional photo editing with explicit identity and pixel-preservation safeguards.

## Included skill

- `identity-safe-photo-editing` — localized AI-assisted retouching, deterministic compositing, protected-region verification, asset-lineage checks, background cleanup, non-generative color grading, and conservative resolution upscaling.

## Install

Copy the skill directory into your Codex skills folder:

```bash
cp -R skills/identity-safe-photo-editing "${CODEX_HOME:-$HOME/.codex}/skills/"
```

The bundled compositor and upscaler require Python 3 and Pillow.

## Repository layout

```text
skills/
└── identity-safe-photo-editing/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── scripts/
        ├── composite_local_edit.py
        └── upscale_photo.py
```

## License

MIT
