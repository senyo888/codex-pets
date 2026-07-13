#!/usr/bin/env python3
"""Render a crisp six-frame idle GIF from a validated Codex v2 atlas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageSequence


ATLAS_SIZE = (1536, 2288)
CELL_SIZE = (192, 208)
IDLE_FRAME_COUNT = 6
IDLE_DURATIONS = [280, 110, 110, 140, 140, 320]
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
    with Image.open(spritesheet) as opened:
        if opened.size != ATLAS_SIZE:
            raise SystemExit(
                f"expected a {ATLAS_SIZE[0]}x{ATLAS_SIZE[1]} v2 atlas, "
                f"found {opened.width}x{opened.height}"
            )
        if "A" not in opened.getbands():
            raise SystemExit("spritesheet must contain an alpha channel")
        atlas = opened.convert("RGBA")

    width, height = CELL_SIZE
    frames = []
    for column in range(IDLE_FRAME_COUNT):
        left = column * width
        frame = atlas.crop((left, 0, left + width, height))
        if scale != 1:
            frame = frame.resize((width * scale, height * scale), Image.Resampling.LANCZOS)
        frames.append(threshold_alpha(frame, alpha_threshold))
    return frames


def validate_preview(output: Path, scale: int) -> dict[str, object]:
    output_size = tuple(dimension * scale for dimension in CELL_SIZE)
    with Image.open(output) as opened:
        frames = []
        for frame in ImageSequence.Iterator(opened):
            frames.append(
                {
                    "size": frame.size,
                    "duration": frame.info.get("duration"),
                    "disposal": getattr(frame, "disposal_method", None),
                    "alphaExtrema": frame.convert("RGBA").getchannel("A").getextrema(),
                }
            )
        loop = opened.info.get("loop")

    if len(frames) != IDLE_FRAME_COUNT:
        raise SystemExit(f"expected {IDLE_FRAME_COUNT} GIF frames, found {len(frames)}")
    if [frame["duration"] for frame in frames] != IDLE_DURATIONS:
        raise SystemExit("rendered GIF durations do not match the idle timing contract")
    if any(frame["size"] != output_size for frame in frames):
        raise SystemExit("rendered GIF contains a frame with the wrong dimensions")
    if any(frame["disposal"] != 2 for frame in frames):
        raise SystemExit("rendered GIF must use restore-to-background disposal")
    if any(frame["alphaExtrema"] != (0, 255) for frame in frames):
        raise SystemExit("rendered GIF must contain both transparent and opaque pixels")
    if loop != 0:
        raise SystemExit("rendered GIF must loop continuously")

    return {
        "ok": True,
        "output": str(output),
        "width": output_size[0],
        "height": output_size[1],
        "scale": scale,
        "frames": IDLE_FRAME_COUNT,
        "durations": IDLE_DURATIONS,
        "loop": loop,
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
    result["spritesheet"] = str(spritesheet)
    result["alphaThreshold"] = args.alpha_threshold
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
