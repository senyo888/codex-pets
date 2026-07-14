#!/usr/bin/env python3
"""Validate catalogue packages, README properties, hashes, and site references."""

from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_HEADING = "## Package"
PACKAGE_PROPERTY_ORDER = (
    "Pet id",
    "Sprite contract",
    "Atlas",
    "Cell size",
    "Animation rows",
    "SHA-256",
)
TABLE_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|$")


class References(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for key in ("href", "src"):
            if values.get(key):
                self.values.append(values[key] or "")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_properties(readme: Path) -> dict[str, str]:
    lines = readme.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index(PACKAGE_HEADING) + 1
    except ValueError as error:
        raise SystemExit(f"missing Package section: {readme.relative_to(ROOT)}") from error

    rows: list[tuple[str, str]] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        match = TABLE_ROW.match(line)
        if not match:
            continue
        name, value = (part.strip() for part in match.groups())
        if name == "Property" or set(name) == {"-"}:
            continue
        rows.append((name, value))

    names = tuple(name for name, _value in rows)
    if names != PACKAGE_PROPERTY_ORDER:
        expected = ", ".join(PACKAGE_PROPERTY_ORDER)
        actual = ", ".join(names) or "none"
        raise SystemExit(
            f"non-canonical Package properties in {readme.relative_to(ROOT)}: "
            f"expected [{expected}], found [{actual}]"
        )
    return dict(rows)


def main() -> int:
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    pets = catalog.get("pets", [])
    ids = [pet["id"] for pet in pets]
    if not pets or len(ids) != len(set(ids)):
        raise SystemExit("catalog must contain unique pet ids")

    readme_ids = {
        path.parent.name for path in (ROOT / "pets").glob("*/README.md")
    }
    if readme_ids != set(ids):
        raise SystemExit("catalog pet ids and pet README directories must match")

    for pet in pets:
        pet_id = pet["id"]
        metadata_path = ROOT / "pets" / pet_id / "pet.json"
        spritesheet = ROOT / pet["spritesheetPath"]
        preview = ROOT / pet["previewPath"]
        readme = ROOT / "pets" / pet_id / "README.md"
        validation = ROOT / "pets" / pet_id / "qa" / "validation-summary.json"
        installer = ROOT / "site" / "install" / pet_id / "index.html"
        site_preview = ROOT / "site" / "assets" / f"{pet_id}-preview.gif"
        for path in (
            metadata_path,
            spritesheet,
            preview,
            readme,
            validation,
            installer,
            site_preview,
        ):
            if not path.exists():
                raise SystemExit(f"missing catalog artifact: {path.relative_to(ROOT)}")

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata["id"] != pet_id or metadata["displayName"] != pet["displayName"]:
            raise SystemExit(f"metadata identity mismatch: {pet_id}")
        if metadata["description"] != pet["description"]:
            raise SystemExit(f"metadata description mismatch: {pet_id}")
        if metadata["spriteVersionNumber"] != pet["spriteVersionNumber"]:
            raise SystemExit(f"sprite version mismatch: {pet_id}")
        if metadata["spritesheetPath"] != spritesheet.name:
            raise SystemExit(f"metadata spritesheet path mismatch: {pet_id}")

        actual_hash = sha256(spritesheet)
        if actual_hash != pet["sha256"]:
            raise SystemExit(f"spritesheet hash mismatch: {pet_id}")
        validation_summary = json.loads(validation.read_text(encoding="utf-8"))
        if validation_summary.get("sha256") != actual_hash:
            raise SystemExit(f"validation summary hash mismatch: {pet_id}")

        properties = package_properties(readme)
        expected_properties = {
            "Pet id": f"`{pet_id}`",
            "Sprite contract": f"v{pet['spriteVersionNumber']}",
            "Atlas": "`1536 × 2288` WebP",
            "Cell size": "`192 × 208`",
            "Animation rows": "9 standard + 2 look-direction rows",
            "SHA-256": f"`{actual_hash}`",
        }
        if properties != expected_properties:
            raise SystemExit(f"Package property value mismatch: {pet_id}")

    checked = 0
    for page in sorted((ROOT / "site").rglob("*.html")):
        parser = References()
        parser.feed(page.read_text(encoding="utf-8"))
        for reference in parser.values:
            if reference.startswith(("#", "http://", "https://", "codex:", "mailto:")):
                continue
            target = (page.parent / reference.split("#", 1)[0].split("?", 1)[0]).resolve()
            if target.is_dir():
                target /= "index.html"
            checked += 1
            if not target.exists():
                raise SystemExit(
                    f"broken local site reference: {page.relative_to(ROOT)} -> {reference}"
                )

    print(
        f"catalog validation: {len(pets)} pets, canonical README properties, "
        f"{checked} local site references, all passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
