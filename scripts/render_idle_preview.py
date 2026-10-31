#!/usr/bin/env python3
"""Render a six-frame idle GIF and matching still from a validated Codex v2 atlas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

from image_safety import (
    CELL_SIZE, IDLE_FRAME_COUNT, MAX_ATLAS_BYTES, MAX_SCALE, Preview,
    load_preview, load_static_image,
)


ATLAS_SIZE = (1536, 2288)
# Desktop renderer observed in 26.930.21537: base idle holds multiplied by six.
# Presentation timing only; pet.json cannot override the app's animation timing.
IDLE_DURATIONS = [1680, 660, 660, 840, 840, 1920]
DEFAULT_ALPHA_THRESHOLD = 192
DEFAULT_SCALE = 2


def threshold_alpha(frame: Image.Image, threshold: int) -> Image.Image:
    rgba = frame.convert("RGBA")
    alpha = rgba.getchannel("A").point([0] * threshold + [255] * (256 - threshold))
    rgba.putalpha(alpha)
    return rgba


def load_idle_frames(
    spritesheet: Path, alpha_threshold: int, scale: int
) -> list[Image.Image]:
    if type(scale) is not int or not 1 <= scale <= MAX_SCALE:
        raise SystemExit("--scale must be between 1 and 4")
    if type(alpha_threshold) is not int or not 1 <= alpha_threshold <= 255:
        raise SystemExit("--alpha-threshold must be between 1 and 255")
    atlas = load_static_image(
        spritesheet, formats=["WEBP", "PNG"], max_bytes=MAX_ATLAS_BYTES,
        expected_size=ATLAS_SIZE, require_alpha=True,
    )

    width, height = CELL_SIZE
    frames = []
    for column in range(IDLE_FRAME_COUNT):
        left = column * width
        frame = atlas.crop((left, 0, left + width, height))
        if scale != 1:
            frame = frame.resize((width * scale, height * scale), Image.Resampling.LANCZOS)
        frames.append(threshold_alpha(frame, alpha_threshold))
    return frames


def validate_preview_data(preview: Preview) -> None:
    """Preserve the timing and transparency contract after bounded decoding."""
    if preview.durations != IDLE_DURATIONS:
        raise SystemExit("rendered GIF durations do not match the idle timing contract")
    if any(disposal != 2 for disposal in preview.disposals):
        raise SystemExit("rendered GIF must use restore-to-background disposal")
    if any(frame.getchannel("A").getextrema() != (0, 255) for frame in preview.frames):
        raise SystemExit("rendered GIF must contain both transparent and opaque pixels")
    if preview.loop != 0:
        raise SystemExit("rendered GIF must loop continuously")


def validate_preview(output: Path, scale: int) -> dict[str, object]:
    """Validate a bounded preview and retain the existing report contract."""
    preview = load_preview(output, scale)
    validate_preview_data(preview)
    output_size = preview.frames[0].size
    return {
        "ok": True,
        "output": str(output),
        "width": output_size[0],
        "height": output_size[1],
        "scale": scale,
        "frames": IDLE_FRAME_COUNT,
        "durations": IDLE_DURATIONS,
        "loop": preview.loop,
        "disposal": 2,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spritesheet", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--alpha-threshold",
        type=int,
        default=DEFAULT_ALPHA_THRESHOLD,
        help="Minimum 0-255 source alpha retained in GIF's binary transparency mask.",
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=DEFAULT_SCALE,
        help="Integer presentation scale. The default 2x asset is downsampled by browsers.",
    )
    args = parser.parse_args()

    if not 1 <= args.alpha_threshold <= 255:
        raise SystemExit("--alpha-threshold must be between 1 and 255")
    if not 1 <= args.scale <= 4:
        raise SystemExit("--scale must be between 1 and 4")

    spritesheet = args.spritesheet.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not spritesheet.is_file():
        raise SystemExit(f"spritesheet not found: {spritesheet}")

    frames = load_idle_frames(spritesheet, args.alpha_threshold, args.scale)
    output.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=IDLE_DURATIONS,
        loop=0,
        disposal=2,
        optimize=True,
        dither=Image.Dither.NONE,
    )

    result = validate_preview(output, args.scale)
    load_preview(output, args.scale).frames[0].save(output.with_suffix(".png"))
    result["stillOutput"] = str(output.with_suffix(".png"))
    result["spritesheet"] = str(spritesheet)
    result["alphaThreshold"] = args.alpha_threshold
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
