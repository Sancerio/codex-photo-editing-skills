# Codex Photo Editing Skills

Reusable Codex skills for professional photo editing with explicit identity and pixel-preservation safeguards.

## Included skill

- `identity-safe-photo-editing` — localized AI-assisted retouching, deterministic compositing, protected-region verification, background cleanup, and non-generative color grading.

## Install

Copy the skill directory into your Codex skills folder:

```bash
cp -R skills/identity-safe-photo-editing "${CODEX_HOME:-$HOME/.codex}/skills/"
```

The bundled compositor requires Python 3 and Pillow.

## Repository layout

```text
skills/
└── identity-safe-photo-editing/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── scripts/composite_local_edit.py
```

## License

MIT
