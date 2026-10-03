#!/usr/bin/env python3
"""Prove the Áureo exception cannot hide changed assets, findings or package gaps."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import validate_catalog as validator

SOURCE = Path(__file__).resolve().parents[1]
CATALOG = json.loads((SOURCE / "catalog.json").read_text(encoding="utf-8"))
PETS = {pet["id"]: pet for pet in CATALOG["pets"]}


class MaintainerExceptionTests(unittest.TestCase):
    """Exercise real package checks against disposable copies, never source files."""

    def setUp(self) -> None:
        """Copy the exception package and one ordinary package into a private fixture."""
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for pet_id in ("aureo", "bella"):
            shutil.copytree(SOURCE / "pets" / pet_id, self.root / "pets" / pet_id)
            shutil.copytree(
                SOURCE / "site/install" / pet_id, self.root / "site/install" / pet_id
            )
            (self.root / "site/assets").mkdir(parents=True, exist_ok=True)
            for suffix in ("gif", "png"):
                name = f"{pet_id}-preview.{suffix}"
                shutil.copy2(SOURCE / "site/assets" / name, self.root / "site/assets" / name)
        (self.root / "docs").mkdir()
        shutil.copy2(SOURCE / "docs/VALIDATION_EXCEPTIONS.md", self.root / "docs")
        roots = patch.multiple(validator, ROOT=self.root, SITE_ROOT=self.root / "site")
        roots.start()
        self.addCleanup(roots.stop)

    def read_summary(self, pet_id: str = "aureo") -> dict:
        """Read a fixture's public QA summary."""
        return json.loads((self.root / f"pets/{pet_id}/qa/validation-summary.json").read_text())

    def write_summary(self, summary: dict, pet_id: str = "aureo") -> None:
        """Write a deliberately modified summary to the disposable fixture."""
        (self.root / f"pets/{pet_id}/qa/validation-summary.json").write_text(json.dumps(summary))

    def errors(self, pet_id: str = "aureo", pet: dict | None = None) -> list[str]:
        """Run the real package validator and return every finding."""
        errors: list[str] = []
        validator.validate_package(pet or PETS[pet_id], errors)
        return errors

    def test_original_exception_and_ordinary_package_pass(self) -> None:
        """The accepted original and the untouched strict package both remain valid."""
        self.assertEqual(self.errors(), [])
        self.assertEqual(self.errors("bella"), [])
        summary = self.read_summary()
        self.assertIs(summary["ok"], False)
        self.assertEqual(summary["atlasValidation"]["errors"], 8)
        self.assertEqual(summary["directionValidation"]["cardinalGates"]["screenLeft"], "fail")

    def test_exception_cannot_be_copied_to_another_pet(self) -> None:
        """A flag copied into a different otherwise-valid package is rejected."""
        summary = self.read_summary("bella")
        summary["maintainerException"] = validator.AUREO_EXCEPTION
        self.write_summary(summary, "bella")
        self.assertIn("unrecognized maintainer exception: bella", self.errors("bella"))

    def test_changed_atlas_cannot_reuse_exception_even_with_updated_hashes(self) -> None:
        """Updating catalogue and summary hashes cannot authorize a different asset."""
        path = self.root / "pets/aureo/spritesheet.webp"
        path.write_bytes(path.read_bytes() + b"changed")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        pet = copy.deepcopy(PETS["aureo"])
        pet["sha256"] = digest
        summary = self.read_summary()
        summary["sha256"] = digest
        summary["maintainerException"]["atlasSha256"] = digest
        self.write_summary(summary)
        self.assertIn("unrecognized maintainer exception: aureo", self.errors(pet=pet))

    def test_failure_counts_and_cardinal_failure_cannot_be_erased(self) -> None:
        """A false clean bill of health is rejected even for the approved atlas."""
        summary = self.read_summary()
        summary["ok"] = True
        summary["atlasValidation"].update(ok=True, errors=0, chromaFringePixels=0)
        summary["directionValidation"]["cardinalGatesPassed"] = 4
        summary["directionValidation"]["cardinalGates"]["screenLeft"] = "pass"
        self.write_summary(summary)
        errors = self.errors()
        self.assertIn("validation summary ok mismatch: aureo", errors)
        self.assertIn("Áureo chroma findings mismatch", errors)
        self.assertIn("Áureo direction findings mismatch", errors)

    def test_independent_evidence_cannot_be_rewritten(self) -> None:
        """Changing the raw strict report invalidates its separately pinned digest."""
        path = self.root / "pets/aureo/qa/atlas-validation.json"
        evidence = json.loads(path.read_text())
        evidence["errors"] = []
        path.write_text(json.dumps(evidence))
        self.assertIn("Áureo strict atlas evidence is missing or changed", self.errors())

    def test_exception_cannot_hide_missing_artifacts(self) -> None:
        """Runtime files, previews, QA and the exception record remain mandatory."""
        for relative in (
            "pets/aureo/spritesheet.webp", "pets/aureo/pet.json",
            "pets/aureo/preview.png", "pets/aureo/qa/contact-sheet.png",
            "pets/aureo/qa/atlas-validation.json", "docs/VALIDATION_EXCEPTIONS.md",
        ):
            with self.subTest(path=relative):
                path = self.root / relative
                contents = path.read_bytes()
                path.unlink()
                try:
                    self.assertTrue(self.errors())
                finally:
                    path.write_bytes(contents)

    def test_corrupt_json_and_wrong_json_types_fail(self) -> None:
        """Invalid JSON and valid non-object JSON cannot bypass metadata or QA checks."""
        for relative in ("pets/aureo/pet.json", "pets/aureo/qa/validation-summary.json"):
            path = self.root / relative
            original = path.read_bytes()
            for contents in ("{broken", "null", "[]"):
                with self.subTest(path=relative, contents=contents):
                    path.write_text(contents)
                    try:
                        self.assertTrue(self.errors())
                    finally:
                        path.write_bytes(original)

    def test_explicit_exception_record_is_required(self) -> None:
        """The known atlas alone does not silently opt into an exception."""
        summary = self.read_summary()
        del summary["maintainerException"]
        self.write_summary(summary)
        self.assertIn("Áureo exception identity or atlas pin mismatch", self.errors())

    def test_other_pets_still_require_zero_strict_errors(self) -> None:
        """Without an exception, the existing strict acceptance bar is unchanged."""
        summary = self.read_summary("bella")
        summary["atlasValidation"].update(ok=False, errors=1)
        self.write_summary(summary, "bella")
        self.assertIn("validation summary atlasValidation.errors mismatch: bella", self.errors("bella"))


if __name__ == "__main__":
    unittest.main()
