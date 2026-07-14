---
name: identity-safe-photo-retouching
description: Retouch raster photographs while preserving identity, geometry, and protected pixels. Use for object or person removal, background cleanup, localized AI inpainting, shadow removal, deterministic color or lighting changes, hair or wardrobe adjustments, and any edit where faces, bodies, hands, clothing, pose, or unrelated scene content must remain locked.
---

# Identity-Safe Photo Retouching

Produce a verified edited master. Do not resize, upscale, or package delivery variants in this skill.

## Non-negotiable rules

- Work from the highest-resolution source selected by the user and save non-destructively.
- Lock faces, bodies, hands, clothing, pose, accessories, and unrelated geometry by default. Lock hair unless hair is the explicit target.
- Treat a full-frame AI result as identity-approximate, never pixel-identical evidence.
- Use generated output only as replacement material and composite through the smallest viable mask.
- Reject residual objects or shadows, halos, repeated texture, warped perspective, smeared detail, hard mask boundaries, floating hair, or disconnected elements.
- Maintain explicit lineage between source, raw AI candidate, localized composite, and approved edited master.

## Select the retouching method

### Local object, person, or shadow removal

1. Inspect the full-resolution source.
2. Generate or construct clean replacement material with matching texture, perspective, lighting, and shadows.
3. Resize the candidate to source dimensions and composite only the edited region with `scripts/composite_local_edit.py`.
4. Keep the mask away from protected people and add lock regions for faces and subjects.
5. Inspect the full frame and every mask boundary at 100%.

### Hair, clothing, or body-adjacent edit

- Trace each generated element from root through its full continuation.
- Prefer a semantic matte for the target material over a broad patch containing skin or background.
- Never blend regenerated skin into an original face merely because it looks similar.
- Stop if reliable segmentation or alignment is unavailable; do not broaden the mask across protected anatomy.

### Global color or lighting treatment

- Use deterministic pointwise color grading when geometry and identity must remain unchanged.
- Use reference images for palette direction, not composition transfer.
- State that RGB values intentionally change even though facial structure and geometry remain fixed.
- Do not regenerate a whole photograph only to make it warmer, cooler, brighter, or sunset-like.

### Background replacement around people

Use a precise subject segmentation mask. Do not approximate people with rectangles or loose silhouette envelopes. Stop if accurate segmentation is unavailable.

## Composite a localized candidate

Create a JSON mask specification with normalized coordinates:

```json
{
  "feather_px": 36,
  "edit_shapes": [
    {"type": "polygon", "points": [[0.08, 0.54], [0.39, 0.53], [0.40, 0.90], [0.08, 0.91]]}
  ],
  "lock_regions": [
    {"name": "face", "box": [0.44, 0.30, 0.58, 0.56]},
    {"name": "subjects", "box": [0.39, 0.30, 0.62, 1.0]}
  ]
}
```

Run:

```bash
python scripts/composite_local_edit.py \
  --original source.jpg \
  --edited ai-candidate.png \
  --spec mask.json \
  --out edited-master.png \
  --mask-out edit-mask.png \
  --report-out verification.json
```

The script fails if the edit mask touches a lock region and verifies protected regions pixel-for-pixel.

## Verify the edited master

1. Confirm source and output dimensions match.
2. Confirm every lock region reports `identical: true`.
3. Inspect edited areas and seams at 100%.
4. Trace perspective, horizons, repeating textures, hair, clothing edges, and accessories.
5. Reopen the exact exported file and inspect a downscaled full-frame preview.
6. Label the method honestly: raw AI preview, localized generated patch plus deterministic compositing, semantic-matte transfer, or pointwise color grading.

Do not approve a known-bad draft. Hand the approved edited master to a separate upscaling or delivery skill only when the user requests those stages.
