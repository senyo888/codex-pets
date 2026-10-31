#!/usr/bin/env python3
"""Exercise Gitleaks against disposable repositories and synthetic credentials."""

from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from scan_secrets import ROOT


class SecretScanTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="pets-secret-tests-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.token = "ghp_" + hashlib.sha256(b"codex-pets-synthetic-test-only").hexdigest()[:36]
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Scanner fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        hooks = self.root / ".git" / "empty-hooks"
        hooks.mkdir()
        self.git("config", "core.hooksPath", str(hooks))
        shutil.copyfile(ROOT / ".gitleaks.toml", self.root / ".gitleaks.toml")
        (self.root / ".gitignore").write_text("private/\n", encoding="utf-8")
        (self.root / "README.md").write_text("Clean fixture.\n", encoding="utf-8")
        self.commit("Clean fixture")

    def git(self, *arguments: str) -> None:
        subprocess.run(
            ["git", "-C", str(self.root), "-c", "commit.gpgsign=false", *arguments],
            check=True, capture_output=True,
        )

    def commit(self, message: str) -> None:
        self.git("add", "-A")
        self.git("commit", "-m", message)

    def assert_scan(self, expected: int) -> None:
        runner = (
            "import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); "
            "import scan_secrets; scan_secrets.ROOT=Path(sys.argv[2]); "
            "raise SystemExit(scan_secrets.main())"
        )
        result = subprocess.run(
            [sys.executable, "-B", "-c", runner, str(ROOT / "scripts"), str(self.root)],
            capture_output=True, text=True,
        )
        output = result.stdout + result.stderr
        if self.token in output:
            self.fail("synthetic credential appeared unredacted in scanner output")
        self.assertEqual(result.returncode, expected, output)
        if expected:
            self.assertIn("leaks found", output)

    def test_clean_history_and_public_snapshot(self) -> None:
        private = self.root / "private"
        private.mkdir()
        (private / "ignored.txt").write_text(self.token, encoding="utf-8")
        self.assert_scan(0)

    def test_untracked_secret_cannot_use_inline_allow_comment(self) -> None:
        (self.root / "new.txt").write_text(self.token + " # gitleaks:allow\n", encoding="utf-8")
        self.assert_scan(1)

    def test_deleted_secret_introduced_only_in_merge_is_detected(self) -> None:
        self.git("checkout", "-b", "feature")
        (self.root / "feature.txt").write_text("Feature.\n", encoding="utf-8")
        self.commit("Feature change")
        self.git("checkout", "main")
        (self.root / "main.txt").write_text("Main.\n", encoding="utf-8")
        self.commit("Main change")
        self.git("merge", "--no-ff", "--no-commit", "feature")
        secret = self.root / "merge-only.txt"
        secret.write_text(self.token, encoding="utf-8")
        self.commit("Synthetic merge fixture")
        secret.unlink()
        self.commit("Delete synthetic fixture")
        self.assert_scan(1)


if __name__ == "__main__":
    unittest.main()
