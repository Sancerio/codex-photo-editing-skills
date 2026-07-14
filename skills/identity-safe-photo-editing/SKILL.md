---
name: identity-safe-photo-editing
description: Edit, verify, export, and conservatively upscale raster photographs while preserving identity, geometry, and protected pixels. Use for object or person removal, background cleanup, localized AI inpainting, shadow removal, color or lighting changes, hair or wardrobe retouching, resolution recovery, and workflows where raw AI previews must be distinguished from pixel-preserving composites.
---

# Identity-Safe Photo Editing

Produce professional edits without treating a full-frame AI result as the final asset. Use generated output only as replacement material, composite it through the smallest viable mask, and prove protected regions remain unchanged.

## Non-negotiable rules

- Work from the highest-resolution source or edited source selected by the user.
- Save non-destructively. Never overwrite the source without explicit instruction.
- Treat faces, bodies, hands, clothing, pose, accessories, and unrelated scene geometry as locked by default.
- Lock hair too unless hair is the explicit edit target.
- Never claim identity preservation from visual similarity alone.
- Treat a full-frame AI preview as identity-approximate even when the prompt requests preservation. It is not pixel-identical evidence.
- Reject halos, residual shadows, repeated texture, warped perspective, smeared details, hard mask boundaries, or disconnected generated elements.
- For a global color or lighting treatment, state that RGB values must change. Preserve geometry and identity rather than identical RGB values.
- Maintain asset lineage. Label the raw AI candidate, localized composite, upscale, and delivery export separately; never silently substitute one for another.

## Choose the edit path

### Local object or background removal

Use for cars, pedestrians, signs, shadows, blemishes, and localized distractions.

1. Inspect the full-resolution source.
2. Create a clean candidate replacement with an image editing/generation tool. Lock all invariants and request reconstruction of occluded texture, perspective, lighting, and shadows.
3. Do not deliver the candidate directly. Resize it to the source dimensions and composite only the edited region with `scripts/composite_local_edit.py`.
4. Keep the feathered mask away from people. Add lock regions for faces and subjects; the script fails if the mask touches them.
5. Inspect the full frame and 100% crops around every mask boundary.

### Boundary-sensitive hair, clothing, and body-adjacent edits

Generated candidates can shift facial geometry or recolor skin even when the prompt says not to. A geometrically correct mask can still transfer mismatched skin or produce a strand that appears from nowhere.

- Trace the complete visual path: a generated hair lock must have a believable root, uninterrupted middle, and natural continuation.
- Prefer a semantic matte that transfers only the target material, such as hair pixels, over a broad geometric patch that includes skin or background.
- Never blend regenerated skin into an original face merely because the face looks similar.
- Compare source, raw candidate, and final composite at 100%. Reject discontinuity, clipping, color smears, floating strands, and visible mask endpoints.
- If reliable segmentation or alignment is unavailable, stop instead of broadening the mask across protected anatomy.

### Global color or lighting treatment

Use deterministic pointwise color grading when the user wants unchanged identity and geometry.

- Do not regenerate the whole photograph merely to make it warmer, cooler, brighter, or sunset-like.
- Apply color math at the same pixel coordinates to preserve every edge, facial structure, object, and pose while intentionally changing RGB values.
- Use reference images for palette direction, not composition transfer.
- If the desired grade requires spatial generation, explain the tradeoff before proceeding.

### Background replacement around people

Use a precise subject segmentation mask. Do not approximate people with a rectangle or broad silhouette envelope; color differences will expose the boundary. If accurate segmentation is unavailable, stop and explain what is needed.

### Conservative resolution upscale

Use when the user approves a lower-resolution image and wants the original pixel dimensions without another generative pass.

1. Explain that resizing restores dimensions, not genuine camera detail.
2. Do not use generative face restoration unless the user explicitly accepts possible identity changes.
3. Run `scripts/upscale_photo.py` with the approved image as the exact input.
4. Inspect the full frame and 100% crops of faces, hair, hands, high-contrast edges, and edited boundaries.
5. Prefer the restrained sharpened result only when it has no halos or crunchy skin texture; otherwise use clean Lanczos resampling.

```bash
python scripts/upscale_photo.py \
  --input approved.png \
  --out-png approved-2560x3840.png \
  --out-jpg approved-2560x3840.jpg \
  --width 2560 --height 3840 \
  --report upscale-verification.json
```

Prompt wording such as "high resolution" may improve perceived detail but does not guarantee output dimensions. Verify actual pixels after generation.

## Asset selection and delivery safety

Before uploading or handing off:

1. Reopen the exact exported file, not an in-memory preview or an earlier candidate.
2. Confirm its dimensions, format, and file size.
3. Keep filenames explicit, such as `raw-ai-preview`, `identity-preserved-composite`, or `upscaled`.
4. Upload the exact asset the user approved. Do not replace a coherent raw preview with a masked composite merely because the composite has stronger identity guarantees.
5. Read the uploaded file or metadata back from the destination. Compare size and preferably a checksum or byte hash against the local source.
6. State the tradeoff honestly: raw AI previews may alter faces; localized composites may create seams; conservative upscales preserve appearance but add no genuine detail.

## Mask specification

Pass a JSON file to `scripts/composite_local_edit.py`:

```json
{
  "feather_px": 36,
  "edit_shapes": [
    {
      "type": "polygon",
      "points": [[0.08, 0.54], [0.39, 0.53], [0.40, 0.90], [0.08, 0.91]]
    }
  ],
  "lock_regions": [
    {"name": "man_face", "box": [0.44, 0.30, 0.52, 0.52]},
    {"name": "woman_face", "box": [0.49, 0.33, 0.58, 0.56]},
    {"name": "couple", "box": [0.39, 0.30, 0.62, 1.0]}
  ]
}
```

All coordinates are normalized fractions of width and height. Supported edit shapes are `polygon`, `rectangle`, and `ellipse`.

Run:

```bash
python scripts/composite_local_edit.py \
  --original source.jpg \
  --edited ai-candidate.png \
  --spec mask.json \
  --out final.png \
  --mask-out edit-mask.png \
  --report-out verification.json
```

The script composites the candidate only where the mask is nonzero, keeps every other source pixel exact, rejects lock-region overlap, and verifies each lock region pixel-for-pixel.

## Verification checklist

1. Confirm source and output dimensions match.
2. Confirm every lock region reports `identical: true`.
3. Inspect the edited area at 100% for residual objects, shadows, clipping, or discontinuity.
4. Trace perspective lines, horizons, repeating textures, and generated material across every seam.
5. Inspect faces, hands, hair, clothing edges, and accessories.
6. Inspect a downscaled full-frame preview for color blocks or mask-shaped boundaries.
7. Inspect the actual exported JPEG or PNG, not only an application preview.
8. Deliver a high-quality JPEG for common use and a lossless PNG when useful.
9. For upscales, verify target dimensions, inspect 100% crops, and record whether generative restoration was disabled.
10. Report the method honestly: raw AI preview, localized generated patch plus deterministic compositing, semantic-matte transfer, pointwise color grading, or conservative interpolation.

If any check fails, revise the candidate or mask and rerun. Do not deliver a known-bad draft.
