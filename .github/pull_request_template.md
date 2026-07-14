## Summary

<!-- Explain what changed and why. Link a guided submission issue with "Closes #..." when one exists. -->

## Change type

- [ ] New pet package
- [ ] Existing pet update
- [ ] Maintainer-initiated website sync
- [ ] Documentation or validation only

## Pet details

<!-- Use N/A for website or documentation-only changes. -->

- Pet name:
- Pet ID:
- Catalogue number:
- Update subtype: New / Atlas / Preview only / Metadata / Version / Identity / N/A
- Related issue:
- Attribution:

## Package checklist

<!-- Complete for every new or changed pet package. -->

- [ ] One pet is included in this pull request
- [ ] `pets/<pet-id>/pet.json` matches the lowercase directory ID
- [ ] The pet README uses the canonical Package property list and order
- [ ] `catalog.json` contains the assigned number and canonical presentation fields
- [ ] The v2 atlas is `1536 × 2288`, transparent, and uses the `8 × 11` layout
- [ ] Preview and QA evidence were produced from the submitted atlas
- [ ] Root README count, preview, name, order, summary, installer, and checksum surfaces agree
- [ ] Every preview cache token matches the exact referenced preview file
- [ ] Website card and installer identity, number, role, summary, traits, alt text, and links agree
- [ ] Website content work was explicitly initiated and approved by a maintainer
- [ ] The atlas SHA-256 matches the catalogue and validation summary
- [ ] Decoded `codex://` parameters match the canonical package metadata and raw spritesheet URL
- [ ] Standard animation rows, directions, and continuity were reviewed

## Validation performed

<!-- List exact commands and manual checks. Do not claim checks that were not run. -->

- [ ] JSON files parse successfully
- [ ] `python3 scripts/validate_catalog.py` passes
- [ ] Preview rendering completed successfully
- [ ] Local website links and installer route were checked
- [ ] Desktop and 390 px mobile layouts were checked
- [ ] Keyboard order, focus visibility, reduced motion, and console output were checked
- [ ] `git diff --check` passes

Results:

## Impact

- Runtime/package impact:
- Website/UI impact:
- Entity or installer semantics changed: No / Yes — explain
- Migration or restart required: No / Yes — explain
- Rollback:

## Rights

- [ ] For every submitted asset, I am the creator or have authority to contribute it under CC BY 4.0
- [ ] I agree that accepted artwork and documentation may be published under CC BY 4.0 with the attribution provided above
