"""Bound encoded input and image allocations before processing pet artwork."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
import os
from pathlib import Path
import stat
import struct

from PIL import Image

CELL_SIZE = (192, 208)
IDLE_FRAME_COUNT = 6
MAX_SCALE = 4
MAX_PREVIEW_BYTES = 8 * 1024 * 1024
MAX_ATLAS_BYTES = 32 * 1024 * 1024


def read_image_bytes(path: Path, limit: int) -> bytes:
    """Read one bounded regular file, keeping validation and decoding on the same bytes."""
    # A FIFO must not block before the regular-file check can run.
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(descriptor, "rb") as source:
        info = os.fstat(source.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            raise SystemExit(f"image must be a regular file no larger than {limit} bytes: {path}")
        data = source.read(limit + 1)
    if len(data) > limit:
        raise SystemExit(f"image exceeds {limit} bytes: {path}")
    return data


def preview_scale(size: tuple[int, int]) -> int:
    """Accept only the renderer's four supported canvas sizes."""
    for scale in range(1, MAX_SCALE + 1):
        if size == tuple(value * scale for value in CELL_SIZE):
            return scale
    raise SystemExit("preview dimensions must be 192 x 208 at integer scale 1 through 4")


def check_gif_structure(data: bytes) -> int:
    """Check all GIF frame rectangles/counts without invoking a pixel decoder.

    Pillow can allocate disposal buffers inside open/seek, before callers can
    inspect a new frame's size. Walk the bounded GIF block stream first. This is
    a resource gate, not a replacement for Pillow's image-data validation.
    """
    position = 0

    def take(count: int) -> bytes:
        nonlocal position
        if position + count > len(data):
            raise SystemExit("truncated GIF block")
        value = data[position:position + count]
        position += count
        return value

    def subblocks() -> None:
        while True:
            length = take(1)[0]
            if not length:
                return
            take(length)

    if take(6) not in (b"GIF87a", b"GIF89a"):
        raise SystemExit("preview must be a GIF")
    width, height, flags, _background, _aspect = struct.unpack("<HHBBB", take(7))
    scale = preview_scale((width, height))
    if flags & 128:
        take(3 * (2 ** ((flags & 7) + 1)))
    frames = 0
    while True:
        marker = take(1)
        if marker == b";":
            if frames != IDLE_FRAME_COUNT:
                raise SystemExit(f"expected {IDLE_FRAME_COUNT} GIF frames, found {frames}")
            return scale
        if marker == b"!":
            label = take(1)[0]
            if label == 0xFE:  # Comments may be empty.
                subblocks()
                continue
            # Fixed extension headers must be nonempty and correctly sized.
            # Pillow consumes an additional block after a missing first block;
            # accepting that malformed form would desynchronize our frame walk.
            header_size = {0xF9: 4, 0xFF: 11, 0x01: 12}.get(label)
            if header_size is None or take(1)[0] != header_size:
                raise SystemExit("invalid GIF extension header")
            header = take(header_size)
            if label == 0xF9:
                if take(1) != b"\0":
                    raise SystemExit("invalid GIF control extension terminator")
            elif label == 0xFF and header == b"NETSCAPE2.0":
                if take(1) != b"\x03" or take(3)[0] != 1 or take(1) != b"\0":
                    raise SystemExit("invalid GIF loop extension")
            else:
                subblocks()
        elif marker == b",":
            frames += 1
            if frames > IDLE_FRAME_COUNT:
                raise SystemExit(f"expected {IDLE_FRAME_COUNT} GIF frames, found more")
            left, top, frame_width, frame_height, flags = struct.unpack("<HHHHB", take(9))
            if (not frame_width or not frame_height or left + frame_width > width
                    or top + frame_height > height):
                raise SystemExit("GIF frame rectangle exceeds the preview canvas")
            if flags & 128:
                take(3 * (2 ** ((flags & 7) + 1)))
            take(1)  # LZW minimum code size; Pillow validates compressed image data.
            subblocks()
        else:
            raise SystemExit("invalid GIF block marker")


@dataclass
class Preview:
    """At most six decoded frames and their presentation metadata."""

    frames: list[Image.Image]
    durations: list[int | None]
    disposals: list[int | None]
    loop: int | None
    scale: int


def load_preview(path: Path, scale: int | None = None) -> Preview:
    """Decode only a structurally bounded six-frame GIF."""
    data = read_image_bytes(path, MAX_PREVIEW_BYTES)
    actual_scale = check_gif_structure(data)
    if scale is not None and (type(scale) is not int or scale != actual_scale):
        raise SystemExit("preview scale does not match its supported canvas")
    frames, durations, disposals = [], [], []
    expected_size = tuple(value * actual_scale for value in CELL_SIZE)
    with Image.open(BytesIO(data), formats=["GIF"]) as source:
        loop = source.info.get("loop")
        for index in range(IDLE_FRAME_COUNT):
            source.seek(index)
            if source.size != expected_size:
                raise SystemExit("GIF decoder canvas differs from checked dimensions")
            durations.append(source.info.get("duration"))
            disposals.append(getattr(source, "disposal_method", None))
            frames.append(source.convert("RGBA"))
    return Preview(frames, durations, disposals, loop, actual_scale)


def check_size(
    size: tuple[int, int], expected_size: tuple[int, int] | None,
    max_size: tuple[int, int] | None,
) -> None:
    if min(size) <= 0:
        raise SystemExit("image dimensions must be positive")
    if expected_size is not None and size != expected_size:
        raise SystemExit(f"expected image dimensions {expected_size}, found {size}")
    if max_size is not None and any(a > b for a, b in zip(size, max_size)):
        raise SystemExit(f"image dimensions exceed {max_size}")


def check_static_webp(
    data: bytes, expected_size: tuple[int, int] | None,
    max_size: tuple[int, int] | None,
) -> None:
    """Bound WebP canvases before Pillow creates its allocating native decoder.

    Read RIFF chunk lengths and VP8/VP8L/VP8X size fields only; Pillow remains
    responsible for compressed data. Animation is outside the atlas contract.
    Format: https://developers.google.com/speed/webp/docs/riff_container
    """
    if len(data) < 20 or int.from_bytes(data[4:8], "little") + 8 != len(data):
        raise SystemExit("invalid WebP container length")
    position, bitstreams = 12, 0
    sizes = []
    while position < len(data):
        if position + 8 > len(data):
            raise SystemExit("truncated WebP chunk")
        kind = data[position:position + 4]
        length = int.from_bytes(data[position + 4:position + 8], "little")
        start = position + 8
        position = start + length + (length % 2)
        if position > len(data):
            raise SystemExit("truncated WebP chunk")
        header = data[start:start + min(length, 10)]
        size = None
        if kind in (b"ANIM", b"ANMF"):
            raise SystemExit("image must be static")
        if kind == b"VP8X":
            if length != 10 or header[0] & 2:
                raise SystemExit("invalid or animated WebP canvas")
            size = (int.from_bytes(header[4:7], "little") + 1,
                    int.from_bytes(header[7:10], "little") + 1)
        elif kind == b"VP8 ":
            if length < 10 or header[3:6] != b"\x9d\x01\x2a":
                raise SystemExit("invalid WebP lossy header")
            size = (int.from_bytes(header[6:8], "little") & 0x3FFF,
                    int.from_bytes(header[8:10], "little") & 0x3FFF)
            bitstreams += 1
        elif kind == b"VP8L":
            if length < 5 or header[0] != 0x2F:
                raise SystemExit("invalid WebP lossless header")
            bits = int.from_bytes(header[1:5], "little")
            size = ((bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
            bitstreams += 1
        if size is not None:
            check_size(size, expected_size, max_size)
            sizes.append(size)
    if bitstreams != 1 or len(set(sizes)) != 1:
        raise SystemExit("WebP must contain one image with consistent dimensions")


def load_static_image(
    path: Path, *, formats: list[str], max_bytes: int,
    expected_size: tuple[int, int] | None = None,
    max_size: tuple[int, int] | None = None, require_alpha: bool = False,
) -> Image.Image:
    """Restrict static PNG/WebP formats and geometry before pixel conversion."""
    if not formats or not set(formats) <= {"PNG", "WEBP"}:
        raise ValueError("static image loader supports only PNG and WebP")
    if expected_size is None and max_size is None:
        raise ValueError("a static image dimension bound is required")
    data = read_image_bytes(path, max_bytes)
    if "WEBP" in formats and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        check_static_webp(data, expected_size, max_size)
    with Image.open(BytesIO(data), formats=formats) as source:
        check_size(source.size, expected_size, max_size)
        # PNG/WebP expose frame counts from container metadata, without enumeration.
        if getattr(source, "n_frames", 1) != 1:
            raise SystemExit("image must be static")
        if require_alpha and "A" not in source.getbands():
            raise SystemExit("spritesheet must contain an alpha channel")
        return source.convert("RGBA")
