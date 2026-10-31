#!/usr/bin/env python3
"""Scan available Git history and the public working snapshot with Gitleaks."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
GITLEAKS_VERSION = "8.30.1"


def public_snapshot(root: Path, destination: Path) -> None:
    """Copy tracked and non-ignored untracked files, without following symlinks."""
    names = subprocess.check_output(
        ["git", "-C", str(root), "ls-files", "-co", "--exclude-standard", "-z"]
    ).split(b"\0")
    for name in sorted(set(names) - {b""}):
        relative = Path(os.fsdecode(name))
        source = root / relative
        target = destination / relative
        if source.is_symlink():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(os.readlink(source), encoding="utf-8")
        elif source.is_file():
            if not source.resolve().is_relative_to(root.resolve()):
                raise SystemExit(f"public file resolves outside the repository: {relative}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)


def main() -> int:
    """Fail on findings or scanner errors, with secrets redacted from output."""
    executable = shutil.which("gitleaks")
    if executable is None:
        raise SystemExit(f"Install Gitleaks {GITLEAKS_VERSION}; see docs/MAINTENANCE.md")
    version = subprocess.check_output([executable, "version"], text=True).strip()
    if version != GITLEAKS_VERSION:
        raise SystemExit(f"Expected Gitleaks {GITLEAKS_VERSION}, found {version}")
    with tempfile.TemporaryDirectory(prefix="codex-pets-secret-scan-") as temporary:
        staging = Path(temporary)
        snapshot = staging / "snapshot"
        snapshot.mkdir()
        # An empty ignore file and explicit config prevent ambient suppressions.
        ignore = staging / "empty-ignore"
        ignore.touch()
        common = [
            "--config", str(ROOT / ".gitleaks.toml"), "--redact=100", "--no-banner",
            "--ignore-gitleaks-allow", "--gitleaks-ignore-path", str(ignore),
        ]
        history = subprocess.run(
            [executable, "git", *common, "--log-opts=--all --full-history -m", str(ROOT)],
            check=False,
        ).returncode
        public_snapshot(ROOT, snapshot)
        working = subprocess.run([executable, "dir", *common, str(snapshot)], check=False).returncode
    return 1 if history or working else 0


if __name__ == "__main__":
    raise SystemExit(main())
