# Maintenance and compatibility

## Development setup

Use Python 3.12 or newer and a complete Git installation with HTTPS helpers.
Keep image tooling in a project environment rather than installing into system Python:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/validate_catalog.py
python scripts/validate_previews.py
```

Repeat setup for each checkout. The standard-library catalogue check can also run
without the environment. CI installs the same pinned Pillow dependency for previews.
If Git reports a missing `remote-https`, inspect `git --exec-path` and the selected
Git distribution; restore its matching helper directory rather than changing credentials.

## Pillow security update

The image tools now require `Pillow==13.0.0`. This replaces 12.3.0, which was affected
by 41 Dependabot advisories recorded on 2026-10-31. Each advisory identifies 13.0.0
as the first patched version; see the [upstream security fixes](https://pillow.readthedocs.io/en/stable/releasenotes/13.0.0.html#security).
Pillow processes contributed artwork during local validation and CI, so update
existing development environments before processing new submissions:

```sh
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip check
python scripts/validate_catalog.py
python scripts/test_validation_exceptions.py
python scripts/validate_previews.py
python scripts/test_image_safety.py
```

Continue using Python 3.12 or newer. This dependency update does not regenerate
artwork or change package metadata, installer links, or installed pets. GitHub alerts
remain open until the updated dependency reaches the default branch and Dependabot
re-evaluates it.

## Image input limits

Image tools read a bounded snapshot of each regular file so validation and decoding
use the same bytes. Preview GIFs must have exactly six frames on a `192 × 208` canvas
at integer scale 1–4. The complete GIF block structure, including every frame rectangle,
is checked before Pillow opens it. Timing, transparency, disposal, looping, and exact
frame-zero PNG comparison still apply.

| Input | Encoded size limit | Image limit |
| --- | --- | --- |
| Idle preview GIF | 8 MiB | Six frames; at most `768 × 832` |
| Preview PNG still | 8 MiB | Static; exact preview dimensions |
| PNG or WebP atlas | 32 MiB | Static; exactly `1536 × 2288`; alpha channel |
| Release header PNG logo | 8 MiB | Static; at most `2048 × 2048` |

WebP canvas and bitstream dimensions are checked before native decoder creation.
Header pet crops must also fit within the `1200 × 560` output before resizing, so a
very thin visible strip cannot cause an excessive allocation. The V1 header generator
retains its explicit seven-pet composition guard; it needs a separate composition
update before it can render the current eight-pet catalogue through its CLI.

Run `python scripts/test_image_safety.py` to exercise malformed inputs, pre-decoder
rejections, supported scales, and valid PNG/WebP paths. This check also runs in CI.

## Secret scanning

Install [Gitleaks 8.30.1](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1)
for your platform from the official release and verify its archive against that
release's checksums. Put the binary on `PATH`, then run:

```sh
gitleaks version
python3 scripts/scan_secrets.py
python3 scripts/test_scan_secrets.py
```

The wrapper requires that exact version and scans all locally available Git history
including diffs against each merge parent, plus a snapshot of tracked and non-ignored
untracked files. Deleted historical secrets are still checked. Ignored, untracked local files are excluded from the public
snapshot; tracked files are included even when an ignore pattern matches them.
Fetch relevant remote branches first when checking history in a shallow or partial
checkout.

The `gitleaks` CI job runs on pull requests, pushes to `main`, and manual dispatch.
It fetches full history, verifies the pinned Linux binary's SHA-256, uses the default
detectors from `.gitleaks.toml`, and fails on findings or scanner errors. Output is
redacted; inline allow comments and ambient ignore files cannot suppress findings.
The job needs only read access to repository contents and no service token.
Its regression tests use disposable repositories and synthetic credentials to check
untracked files, merge-only historical secrets, redaction, and a clean control.

If a real credential is found, revoke or rotate it and investigate its exposure.
Removing the current file does not remove it from history. Review any required
history remediation explicitly rather than adding a blanket allowlist.

## Version assessment

These security changes are repository tooling and CI maintenance. They do not alter
the catalogue schema or sprite contract: keep `schemaVersion` and
`spriteVersionNumber` at `2`. Installed pets need no metadata bump or reinstallation.

The repository has no application version manifest to update. The `v1.0.1` patch
release records this security maintenance; a release tag is not required for
Dependabot to recognize the corrected default-branch dependency. See the
[v1.0.1 release notes](releases/v1.0.1.md) for the security fixes and other changes
since v1.0.0. Publication status is recorded on the
[GitHub releases page](https://github.com/senyo888/codex-pets/releases).

## October 2026 maintenance changes

- Idle previews now use a 6.6-second loop rather than the previous 1.1-second loop.
  Timing was checked against desktop app 26.930.21537 on 2026-10-03. Original decoded
  GIF artwork is retained; only frame delays changed.
- Static PNG alternatives show frame zero under reduced motion on the catalogue and
  every installer. GIF and PNG cache tokens track the exact referenced files.
- Preview validation runs in CI alongside catalogue validation.
- Authoritative atlases, package IDs, descriptions, sprite versions, installer queries,
  and published v1.0.0 release assets are unchanged by these presentation changes.

## Runtime boundaries

The desktop app owns playback, state priority, pointer responses, pet size, and
reduced-motion handling. Package artwork does not implement agent reasoning or control
Home Assistant. Changing preview timing cannot change installed runtime timing.

Desktop v2 atlases and ChatGPT web derivatives have separate contracts. Desktop files
are local; web adoption links and uploads are separate distribution records. Do not
replace an eleven-row desktop atlas with a nine-row web export.

Sources: [Pets](https://learn.chatgpt.com/docs/pets) and
[September 11 pet controls update](https://learn.chatgpt.com/docs/changelog), checked
2026-10-03. Recheck renderer timing on future app updates before changing this baseline.

## Validation before distribution

Run both validators, inspect catalogue and all installers at desktop and 390 px mobile
widths, and switch reduced motion both ways. Confirm each loaded still is static and
matches the visible idle character. Check for image failures, overflow, console errors,
and unchanged install actions. Preview-only changes do not require reinstalling atlases.
For installed packages, compare both pet.json and spritesheet bytes with the chosen
canonical package; preserve prior files before synchronizing metadata.

For an artwork change, rerun structural and visual QA across all states and directions,
update hashes and previews together, and verify at actual display sizes. A frame-difference
outlier alone is not sufficient evidence to regenerate a character.
