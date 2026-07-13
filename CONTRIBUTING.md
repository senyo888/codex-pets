# Contributing a Codex pet

Thanks for helping the collection grow. A pet should be delightful in the app and boringly reliable as a package.

## Add Your Pet

Have a companion you would like to share? Choose the route that matches what you
have today. You do not need a finished sprite atlas to ask for guidance.

### Need a hand? Start a guided submission

Use the [Add Your Pet form](https://github.com/senyo888/codex-pets/issues/new?template=add-your-pet.yml)
if you have an idea, artwork, an atlas in progress, or a partial package. Tell us
what you have and where you need help. A maintainer will check the proposed pet ID
and licensing information, then give you a concrete list of next steps.

GitHub issues are public. Do not include tokens, private download links, local file
paths, personal information, or artwork you cannot share publicly.

Starting a submission begins a review; it does not approve or publish the pet. Every
pet must still complete the package, licensing, and validation checks before joining
the catalogue.

### Package ready? Open a pull request

Use this route when the atlas, metadata, preview, QA evidence, and licensing
confirmation are ready. If any of those pieces are missing, use the guided route so
the gap is clear before you build the pull request.

1. Fork the repository, clone your fork, and create one branch for one pet:

   ```bash
   GITHUB_USER=your-user
   PET_ID=your-pet
   git clone "https://github.com/${GITHUB_USER}/codex-pets.git"
   cd codex-pets
   git remote add upstream https://github.com/senyo888/codex-pets.git
   git switch -c "add-${PET_ID}"
   mkdir -p "pets/${PET_ID}/qa"
   ```

2. Add the complete [required package](#required-package), then render its preview
   using the [preview command](#preview-rendering).
3. Update every public catalogue surface in the same change:

   ```text
   pets/<pet-id>/
   site/assets/<pet-id>-preview.gif
   site/install/<pet-id>/index.html
   catalog.json
   README.md
   site/index.html
   ```

4. Run the contributor checks that exist in this repository:

   ```bash
   python3 scripts/render_idle_preview.py \
     --spritesheet "pets/${PET_ID}/spritesheet.webp" \
     --output "pets/${PET_ID}/preview.gif"
   python3 -m json.tool "pets/${PET_ID}/pet.json" >/dev/null
   python3 -m json.tool "pets/${PET_ID}/qa/validation-summary.json" >/dev/null
   python3 -m json.tool catalog.json >/dev/null
   shasum -a 256 "pets/${PET_ID}/spritesheet.webp"
   git diff --check
   ```

   The preview renderer requires Python 3 and Pillow. It checks the v2 atlas
   dimensions and alpha channel while producing the public GIF. Maintainers confirm
   the full animation-row, direction, continuity, checksum, and catalogue checks
   during review.

5. Push your branch and open a pull request. The repository pull request template
   contains the final package and review checklist.

Not sure which route fits? Start with the guided submission. It is better to identify
a missing requirement early than to reverse-engineer a published package.

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

## Preview rendering

Build the six-frame idle GIF directly from the validated v2 atlas:

```bash
PET_ID=your-pet
python3 scripts/render_idle_preview.py \
  --spritesheet "pets/${PET_ID}/spritesheet.webp" \
  --output "pets/${PET_ID}/preview.gif"
```

The command requires Python 3 and Pillow. The renderer preserves the standard idle
timing, creates a `384 × 416` 2x presentation asset for clean browser downsampling, and
uses a deterministic alpha cutoff before GIF encoding. This prevents GIF's binary
transparency from turning faint edge pixels into a grainy fringe. Copy the resulting
preview to `site/assets/` when the pet is shown in the public catalogue.

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
