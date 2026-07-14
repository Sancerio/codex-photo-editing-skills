---
name: identity-safe-photo-editing
description: Compose multi-stage identity-safe photo workflows across focused retouching, conservative upscaling, and delivery-export skills. Use when a request spans two or more of these stages, requires end-to-end asset lineage, or needs routing to the correct focused photo skill. For a single-stage request, use the corresponding focused skill directly.
---

# Identity-Safe Photo Editing

Route and compose focused skills. Do not duplicate their implementation here.

## Route to the minimum skill set

- Use `$identity-safe-photo-retouching` for object or person removal, background cleanup, hair or wardrobe edits, color grading, masking, compositing, and protected-pixel verification.
- Use `$conservative-photo-upscaling` for enlarging an approved image without generative face restoration.
- Use `$photo-delivery-export` for web/full-size folders, original camera filenames, Google Drive upload, and delivery verification.

For single-stage work, load and follow only that focused skill.

## Compose multi-stage work

When the user requests multiple stages, run them in this order:

1. Retouch and verify an edited master.
2. Obtain or infer approval only within the user's authorization; never silently replace the selected result.
3. Upscale the exact approved result when requested.
4. Package and upload the exact approved master or upscale when requested.

At every handoff, record the input path, output path, dimensions, format, byte size, and SHA-256 hash. Preserve explicit lineage among raw AI candidates, localized composites, approved masters, upscales, web exports, and uploaded files.

Never let a later stage regenerate or alter an asset approved at an earlier stage. If a focused skill's verification fails, stop that stage instead of continuing with a known-bad asset.
