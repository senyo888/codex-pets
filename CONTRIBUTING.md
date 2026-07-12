# Contributing a Codex pet

Thanks for helping the collection grow. A pet should be delightful in the app and boringly reliable as a package.

## Required package

Create one lowercase directory under `pets/` containing:

```text
pets/<pet-id>/
├── pet.json
├── spritesheet.webp
├── preview.gif
├── README.md
└── qa/
    ├── contact-sheet.png
    ├── look-directions.png
    └── validation-summary.json
```

The metadata must use the same id as the directory:

```json
{
  "id": "pet-id",
  "displayName": "Pet Name",
  "description": "One clear sentence.",
  "spriteVersionNumber": 2,
  "spritesheetPath": "spritesheet.webp"
}
```

## Acceptance bar

- The atlas is transparent WebP or PNG and follows the declared Codex sprite version.
- A v2 atlas is exactly `1536 × 2288`, using `192 × 208` cells in an `8 × 11` layout.
- Standard rows have the correct state semantics and contain no detached effects, shadows, guide marks, or opaque backgrounds.
- Look directions preserve identity and pass the four cardinal gates: up, screen-right, down, and screen-left.
- Deterministic validation reports no errors.
- The preview and QA images were produced from the exact submitted atlas.
- `catalog.json`, the root catalogue table, and the one-click install link are updated in the same change.

Do not submit an unreviewed generated atlas, a flattened image without transparency, or a package whose metadata and spritesheet disagree.

## Pull request checklist

- [ ] Pet package added under `pets/<pet-id>/`
- [ ] `pet.json` and atlas version agree
- [ ] Atlas dimensions and alpha channel validated
- [ ] Standard animations visually reviewed
- [ ] V2 look directions and continuity reviewed
- [ ] SHA-256 recorded in `catalog.json` and the validation summary
- [ ] Install link tested with a public HTTPS spritesheet URL
- [ ] Artwork is original or licensed for redistribution

Keep each pull request focused on one pet or one coherent update to an existing pet.
