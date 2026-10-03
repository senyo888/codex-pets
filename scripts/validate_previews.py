#!/usr/bin/env python3
"""Check every distributed idle preview and its reduced-motion still."""

import json
from pathlib import Path

from PIL import Image, ImageChops

from render_idle_preview import validate_preview

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    count = 0
    for pet in json.loads((ROOT / "catalog.json").read_text())["pets"]:
        for gif in (ROOT / pet["previewPath"], ROOT / "site/assets" / f"{pet['id']}-preview.gif"):
            with Image.open(gif) as preview:
                if preview.width % 192:
                    raise SystemExit(f"invalid preview width: {gif}")
                validate_preview(gif, preview.width // 192)
                with Image.open(gif.with_suffix(".png")) as still:
                    if getattr(still, "n_frames", 1) != 1 or still.size != preview.size:
                        raise SystemExit(f"invalid still dimensions or frame count: {still.filename}")
                    if ImageChops.difference(still.convert("RGBA"), preview.convert("RGBA")).getbbox(alpha_only=False):
                        raise SystemExit(f"still differs from idle frame zero: {still.filename}")
            count += 1
    print(f"previews: {count} GIFs at 6600 ms, matching static PNGs; passed")


if __name__ == "__main__":
    main()
