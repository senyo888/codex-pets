#!/usr/bin/env python3
"""Exercise image limits before decoder/allocation calls, plus valid artwork paths."""

from __future__ import annotations

import os
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, UnidentifiedImageError

import build_lab_header as header
import image_safety as safety
import render_idle_preview as renderer


class ImageSafetyTests(unittest.TestCase):
    """Keep adversarial fixtures tiny and all generated outputs disposable."""

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def gif(self, scale: int = 1, frames: int = 6) -> Path:
        """Generate distinct transparent frames with the real timing contract."""
        images = []
        for index in range(frames):
            image = Image.new("RGBA", (192 * scale, 208 * scale))
            image.paste((255, 40 * index, 0, 255), (index + 1, 1, index + 9, 9))
            images.append(image)
        path = self.root / f"preview-{scale}-{frames}.gif"
        images[0].save(
            path, save_all=True, append_images=images[1:], loop=0, disposal=2,
            duration=(renderer.IDLE_DURATIONS if frames == 6 else [100] * frames),
        )
        return path

    def encoded_gif(self, rectangles: list[tuple[int, int, int, int]]) -> bytes:
        """Build a small block stream for pre-decoder geometry rejection tests."""
        data = b"GIF89a" + struct.pack("<HHBBB", 192, 208, 128, 0, 0)
        data += b"\0\0\0\xff\xff\xff"
        for rectangle in rectangles:
            data += b"," + struct.pack("<HHHHB", *rectangle, 0) + b"\x02\x02D\x01\0"
        return data + b";"

    def rejected_before_decoder(self, contents: bytes) -> None:
        """No Pillow open/seek may precede rejection of invalid GIF structure."""
        path = self.root / "untrusted.gif"
        path.write_bytes(contents)
        with patch.object(safety.Image, "open") as decode:
            with self.assertRaises(SystemExit):
                safety.load_preview(path)
            decode.assert_not_called()

    def test_valid_preview_scales_and_report_contract(self) -> None:
        """All supported scales retain geometry, timing and alpha validation."""
        for scale in range(1, 5):
            with self.subTest(scale=scale):
                result = renderer.validate_preview(self.gif(scale), scale)
                self.assertEqual(result["width"], 192 * scale)
                self.assertEqual(result["height"], 208 * scale)
                self.assertEqual(result["frames"], 6)
                self.assertEqual(result["durations"], renderer.IDLE_DURATIONS)
                self.assertEqual(result["loop"], 0)
                self.assertEqual(result["disposal"], 2)

    def test_extra_frames_rejected_before_any_decode(self) -> None:
        self.rejected_before_decoder(self.gif(frames=7).read_bytes())

    def test_missing_frames_rejected_before_any_decode(self) -> None:
        self.rejected_before_decoder(self.gif(frames=5).read_bytes())

    def test_initial_canvas_bound_precedes_decoder(self) -> None:
        for width, height in ((960, 1040), (192, 65535), (0, 208), (193, 208)):
            with self.subTest(size=(width, height)):
                data = bytearray(self.gif().read_bytes())
                struct.pack_into("<HH", data, 6, width, height)
                self.rejected_before_decoder(bytes(data))

    def test_each_frame_rectangle_is_checked_before_pillow_seek(self) -> None:
        for rectangle in ((0, 0, 65535, 208), (191, 0, 2, 208), (0, 207, 192, 2), (0, 0, 0, 208)):
            for index in (0, 5):
                with self.subTest(rectangle=rectangle, index=index):
                    rectangles = [(0, 0, 1, 1)] * 6
                    rectangles[index] = rectangle
                    self.rejected_before_decoder(self.encoded_gif(rectangles))

    def test_wrong_format_and_truncated_blocks_rejected_before_decoder(self) -> None:
        valid = self.gif().read_bytes()
        for contents in (b"not a GIF", valid[:12], valid[:-1], self.encoded_gif([(0, 0, 1, 1)] * 6)[:-4]):
            with self.subTest(length=len(contents)):
                self.rejected_before_decoder(contents)

    def test_malformed_extension_cannot_hide_an_oversized_descriptor(self) -> None:
        header = self.encoded_gif([])[:-1]
        hidden = bytearray(b"," + struct.pack("<HHHHB", 0, 0, 1, 1, 0) + b"\x02\x64" + b"\0" * 100 + b"\0")
        hidden[45] = 0
        hidden[46:57] = b"," + struct.pack("<HHHHB", 0, 0, 9000, 9000, 0) + b"\x02"
        small = self.encoded_gif([(0, 0, 1, 1)] * 5)[19:]
        for malformed in (b"!\xf9\0", b"!\xff\0", b"!\x01\0", b"!\xff\x0bNETSCAPE2.0\0"):
            with self.subTest(extension=malformed):
                self.rejected_before_decoder(header + b"!\xf9\x04\x08\0\0\0\0" + malformed + hidden + small)

    def test_valid_extension_forms_remain_supported(self) -> None:
        data = self.encoded_gif([(0, 0, 1, 1)] * 6)
        for extension in (b"!\xfe\0", b"!\xfe\x03abc\0", b"!\xff\x0bTESTAPP1000\0",
                          b"!\x01\x0c" + b"\0" * 12 + b"\0",
                          b"!\xff\x0bNETSCAPE2.0\x03\x01\0\0\0"):
            path = self.root / "extensions.gif"
            path.write_bytes(data[:19] + extension + data[19:])
            with self.subTest(extension=extension):
                self.assertEqual(len(safety.load_preview(path).frames), 6)

    def test_encoded_size_limit_precedes_decoder(self) -> None:
        path = self.gif()
        with patch.object(safety, "MAX_PREVIEW_BYTES", path.stat().st_size - 1):
            with patch.object(safety.Image, "open") as decode:
                with self.assertRaises(SystemExit):
                    safety.load_preview(path)
                decode.assert_not_called()

    @unittest.skipUnless(hasattr(os, "mkfifo"), "requires POSIX named pipes")
    def test_non_regular_input_rejected_without_waiting_for_a_writer(self) -> None:
        path = self.root / "pipe.gif"
        os.mkfifo(path)
        with self.assertRaisesRegex(SystemExit, "regular file"):
            safety.load_preview(path)

    def test_scale_mismatch_rejected_before_decoder(self) -> None:
        path = self.gif()
        for scale in (0, 2, 5, True):
            with self.subTest(scale=scale), patch.object(safety.Image, "open") as decode:
                with self.assertRaises(SystemExit):
                    safety.load_preview(path, scale)
                decode.assert_not_called()

    def test_timing_disposal_loop_and_alpha_checks_remain(self) -> None:
        for field, value in (("durations", [100] * 6), ("disposals", [1] * 6), ("loop", 1)):
            preview = safety.load_preview(self.gif())
            setattr(preview, field, value)
            with self.subTest(field=field), self.assertRaises(SystemExit):
                renderer.validate_preview_data(preview)
        preview = safety.load_preview(self.gif())
        preview.frames[0].putalpha(255)
        with self.assertRaises(SystemExit):
            renderer.validate_preview_data(preview)

    def test_png_and_webp_atlases_remain_supported(self) -> None:
        image = Image.new("RGBA", renderer.ATLAS_SIZE, (100, 20, 30, 0))
        image.putpixel((10, 10), (100, 20, 30, 255))
        for extension, lossless in (("png", False), ("webp", False), ("webp", True)):
            path = self.root / f"atlas.{extension}"
            image.save(path, lossless=lossless)
            with self.subTest(extension=extension, lossless=lossless):
                frames = renderer.load_idle_frames(path, 192, 1)
                self.assertEqual(len(frames), 6)
                self.assertTrue(all(frame.size == (192, 208) for frame in frames))

    def test_direct_renderer_arguments_fail_before_image_read(self) -> None:
        for threshold, scale in ((192, 5), (192, True), (0, 1), (256, 1)):
            with self.subTest(threshold=threshold, scale=scale), patch.object(renderer, "load_static_image") as load:
                with self.assertRaises(SystemExit):
                    renderer.load_idle_frames(self.root / "absent.webp", threshold, scale)
                load.assert_not_called()

    def test_static_geometry_and_animation_fail_before_pixel_conversion(self) -> None:
        wrong_size = self.root / "wrong.png"
        Image.new("RGBA", (193, 208)).save(wrong_size)
        animated = self.root / "animated.png"
        Image.new("RGBA", (192, 208), "red").save(
            animated, save_all=True, append_images=[Image.new("RGBA", (192, 208), "blue")], duration=100,
        )
        for path in (wrong_size, animated):
            with self.subTest(path=path.name), patch.object(Image.Image, "convert") as convert:
                with self.assertRaises(SystemExit):
                    safety.load_static_image(path, formats=["PNG"], max_bytes=1024 * 1024, expected_size=(192, 208))
                convert.assert_not_called()

    def test_webp_canvas_is_bounded_before_native_decoder_creation(self) -> None:
        path = self.root / "atlas.webp"
        for lossless in (False, True):
            Image.new("RGBA", (192, 208), (1, 2, 3, 128)).save(path, lossless=lossless)
            with self.subTest(lossless=lossless), patch.object(safety.Image, "open") as decode:
                with self.assertRaises(SystemExit):
                    renderer.load_idle_frames(path, 192, 1)
                decode.assert_not_called()

    def test_animated_webp_rejected_before_native_decoder_creation(self) -> None:
        path = self.root / "animated.webp"
        Image.new("RGBA", (192, 208), "red").save(
            path, save_all=True, append_images=[Image.new("RGBA", (192, 208), "blue")], duration=100,
        )
        with patch.object(safety.Image, "open") as decode:
            with self.assertRaises(SystemExit):
                safety.load_static_image(path, formats=["WEBP"], max_bytes=1024 * 1024, expected_size=(192, 208))
            decode.assert_not_called()

    def test_webp_container_and_bitstream_must_agree(self) -> None:
        path = self.root / "mismatch.webp"
        Image.new("RGBA", (192, 208), (1, 2, 3, 128)).save(path)
        original = path.read_bytes()
        self.assertEqual(original[12:16], b"VP8X")
        mismatch = bytearray(original)
        mismatch[24:27] = (191).to_bytes(3, "little")
        mismatch[27:30] = (207).to_bytes(3, "little")
        position = original.index(b"VP8 ") + 8
        mismatch[position + 6:position + 8] = (16383).to_bytes(2, "little")
        for contents in (bytes(mismatch), original[:-1], original + b"trailing"):
            path.write_bytes(contents)
            with self.subTest(length=len(contents)), patch.object(safety.Image, "open") as decode:
                with self.assertRaises(SystemExit):
                    safety.load_static_image(path, formats=["WEBP"], max_bytes=1024 * 1024, expected_size=(192, 208))
                decode.assert_not_called()

    def test_atlas_requires_alpha(self) -> None:
        path = self.root / "opaque.png"
        Image.new("RGB", renderer.ATLAS_SIZE).save(path)
        with patch.object(Image.Image, "convert") as convert:
            with self.assertRaisesRegex(SystemExit, "alpha"):
                renderer.load_idle_frames(path, 192, 1)
            convert.assert_not_called()

    def test_static_loader_rejects_renamed_formats_and_oversized_logo(self) -> None:
        renamed = self.root / "still.png"
        Image.new("RGB", (192, 208)).save(renamed, format="JPEG")
        with self.assertRaises(UnidentifiedImageError):
            safety.load_static_image(renamed, formats=["PNG"], max_bytes=1024 * 1024, expected_size=(192, 208))
        logo = self.root / "logo.png"
        Image.new("RGBA", (2049, 1)).save(logo)
        with patch.object(Image.Image, "convert") as convert:
            with self.assertRaises(SystemExit):
                safety.load_static_image(logo, formats=["PNG"], max_bytes=1024 * 1024, max_size=(2048, 2048))
            convert.assert_not_called()

    def test_thin_strip_cannot_trigger_header_resize_amplification(self) -> None:
        frame = Image.new("RGBA", (768, 832))
        frame.paste((255, 0, 0, 255), (0, 0, 768, 1))
        preview = safety.Preview([frame] * 6, renderer.IDLE_DURATIONS, [2] * 6, 0, 4)
        with patch.object(header, "load_preview", return_value=preview), patch.object(Image.Image, "resize") as resize:
            with self.assertRaisesRegex(SystemExit, "aspect ratio"):
                header.load_pet_frames({"previewPath": "unused.gif"}, header.PLACEMENTS["bella"])
            resize.assert_not_called()

    def test_header_consumer_uses_the_same_early_frame_gate(self) -> None:
        path = self.gif(frames=7)
        with patch.object(safety.Image, "open") as decode:
            with self.assertRaises(SystemExit):
                header.load_pet_frames({"previewPath": str(path)}, header.PLACEMENTS["bella"])
            decode.assert_not_called()


if __name__ == "__main__":
    unittest.main()
