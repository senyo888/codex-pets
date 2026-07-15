#!/usr/bin/env python3
"""Build the Codex Pets V1 release header from tracked public assets.

The script verifies every published spritesheet checksum before reading the
catalogue previews. It never opens, rewrites, rescales, or recompresses a
package spritesheet. The laboratory, instrumentation, lighting, and motion are
drawn deterministically with Pillow; the pets remain the real tracked preview
frames referenced by catalog.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFilter, ImageSequence


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 1200
HEIGHT = 560
FRAME_COUNT = 24
FRAME_DURATION_MS = 280
STATIC_FRAME_INDEX = 9
OUTPUT_GIF = "codex-pets-v1-lab.gif"
OUTPUT_STATIC = "codex-pets-v1-lab-static.png"

NAVY = (3, 12, 26)
INK = (240, 251, 255)
CYAN = (100, 230, 245)
BLUE = (23, 135, 255)
VIOLET = (139, 92, 246)
GOLD = (249, 198, 66)
GREEN = (99, 233, 148)
SCARLET = (255, 105, 91)


@dataclass(frozen=True)
class Placement:
    center_x: int
    bottom_y: int
    visible_height: int
    phase: int


# Explicit V1 staging is intentional. A catalogue addition must update the
# composition instead of silently producing an overcrowded or incomplete hero.
PLACEMENTS = {
    "aethercore": Placement(150, 438, 176, 1),
    "aethermite": Placement(342, 463, 168, 4),
    "bella": Placement(600, 505, 194, 0),
    "aetherwing": Placement(610, 238, 180, 3),
    "aetherbite": Placement(824, 463, 168, 2),
    "calian": Placement(1000, 451, 176, 5),
    "scarlet": Placement(1110, 451, 178, 0),
}

PET_ACCENTS = {
    "aethercore": GOLD,
    "aethermite": (84, 230, 195),
    "bella": CYAN,
    "aetherwing": (101, 230, 244),
    "aetherbite": (88, 174, 255),
    "calian": (255, 138, 115),
    "scarlet": (212, 140, 255),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "docs" / "releases" / "assets",
        help="Directory for the release animation and static fallback.",
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_catalogue() -> dict[str, dict]:
    catalogue = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    published = {
        pet["id"]: pet
        for pet in catalogue["pets"]
        if pet.get("publicationState") == "published"
    }
    expected = set(PLACEMENTS)
    actual = set(published)
    if actual != expected:
        missing = sorted(actual - expected)
        stale = sorted(expected - actual)
        raise SystemExit(
            "V1 header composition does not match the published catalogue: "
            f"unplaced={missing or 'none'}, unpublished={stale or 'none'}"
        )

    for pet_id, pet in published.items():
        spritesheet = ROOT / pet["spritesheetPath"]
        actual_hash = sha256(spritesheet)
        if actual_hash != pet["sha256"]:
            raise SystemExit(
                f"spritesheet checksum mismatch for {pet_id}: "
                f"catalog={pet['sha256']} actual={actual_hash}"
            )
    return published


def union_bbox(frames: Iterable[Image.Image]) -> tuple[int, int, int, int]:
    boxes = [frame.getchannel("A").getbbox() for frame in frames]
    visible = [box for box in boxes if box is not None]
    if not visible:
        raise ValueError("preview contains no visible pixels")
    return (
        min(box[0] for box in visible),
        min(box[1] for box in visible),
        max(box[2] for box in visible),
        max(box[3] for box in visible),
    )


def load_pet_frames(pet: dict, placement: Placement) -> list[Image.Image]:
    preview_path = ROOT / pet["previewPath"]
    with Image.open(preview_path) as source:
        frames = [frame.convert("RGBA") for frame in ImageSequence.Iterator(source)]
    if len(frames) != 6:
        raise SystemExit(
            f"expected 6 tracked preview frames for {pet['id']}, found {len(frames)}"
        )

    bbox = union_bbox(frames)
    crop_width = bbox[2] - bbox[0]
    crop_height = bbox[3] - bbox[1]
    target_width = round(placement.visible_height * crop_width / crop_height)
    return [
        frame.crop(bbox).resize(
            (target_width, placement.visible_height), Image.Resampling.LANCZOS
        )
        for frame in frames
    ]


def rgba_layer() -> Image.Image:
    return Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))


def composite_with_opacity(
    destination: Image.Image,
    source: Image.Image,
    position: tuple[int, int],
    opacity: int,
) -> None:
    layer = source.copy()
    alpha = layer.getchannel("A").point(lambda value: value * opacity // 255)
    layer.putalpha(alpha)
    destination.alpha_composite(layer, position)


def glow_ellipse(
    image: Image.Image,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int],
    alpha: int,
    blur: int,
) -> None:
    glow = rgba_layer()
    ImageDraw.Draw(glow).ellipse(box, fill=(*color, alpha))
    image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(blur)))


def draw_glass_panel(
    image: Image.Image,
    box: tuple[int, int, int, int],
    accent: tuple[int, int, int],
    phase: float,
    scan_offset: int,
) -> None:
    layer = rgba_layer()
    draw = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(
        box,
        radius=14,
        fill=(5, 27, 48, 142),
        outline=(*accent, 92),
        width=2,
    )
    draw.line((x0 + 14, y0 + 28, x1 - 14, y0 + 28), fill=(*accent, 56), width=1)
    for row in range(4):
        y = y0 + 48 + row * 24
        length = 34 + ((row * 31 + scan_offset * 7) % max(40, x1 - x0 - 68))
        draw.rounded_rectangle(
            (x0 + 18, y, min(x0 + 18 + length, x1 - 18), y + 5),
            radius=2,
            fill=(*accent, 44 + row * 6),
        )
    scan_y = y0 + 34 + ((scan_offset * 9) % max(1, y1 - y0 - 44))
    draw.line((x0 + 8, scan_y, x1 - 8, scan_y), fill=(*accent, 42), width=1)
    sheen_x = x0 + 10 + round((x1 - x0 - 20) * phase)
    draw.line((sheen_x, y0 + 10, min(sheen_x + 26, x1 - 8), y1 - 10), fill=(255, 255, 255, 18), width=2)
    image.alpha_composite(layer)


def build_static_lab(logo: Image.Image) -> Image.Image:
    base = Image.new("RGBA", (WIDTH, HEIGHT), (*NAVY, 255))
    draw = ImageDraw.Draw(base)

    top = (3, 12, 27)
    bottom = (8, 27, 45)
    for y in range(HEIGHT):
        ratio = y / (HEIGHT - 1)
        color = tuple(round(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
        draw.line((0, y, WIDTH, y), fill=(*color, 255))

    ambient = rgba_layer()
    ambient_draw = ImageDraw.Draw(ambient)
    ambient_draw.ellipse((-210, -280, 520, 450), fill=(23, 135, 255, 54))
    ambient_draw.ellipse((760, -260, 1420, 430), fill=(139, 92, 246, 42))
    ambient_draw.ellipse((340, 80, 900, 690), fill=(100, 230, 245, 24))
    base.alpha_composite(ambient.filter(ImageFilter.GaussianBlur(100)))

    # Architectural shell and a calm, technically credible floor grid.
    draw = ImageDraw.Draw(base)
    draw.polygon(((0, 0), (250, 0), (420, 382), (0, 420)), fill=(4, 15, 31, 205))
    draw.polygon(((950, 0), (1200, 0), (1200, 420), (780, 382)), fill=(4, 15, 31, 205))
    draw.line((0, 382, WIDTH, 382), fill=(100, 230, 245, 52), width=2)
    draw.rectangle((0, 383, WIDTH, HEIGHT), fill=(4, 16, 29, 170))
    for y in (410, 448, 494, 546):
        draw.line((0, y, WIDTH, y), fill=(100, 230, 245, 20), width=1)
    for floor_x in range(-120, WIDTH + 121, 120):
        draw.line((600, 382, floor_x, HEIGHT), fill=(100, 230, 245, 18), width=1)

    # Ceiling rails and sparse faceted signal nodes.
    for offset in (0, 1):
        y = 26 + offset * 22
        draw.line((80, y, 1120, y), fill=(100, 230, 245, 28 - offset * 8), width=2)
    for x, y, color in (
        (94, 72, CYAN),
        (262, 48, BLUE),
        (906, 61, VIOLET),
        (1135, 84, GOLD),
        (746, 43, CYAN),
    ):
        draw.polygon(((x, y - 5), (x + 5, y), (x, y + 5), (x - 5, y)), fill=(*color, 88))

    # Static glass stations. Moving scan details are added per frame.
    for box, accent in (
        ((26, 98, 250, 284), CYAN),
        ((468, 92, 732, 340), CYAN),
        ((938, 96, 1174, 284), VIOLET),
    ):
        draw.rounded_rectangle(box, radius=16, fill=(5, 23, 42, 130), outline=(*accent, 48), width=2)

    # Approved orbital-paw language appears as a restrained console hologram.
    logo_copy = logo.copy()
    logo_copy.thumbnail((126, 126), Image.Resampling.LANCZOS)
    composite_with_opacity(base, logo_copy, ((WIDTH - logo_copy.width) // 2, 138), 96)

    # Bench and reactor structures sit behind the characters.
    draw = ImageDraw.Draw(base)
    draw.polygon(((252, 397), (438, 397), (463, 422), (229, 422)), fill=(12, 45, 66, 235), outline=(*CYAN, 66))
    draw.rectangle((252, 422, 438, 448), fill=(7, 25, 40, 245), outline=(*CYAN, 42))
    draw.polygon(((748, 397), (935, 397), (960, 422), (724, 422)), fill=(12, 45, 66, 235), outline=(*BLUE, 66))
    draw.rectangle((748, 422, 935, 448), fill=(7, 25, 40, 245), outline=(*BLUE, 42))
    draw.rounded_rectangle((508, 414, 692, 485), radius=20, fill=(7, 29, 48, 240), outline=(*CYAN, 68), width=2)
    draw.rounded_rectangle((960, 388, 1175, 448), radius=14, fill=(8, 28, 45, 238), outline=(*VIOLET, 62), width=2)

    return base


def draw_dynamic_lab(image: Image.Image, frame_index: int) -> None:
    phase = frame_index / FRAME_COUNT
    wave = (math.sin(phase * math.tau) + 1) / 2

    draw_glass_panel(image, (26, 98, 250, 284), CYAN, phase, frame_index)
    draw_glass_panel(image, (468, 92, 732, 340), CYAN, (phase + 0.33) % 1, frame_index + 5)
    draw_glass_panel(image, (938, 96, 1174, 284), VIOLET, (phase + 0.66) % 1, frame_index + 11)

    # AetherCore's reactor: slow pulse, rotating arcs, no flash.
    reactor = rgba_layer()
    reactor_draw = ImageDraw.Draw(reactor)
    center = (150, 314)
    radius = 82
    glow_ellipse(image, (96, 260, 204, 368), CYAN, 24 + round(wave * 18), 22)
    for index, color in enumerate((CYAN, BLUE, GOLD)):
        inset = index * 10
        start = (frame_index * (4 + index) * (1 if index != 1 else -1) + index * 47) % 360
        reactor_draw.arc(
            (
                center[0] - radius + inset,
                center[1] - radius + inset,
                center[0] + radius - inset,
                center[1] + radius - inset,
            ),
            start=start,
            end=start + 205 - index * 18,
            fill=(*color, 96 - index * 14),
            width=3,
        )
    reactor_draw.ellipse((127, 291, 173, 337), fill=(7, 34, 55, 220), outline=(*CYAN, 104), width=2)
    reactor_draw.ellipse((140, 304, 160, 324), fill=(*CYAN, 106 + round(wave * 48)))
    image.alpha_composite(reactor)

    # Quiet waveform at Bella's truth console.
    console = rgba_layer()
    console_draw = ImageDraw.Draw(console)
    points = []
    for x in range(500, 701, 8):
        envelope = math.sin((x - 500) / 200 * math.pi)
        y = 301 + math.sin((x / 32) + phase * math.tau) * 10 * envelope
        points.append((x, round(y)))
    console_draw.line(points, fill=(*CYAN, 104), width=2)
    cursor_x = 500 + round(200 * phase)
    console_draw.line((cursor_x, 280, cursor_x, 320), fill=(*GOLD, 82), width=2)
    image.alpha_composite(console)

    # Calian traces the fault; Scarlet closes it. The status moves steadily
    # from scarlet through gold to green over the complete 6.72-second loop.
    correction = rgba_layer()
    correction_draw = ImageDraw.Draw(correction)
    progress = 0.18 + 0.76 * (0.5 - 0.5 * math.cos(phase * math.tau))
    correction_draw.rounded_rectangle((978, 348, 1156, 361), radius=6, fill=(4, 15, 26, 220), outline=(*VIOLET, 50))
    progress_color = GREEN if progress > 0.72 else GOLD if progress > 0.42 else SCARLET
    correction_draw.rounded_rectangle((981, 351, 981 + round(172 * progress), 358), radius=3, fill=(*progress_color, 152))
    for x in range(990, 1150, 26):
        height = 8 + ((x + frame_index * 5) % 22)
        correction_draw.line((x, 332, x, 332 - height), fill=(*VIOLET, 50), width=2)
    image.alpha_composite(correction)


def draw_floor_shadows(image: Image.Image) -> None:
    shadows = rgba_layer()
    draw = ImageDraw.Draw(shadows)
    for pet_id, placement in PLACEMENTS.items():
        if pet_id == "aetherwing":
            continue
        width = 72 if pet_id not in {"bella", "aethermite"} else 88
        draw.ellipse(
            (
                placement.center_x - width,
                placement.bottom_y - 12,
                placement.center_x + width,
                placement.bottom_y + 10,
            ),
            fill=(*PET_ACCENTS[pet_id], 42),
        )
    image.alpha_composite(shadows.filter(ImageFilter.GaussianBlur(13)))


def place_pet(image: Image.Image, pet_frame: Image.Image, placement: Placement) -> None:
    x = placement.center_x - pet_frame.width // 2
    y = placement.bottom_y - pet_frame.height
    image.alpha_composite(pet_frame, (x, y))


def draw_foreground_instruments(image: Image.Image, frame_index: int) -> None:
    phase = frame_index / FRAME_COUNT
    layer = rgba_layer()
    draw = ImageDraw.Draw(layer)

    # Bench lips integrate the two tinkerers without covering their identity.
    draw.polygon(((238, 420), (454, 420), (440, 437), (252, 437)), fill=(8, 31, 48, 244), outline=(*CYAN, 70))
    draw.polygon(((733, 420), (951, 420), (936, 437), (748, 437)), fill=(8, 31, 48, 244), outline=(*BLUE, 70))
    for x, accent, offset in ((270, CYAN, 0), (774, BLUE, 7)):
        for index in range(4):
            active = ((frame_index + offset) // 3) % 4 == index
            color = GOLD if active else accent
            draw.rounded_rectangle((x + index * 31, 425, x + 18 + index * 31, 430), radius=2, fill=(*color, 150 if active else 58))

    # Central truth console and paired diagnosis/correction stations.
    draw.rounded_rectangle((521, 454, 679, 482), radius=11, fill=(5, 24, 39, 248), outline=(*CYAN, 88), width=2)
    draw.line((540, 463, 660, 463), fill=(*CYAN, 58), width=2)
    truth_x = 540 + round(120 * phase)
    draw.ellipse((truth_x - 3, 460, truth_x + 3, 466), fill=(*GOLD, 168))
    draw.rounded_rectangle((966, 417, 1170, 445), radius=10, fill=(6, 23, 38, 246), outline=(*VIOLET, 74), width=2)
    draw.line((985, 429, 1148, 429), fill=(*GREEN, 62), width=2)

    image.alpha_composite(layer)


def build_frames(
    catalogue: dict[str, dict],
    logo: Image.Image,
) -> list[Image.Image]:
    pet_frames = {
        pet_id: load_pet_frames(catalogue[pet_id], placement)
        for pet_id, placement in PLACEMENTS.items()
    }
    static_lab = build_static_lab(logo)
    output: list[Image.Image] = []

    for frame_index in range(FRAME_COUNT):
        scene = static_lab.copy()
        draw_dynamic_lab(scene, frame_index)
        draw_floor_shadows(scene)

        # Background-to-foreground order keeps the lab readable and every pet
        # fully visible. AetherWing patrols above the grounded work stations.
        for pet_id in (
            "aethercore",
            "aetherwing",
            "aethermite",
            "aetherbite",
            "calian",
            "scarlet",
            "bella",
        ):
            placement = PLACEMENTS[pet_id]
            frame = pet_frames[pet_id][(frame_index + placement.phase) % 6]
            place_pet(scene, frame, placement)

        draw_foreground_instruments(scene, frame_index)
        output.append(scene.convert("RGB"))
    return output


def make_global_palette(frames: list[Image.Image]) -> Image.Image:
    thumb_width = WIDTH // 4
    thumb_height = HEIGHT // 4
    sheet = Image.new("RGB", (thumb_width * 4, thumb_height * 6), NAVY)
    for index, frame in enumerate(frames):
        thumb = frame.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        x = (index % 4) * thumb_width
        y = (index // 4) * thumb_height
        sheet.paste(thumb, (x, y))
    return sheet.quantize(
        colors=192,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.NONE,
    )


def save_outputs(frames: list[Image.Image], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    animation_path = output_dir / OUTPUT_GIF
    static_path = output_dir / OUTPUT_STATIC

    frames[STATIC_FRAME_INDEX].save(static_path, format="PNG", optimize=True)
    palette = make_global_palette(frames)
    paletted = [
        frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames
    ]
    paletted[0].save(
        animation_path,
        format="GIF",
        save_all=True,
        append_images=paletted[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        optimize=True,
        disposal=1,
    )
    return animation_path, static_path


def report_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def main() -> int:
    args = parse_args()
    catalogue = load_catalogue()
    logo_path = ROOT / "site" / "assets" / "brand" / "codex-pets-logo.png"
    with Image.open(logo_path) as logo_source:
        logo = logo_source.convert("RGBA")
    frames = build_frames(catalogue, logo)
    animation_path, static_path = save_outputs(frames, args.output_dir)
    print(
        json.dumps(
            {
                "animation": report_path(animation_path),
                "static": report_path(static_path),
                "width": WIDTH,
                "height": HEIGHT,
                "frames": FRAME_COUNT,
                "frameDurationMs": FRAME_DURATION_MS,
                "durationMs": FRAME_COUNT * FRAME_DURATION_MS,
                "loop": "infinite",
                "publishedPets": sorted(catalogue),
                "animationBytes": animation_path.stat().st_size,
                "staticBytes": static_path.stat().st_size,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
