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
