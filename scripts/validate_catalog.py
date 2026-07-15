#!/usr/bin/env python3
"""Validate the canonical Codex Pets catalogue and every repeated public surface."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "site"
SITE_BASE_URL = "https://senyo888.github.io/codex-pets"
RAW_BASE_URL = "https://raw.githubusercontent.com/senyo888/codex-pets/main"
CATALOG_SCHEMA_VERSION = 2
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NUMBER_PATTERN = re.compile(r"^[0-9]{3,}$")
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
PACKAGE_HEADING = "## Package"
PACKAGE_PROPERTY_ORDER = (
    "Pet id",
    "Sprite contract",
    "Atlas",
    "Cell size",
    "Animation rows",
    "SHA-256",
)
CATALOG_KEYS = {"schemaVersion", "pets"}
PET_KEYS = {
    "catalogueNumber",
    "publicationState",
    "id",
    "displayName",
    "description",
    "spriteVersionNumber",
    "spritesheetPath",
    "previewPath",
    "installPage",
    "sha256",
    "presentation",
}
PRESENTATION_KEYS = {"shortRole", "summary", "traits", "previewAlt"}
METADATA_KEYS = {
    "id",
    "displayName",
    "description",
    "spriteVersionNumber",
    "spritesheetPath",
}
TABLE_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|$")
MARKDOWN_REFERENCE = re.compile(
    r"!?\[[^\]]*\]\(([^)]+)\)|<img\s+[^>]*src=[\"']([^\"']+)", re.I
)


class References(HTMLParser):
    """Collect local reference attributes from parsed HTML."""

    def __init__(self) -> None:
        """Initialize an empty reference collection."""
        super().__init__()
        self.values: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Record href and src values from an HTML start tag."""
        values = dict(attrs)
        for key in ("href", "src"):
            if values.get(key):
                self.values.append(values[key] or "")


def add_error(errors: list[str], message: str) -> None:
    """Append one deterministic validation error."""
    errors.append(message)


def sha256(path: Path) -> str:
    """Return the lowercase SHA-256 digest for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path, errors: list[str]) -> object | None:
    """Read JSON while converting parse and file errors into validation errors."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        add_error(errors, f"invalid JSON: {path.relative_to(ROOT)}: {error}")
        return None


def exact_keys(
    value: dict[str, object], expected: set[str], label: str, errors: list[str]
) -> bool:
    """Require an object to contain exactly the expected keys."""
    actual = set(value)
    if actual == expected:
        return True
    missing = ", ".join(sorted(expected - actual)) or "none"
    extra = ", ".join(sorted(actual - expected)) or "none"
    add_error(errors, f"{label} keys mismatch: missing [{missing}], extra [{extra}]")
    return False


def nonempty_string(value: object) -> bool:
    """Return whether a value is a non-empty string after trimming."""
    return isinstance(value, str) and bool(value.strip())


def validate_catalog_shape(catalog: object, errors: list[str]) -> bool:
    """Validate the schema-v2 catalogue structure and entry identity fields."""
    start = len(errors)
    if not isinstance(catalog, dict):
        add_error(errors, "catalog root must be an object")
        return False
    exact_keys(catalog, CATALOG_KEYS, "catalog", errors)
    if catalog.get("schemaVersion") != CATALOG_SCHEMA_VERSION:
        add_error(
            errors,
            f"catalog schemaVersion must be {CATALOG_SCHEMA_VERSION}",
        )
    pets = catalog.get("pets")
    if not isinstance(pets, list) or not pets:
        add_error(errors, "catalog pets must be a non-empty array")
        return False

    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    seen_numbers: set[str] = set()
    numbers: list[int] = []

    for index, pet in enumerate(pets):
        label = f"catalog pet at index {index}"
        if not isinstance(pet, dict):
            add_error(errors, f"{label} must be an object")
            continue
        exact_keys(pet, PET_KEYS, label, errors)
        pet_id = pet.get("id")
        name = pet.get("displayName")
        number = pet.get("catalogueNumber")
        state = pet.get("publicationState")
        presentation = pet.get("presentation")

        if not nonempty_string(pet_id) or not ID_PATTERN.fullmatch(str(pet_id)):
            add_error(errors, f"{label} has invalid id: {pet_id!r}")
        elif str(pet_id) in seen_ids:
            add_error(errors, f"duplicate catalog id: {pet_id}")
        else:
            seen_ids.add(str(pet_id))

        if not nonempty_string(name):
            add_error(errors, f"{label} displayName must be a non-empty string")
        elif str(name).casefold() in seen_names:
            add_error(errors, f"duplicate displayName ignoring case: {name}")
        else:
            seen_names.add(str(name).casefold())

        if not nonempty_string(number) or not NUMBER_PATTERN.fullmatch(str(number)):
            add_error(errors, f"{label} has invalid catalogueNumber: {number!r}")
        elif str(number) in seen_numbers:
            add_error(errors, f"duplicate catalogueNumber: {number}")
        else:
            seen_numbers.add(str(number))
            numbers.append(int(str(number)))

        if state != "published":
            add_error(
                errors,
                f"{label} publicationState must be 'published'; retirement requires a contract update",
            )
        if not nonempty_string(pet.get("description")):
            add_error(errors, f"{label} description must be a non-empty string")
        if not isinstance(pet.get("spriteVersionNumber"), int):
            add_error(errors, f"{label} spriteVersionNumber must be an integer")
        if not isinstance(presentation, dict):
            add_error(errors, f"{label} presentation must be an object")
        else:
            exact_keys(presentation, PRESENTATION_KEYS, f"{label} presentation", errors)
            for key in ("shortRole", "summary", "previewAlt"):
                if not nonempty_string(presentation.get(key)):
                    add_error(errors, f"{label} presentation.{key} must be non-empty")
            traits = presentation.get("traits")
            if (
                not isinstance(traits, list)
                or len(traits) != 3
                or any(not nonempty_string(trait) for trait in traits)
                or len({str(trait).casefold() for trait in traits}) != 3
            ):
                add_error(errors, f"{label} presentation.traits must contain 3 unique strings")
            if nonempty_string(name) and nonempty_string(presentation.get("previewAlt")):
                if str(name).casefold() not in str(presentation["previewAlt"]).casefold():
                    add_error(errors, f"{label} previewAlt must name the pet")

        if not nonempty_string(pet.get("sha256")) or not SHA256_PATTERN.fullmatch(
            str(pet.get("sha256", ""))
        ):
            add_error(errors, f"{label} sha256 must be 64 lowercase hexadecimal characters")

    if numbers != sorted(numbers):
        add_error(errors, "catalog pets must be sorted by ascending catalogueNumber")
    return len(errors) == start


def compare_membership(
    label: str, actual: set[str], expected: set[str], errors: list[str]
) -> None:
    """Record missing and extra members for a repeated catalogue surface."""
    if actual == expected:
        return
    missing = ", ".join(sorted(expected - actual)) or "none"
    extra = ", ".join(sorted(actual - expected)) or "none"
    add_error(errors, f"{label} membership mismatch: missing [{missing}], extra [{extra}]")


def package_properties(readme: Path, errors: list[str]) -> dict[str, str]:
    """Parse and validate the canonical Package table in a pet README."""
    lines = readme.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index(PACKAGE_HEADING) + 1
    except ValueError:
        add_error(errors, f"missing Package section: {readme.relative_to(ROOT)}")
        return {}

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
        add_error(
            errors,
            f"non-canonical Package properties in {readme.relative_to(ROOT)}: "
            f"expected [{expected}], found [{actual}]",
        )
    return dict(rows)


def expected_install_values(pet: dict[str, object]) -> dict[str, str]:
    """Derive the canonical installer query values for one pet."""
    pet_id = str(pet["id"])
    return {
        "name": str(pet["displayName"]),
        "imageUrl": f"{RAW_BASE_URL}/pets/{pet_id}/spritesheet.webp",
        "description": str(pet["description"]),
        "spriteVersionNumber": str(pet["spriteVersionNumber"]),
    }


def validate_deep_link(
    text: str, pet: dict[str, object], label: str, errors: list[str]
) -> None:
    """Validate one installer deep link against canonical package metadata."""
    decoded = html.unescape(text)
    matches = re.findall(r"codex://pets/install\?[^\s\"<]+", decoded)
    if len(matches) != 1:
        add_error(errors, f"{label} must contain exactly one codex installer link")
        return
    parsed = parse_qs(urlsplit(matches[0]).query, keep_blank_values=True)
    if any(len(values) != 1 for values in parsed.values()):
        add_error(errors, f"{label} installer query contains duplicate parameters")
        return
    actual = {key: values[0] for key, values in parsed.items()}
    expected = expected_install_values(pet)
    if actual != expected:
        add_error(errors, f"{label} installer query does not match canonical package metadata")


def validate_package(
    pet: dict[str, object], errors: list[str]
) -> tuple[str, str]:
    """Validate one package and return its README and site preview tokens."""
    pet_id = str(pet["id"])
    metadata_path = ROOT / "pets" / pet_id / "pet.json"
    spritesheet = ROOT / str(pet["spritesheetPath"])
    preview = ROOT / str(pet["previewPath"])
    readme = ROOT / "pets" / pet_id / "README.md"
    validation = ROOT / "pets" / pet_id / "qa" / "validation-summary.json"
    site_preview = SITE_ROOT / "assets" / f"{pet_id}-preview.gif"
    installer = SITE_ROOT / "install" / pet_id / "index.html"
    required_paths = (
        metadata_path,
        spritesheet,
        preview,
        readme,
        validation,
        ROOT / "pets" / pet_id / "qa" / "contact-sheet.png",
        ROOT / "pets" / pet_id / "qa" / "look-directions.png",
        site_preview,
        installer,
    )
    for path in required_paths:
        if not path.is_file():
            add_error(errors, f"missing catalog artifact: {path.relative_to(ROOT)}")
    if any(not path.is_file() for path in required_paths):
        return "", ""

    expected_paths = {
        "spritesheetPath": f"pets/{pet_id}/spritesheet.webp",
        "previewPath": f"pets/{pet_id}/preview.gif",
        "installPage": f"{SITE_BASE_URL}/install/{pet_id}/",
    }
    for key, expected in expected_paths.items():
        if pet[key] != expected:
            add_error(errors, f"non-canonical {key} for {pet_id}: expected {expected}")

    metadata = read_json(metadata_path, errors)
    if isinstance(metadata, dict):
        exact_keys(metadata, METADATA_KEYS, f"pets/{pet_id}/pet.json", errors)
        expected_metadata = {
            "id": pet_id,
            "displayName": pet["displayName"],
            "description": pet["description"],
            "spriteVersionNumber": pet["spriteVersionNumber"],
            "spritesheetPath": "spritesheet.webp",
        }
        if metadata != expected_metadata:
            add_error(errors, f"package metadata mismatch: {pet_id}")

    actual_hash = sha256(spritesheet)
    if actual_hash != pet["sha256"]:
        add_error(errors, f"spritesheet hash mismatch: {pet_id}")

    summary = read_json(validation, errors)
    if isinstance(summary, dict):
        expected_core = {
            "ok": True,
            "petId": pet_id,
            "spriteVersionNumber": pet["spriteVersionNumber"],
            "format": "WEBP",
            "mode": "RGBA",
            "width": 1536,
            "height": 2288,
            "columns": 8,
            "rows": 11,
            "sha256": actual_hash,
        }
        for key, expected in expected_core.items():
            if summary.get(key) != expected:
                add_error(errors, f"validation summary {key} mismatch: {pet_id}")
        atlas = summary.get("atlasValidation")
        if not isinstance(atlas, dict):
            add_error(errors, f"validation summary atlasValidation missing: {pet_id}")
        else:
            for key, expected in (("ok", True), ("errors", 0), ("warnings", 0)):
                if atlas.get(key) != expected:
                    add_error(errors, f"validation summary atlasValidation.{key} mismatch: {pet_id}")

    readme_text = readme.read_text(encoding="utf-8")
    properties = package_properties(readme, errors)
    expected_properties = {
        "Pet id": f"`{pet_id}`",
        "Sprite contract": f"v{pet['spriteVersionNumber']}",
        "Atlas": "`1536 × 2288` WebP",
        "Cell size": "`192 × 208`",
        "Animation rows": "9 standard + 2 look-direction rows",
        "SHA-256": f"`{actual_hash}`",
    }
    if properties != expected_properties:
        add_error(errors, f"Package property value mismatch: {pet_id}")

    package_token = sha256(preview)[:12]
    alt = str(pet["presentation"]["previewAlt"])
    expected_preview = (
        f'<img src="preview.gif?v={package_token}" alt="{alt}" width="240">'
    )
    if expected_preview not in readme_text:
        add_error(errors, f"per-pet README preview contract mismatch: {pet_id}")
    if f"[**Install {pet['displayName']}**]({pet['installPage']})" not in readme_text:
        add_error(errors, f"per-pet README install page mismatch: {pet_id}")
    validate_deep_link(readme_text, pet, f"pets/{pet_id}/README.md", errors)

    return package_token, sha256(site_preview)[:12]


def validate_root_readme(
    pets: list[dict[str, object]], package_tokens: dict[str, str], errors: list[str]
) -> None:
    """Validate all catalogue-derived surfaces in the root README."""
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    count = len(pets)

    badge_counts = re.findall(r"badge/pets-([0-9]+)-", text)
    if badge_counts != [str(count)]:
        add_error(errors, "README pet-count badge mismatch")

    hero = re.findall(
        (
            r'<a href="pets/([^/]+)/README\.md"><img '
            r'src="pets/([^/]+)/preview\.gif\?v=([0-9a-f]+)" '
            r'alt="([^"]+)" width="150"></a>'
        ),
        text,
    )
    expected_hero = [
        (
            str(pet["id"]),
            str(pet["id"]),
            package_tokens[str(pet["id"])],
            str(pet["presentation"]["previewAlt"]),
        )
        for pet in pets
    ]
    if hero != expected_hero:
        add_error(errors, "README hero previews differ from canonical catalogue order or metadata")

    rollup_match = re.search(r"^## (.+\(pets/.+/README\.md\).*)$", text, re.M)
    rollup = (
        re.findall(r"\[([^\]]+)\]\(pets/([^/]+)/README\.md\)", rollup_match.group(1))
        if rollup_match
        else []
    )
    expected_rollup = [(str(pet["displayName"]), str(pet["id"])) for pet in pets]
    if rollup != expected_rollup:
        add_error(errors, "README linked-name roll-up mismatch")

    collection_total = (
        f"*{count} distinct companions, each shipped as a transparent "
        "and inspectable v2 package.*"
    )
    if collection_total not in text:
        add_error(errors, "README collection-total sentence mismatch")

    collection_rows = re.findall(
        (
            r"^\| ([0-9]{3,}) \| \[\*\*(.+?)\*\*\]\(pets/([^/]+)/README\.md\) "
            r"\| (.*?) \| Sprite v([0-9]+) \| Validated and ready \|$"
        ),
        text,
        re.M,
    )
    expected_collection = [
        (
            str(pet["catalogueNumber"]),
            str(pet["displayName"]),
            str(pet["id"]),
            str(pet["presentation"]["summary"]),
            str(pet["spriteVersionNumber"]),
        )
        for pet in pets
    ]
    if collection_rows != expected_collection:
        add_error(errors, "README collection table mismatch")

    installer_rows = re.findall(
        (
            r"^\| ([^|]+?) \| `([^`]+)` \| \[Open installer\]\((https://[^)]+)\) "
            r"\| \[Read README\]\(pets/([^/]+)/README\.md\) \|$"
        ),
        text,
        re.M,
    )
    expected_installers = [
        (
            str(pet["displayName"]),
            str(pet["id"]),
            str(pet["installPage"]),
            str(pet["id"]),
        )
        for pet in pets
    ]
    if installer_rows != expected_installers:
        add_error(errors, "README installer table mismatch")
    if "PET_ID=aetherwing # choose an ID from the table above" not in text:
        add_error(errors, "README manual-install ID guidance mismatch")
    if f"All {count} published pets ship as exact `1536 × 2288` RGBA WebP atlases." not in text:
        add_error(errors, "README quality total mismatch")

    checksum_rows = re.findall(
        r"^\| ([^|]+?) \| `([0-9a-f]{64})` \| \[Summary\]\(pets/([^/]+)/qa/validation-summary\.json\) \|$",
        text,
        re.M,
    )
    expected_checksums = [
        (str(pet["displayName"]), str(pet["sha256"]), str(pet["id"]))
        for pet in pets
    ]
    if checksum_rows != expected_checksums:
        add_error(errors, "README checksum table mismatch")


def text_value(value: object) -> str:
    """Escape a catalogue value for safe HTML text comparison."""
    return html.escape(str(value), quote=False)


def validate_site_index(
    pets: list[dict[str, object]], site_tokens: dict[str, str], errors: list[str]
) -> None:
    """Validate landing-page cards against canonical catalogue presentation."""
    path = SITE_ROOT / "index.html"
    text = path.read_text(encoding="utf-8")
    count_match = re.search(r"<dt>Published pets</dt><dd>([0-9]+)</dd>", text)
    if not count_match or count_match.group(1) != str(len(pets)):
        add_error(errors, "site published-pet count mismatch")

    cards = re.findall(
        r'(<article class="pet-card pet-([^"]+)" data-pet-id="([^"]+)"[\s\S]*?</article>)',
        text,
    )
    actual_ids = [(class_id, data_id) for _block, class_id, data_id in cards]
    expected_ids = [(str(pet["id"]), str(pet["id"])) for pet in pets]
    if actual_ids != expected_ids:
        add_error(errors, "site card membership, order, class, or data-pet-id mismatch")
        return

    for (block, _class_id, _data_id), pet in zip(cards, pets):
        pet_id = str(pet["id"])
        presentation = pet["presentation"]
        token = site_tokens[pet_id]
        required_snippets = (
            f'src="./assets/{pet_id}-preview.gif?v={token}" alt="{presentation["previewAlt"]}"',
            f'<p class="pet-number">Pet {pet["catalogueNumber"]}</p>',
            f'id="{pet_id}-title"',
            f'>{text_value(pet["displayName"])}</a></h2>',
            f'Validated v{pet["spriteVersionNumber"]}',
            f'<p class="pet-role">{text_value(presentation["shortRole"])}</p>',
            f'<p class="pet-description">{text_value(presentation["summary"])}</p>',
            f'href="./install/{pet_id}/">Install {text_value(pet["displayName"])}</a>',
        )
        for snippet in required_snippets:
            if snippet not in block:
                add_error(errors, f"site card contract mismatch for {pet_id}: missing {snippet}")
        traits_match = re.search(r'<ul class="pet-traits"[^>]*>([\s\S]*?)</ul>', block)
        traits = re.findall(r"<li>(.*?)</li>", traits_match.group(1)) if traits_match else []
        if traits != [text_value(trait) for trait in presentation["traits"]]:
            add_error(errors, f"site card traits mismatch: {pet_id}")
        readme_url = f"https://github.com/senyo888/codex-pets/blob/main/pets/{pet_id}/README.md"
        if block.count(f'href="{readme_url}"') != 2:
            add_error(errors, f"site card README actions mismatch: {pet_id}")

    contribution_position = text.find('class="contribution-card"')
    last_card_position = text.rfind('</article>', 0, contribution_position)
    if contribution_position < 0 or last_card_position < 0:
        add_error(errors, "contribution card must follow all published pet cards")


def validate_installer(
    pet: dict[str, object], site_token: str, errors: list[str]
) -> None:
    """Validate one installer page against canonical package and site truth."""
    pet_id = str(pet["id"])
    name = str(pet["displayName"])
    path = SITE_ROOT / "install" / pet_id / "index.html"
    text = path.read_text(encoding="utf-8")
    readme_url = f"https://github.com/senyo888/codex-pets/blob/main/pets/{pet_id}/README.md"
    required_snippets = (
        (
            f'<meta name="description" content="Install {name}, a custom animated '
            f'v{pet["spriteVersionNumber"]} pet for the Codex desktop app.">'
        ),
        f"<title>Install {name} · Codex Pets</title>",
        f'data-pet-id="{pet_id}"',
        f'href="{readme_url}">Read README</a>',
        f'src="../../assets/{pet_id}-preview.gif?v={site_token}" alt="{pet["presentation"]["previewAlt"]}"',
        f'<p class="eyebrow">Pet {pet["catalogueNumber"]} · sprite v{pet["spriteVersionNumber"]}</p>',
        f"<h1>Wake {name}?</h1>",
        f"<p>{text_value(pet['description'])}</p>",
        f'id="install-{pet_id}"',
        f'href="{RAW_BASE_URL}/pets/{pet_id}/pet.json">Download pet.json</a>',
        f'href="{RAW_BASE_URL}/pets/{pet_id}/spritesheet.webp">Download spritesheet.webp</a>',
    )
    for snippet in required_snippets:
        if snippet not in text:
            add_error(errors, f"installer contract mismatch for {pet_id}: missing {snippet}")
    validate_deep_link(text, pet, f"site/install/{pet_id}/index.html", errors)


def validate_html_references(errors: list[str]) -> int:
    """Validate local site references and return the number inspected."""
    checked = 0
    for page in sorted(SITE_ROOT.rglob("*.html")):
        parser = References()
        parser.feed(page.read_text(encoding="utf-8"))
        for reference in parser.values:
            if reference.startswith(("#", "http://", "https://", "codex:", "mailto:")):
                continue
            clean = reference.split("#", 1)[0].split("?", 1)[0]
            target = (page.parent / clean).resolve()
            if target.is_dir():
                target /= "index.html"
            checked += 1
            if not target.is_relative_to(SITE_ROOT.resolve()):
                add_error(
                    errors,
                    f"site reference escapes site root: {page.relative_to(ROOT)} -> {reference}",
                )
            elif not target.exists():
                add_error(errors, f"broken local site reference: {page.relative_to(ROOT)} -> {reference}")
    return checked


def validate_markdown_references(errors: list[str]) -> int:
    """Validate local Markdown references and return the number inspected."""
    checked = 0
    for page in sorted(ROOT.rglob("*.md")):
        text = page.read_text(encoding="utf-8")
        for match in MARKDOWN_REFERENCE.finditer(text):
            reference = next(value for value in match.groups() if value)
            reference = reference.strip().split()[0].strip("<>")
            if reference.startswith(("#", "http://", "https://", "codex:", "mailto:")):
                continue
            clean = reference.split("#", 1)[0].split("?", 1)[0]
            target = (page.parent / clean).resolve()
            checked += 1
            if not target.is_relative_to(ROOT):
                add_error(
                    errors,
                    f"Markdown reference escapes repository: {page.relative_to(ROOT)} -> {reference}",
                )
            elif not target.exists():
                add_error(errors, f"broken local Markdown reference: {page.relative_to(ROOT)} -> {reference}")
    return checked


def validate_stable_identity(
    base_ref: str, pets: list[dict[str, object]], errors: list[str]
) -> None:
    """Reject removal or renumbering of published pets relative to a base ref."""
    result = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{base_ref}:catalog.json"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        add_error(errors, f"could not read base catalogue at {base_ref}")
        return
    try:
        base_catalog = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        add_error(errors, f"base catalogue is invalid JSON: {error}")
        return
    base_pets = base_catalog.get("pets", []) if isinstance(base_catalog, dict) else []
    current_by_id = {str(pet["id"]): pet for pet in pets}
    base_ids: set[str] = set()
    base_numbers: list[int] = []
    for index, base_pet in enumerate(base_pets, 1):
        if not isinstance(base_pet, dict) or "id" not in base_pet:
            continue
        pet_id = str(base_pet["id"])
        base_ids.add(pet_id)
        base_number = str(base_pet.get("catalogueNumber", f"{index:03d}"))
        if NUMBER_PATTERN.fullmatch(base_number):
            base_numbers.append(int(base_number))
        if pet_id not in current_by_id:
            add_error(errors, f"published pet id removed instead of retained or retired: {pet_id}")
            continue
        if current_by_id[pet_id]["catalogueNumber"] != base_number:
            add_error(errors, f"published catalogueNumber changed for {pet_id}")

    highest_base_number = max(base_numbers, default=0)
    for pet_id, pet in current_by_id.items():
        if pet_id not in base_ids and int(str(pet["catalogueNumber"])) <= highest_base_number:
            add_error(errors, f"new pet {pet_id} must use a catalogueNumber above existing numbers")


def main() -> int:
    """Run the complete catalogue contract validation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-ref",
        help="Optional base commit used to reject removal or renumbering of published pets.",
    )
    args = parser.parse_args()
    errors: list[str] = []
    catalog = read_json(ROOT / "catalog.json", errors)
    if catalog is None or not validate_catalog_shape(catalog, errors):
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    assert isinstance(catalog, dict)
    pets = catalog["pets"]
    assert isinstance(pets, list)
    typed_pets = [pet for pet in pets if isinstance(pet, dict)]
    ids = {str(pet["id"]) for pet in typed_pets}

    compare_membership(
        "package directories",
        {path.name for path in (ROOT / "pets").iterdir() if path.is_dir()},
        ids,
        errors,
    )
    compare_membership(
        "pet metadata",
        {path.parent.name for path in (ROOT / "pets").glob("*/pet.json")},
        ids,
        errors,
    )
    compare_membership(
        "pet READMEs",
        {path.parent.name for path in (ROOT / "pets").glob("*/README.md")},
        ids,
        errors,
    )
    compare_membership(
        "installer directories",
        {path.parent.name for path in (SITE_ROOT / "install").glob("*/index.html")},
        ids,
        errors,
    )
    compare_membership(
        "site preview assets",
        {
            path.name.removesuffix("-preview.gif")
            for path in (SITE_ROOT / "assets").glob("*-preview.gif")
        },
        ids,
        errors,
    )

    package_tokens: dict[str, str] = {}
    site_tokens: dict[str, str] = {}
    for pet in typed_pets:
        package_token, site_token = validate_package(pet, errors)
        package_tokens[str(pet["id"])] = package_token
        site_tokens[str(pet["id"])] = site_token

    validate_root_readme(typed_pets, package_tokens, errors)
    validate_site_index(typed_pets, site_tokens, errors)
    for pet in typed_pets:
        validate_installer(pet, site_tokens[str(pet["id"])], errors)

    html_checked = validate_html_references(errors)
    markdown_checked = validate_markdown_references(errors)
    if args.base_ref:
        validate_stable_identity(args.base_ref, typed_pets, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"catalog validation failed with {len(errors)} error(s)")
        return 1

    print(
        f"catalog contract: {len(typed_pets)} published pets, canonical README/site/installers, "
        f"{html_checked} local site references, {markdown_checked} local Markdown references, all passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
