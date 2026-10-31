#!/usr/bin/env python3
"""Check every distributed idle preview and its reduced-motion still."""

import json
from pathlib import Path

from PIL import ImageChops

from image_safety import MAX_PREVIEW_BYTES, load_preview, load_static_image
from render_idle_preview import validate_preview_data

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    count = 0
    for pet in json.loads((ROOT / "catalog.json").read_text())["pets"]:
        for gif in (ROOT / pet["previewPath"], ROOT / "site/assets" / f"{pet['id']}-preview.gif"):
            preview = load_preview(gif)
            validate_preview_data(preview)
            still = load_static_image(
                gif.with_suffix(".png"), formats=["PNG"], max_bytes=MAX_PREVIEW_BYTES,
                expected_size=preview.frames[0].size,
            )
            if ImageChops.difference(still, preview.frames[0]).getbbox(alpha_only=False):
                raise SystemExit(f"still differs from idle frame zero: {gif.with_suffix('.png')}")
            count += 1
    print(f"previews: {count} GIFs at 6600 ms, matching static PNGs; passed")


if __name__ == "__main__":
    main()
