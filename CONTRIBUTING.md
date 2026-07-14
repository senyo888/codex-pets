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
3. Update every public catalogue surface in the same pull request:

   ```text
   pets/<pet-id>/
   site/assets/<pet-id>-preview.gif
   site/install/<pet-id>/index.html
   catalog.json
   README.md
   site/index.html
   ```

   The root README update is mandatory for both new pets and existing-pet upgrades.
   Website content remains maintainer-initiated manual work: a maintainer must explicitly
   authorize the website portion before it is edited or approved. The Pages workflow
   deploys approved `site/` files after merge; it does not create or autonomously update
   catalogue content.

4. Run the contributor checks that exist in this repository:

   ```bash
   python3 scripts/render_idle_preview.py \
     --spritesheet "pets/${PET_ID}/spritesheet.webp" \
     --output "pets/${PET_ID}/preview.gif"
   python3 -m json.tool "pets/${PET_ID}/pet.json" >/dev/null
   python3 -m json.tool "pets/${PET_ID}/qa/validation-summary.json" >/dev/null
   python3 -m json.tool catalog.json >/dev/null
   python3 scripts/validate_catalog.py
   shasum -a 256 "pets/${PET_ID}/spritesheet.webp"
   git diff --check
   ```

   The preview renderer requires Python 3 and Pillow. The tracked catalogue validator
   is the canonical consistency check used locally and in pull requests. It checks the
   package, root README, website cards, preview cache tokens, and installer semantics.
   The renderer checks the v2 atlas
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

A maintainer assigns the next immutable `catalogueNumber` when a pet is accepted. Do
not reserve, reuse, or renumber public catalogue identities yourself.

### Canonical catalogue fields

`catalog.json` is the collection-membership and ordering source. Every entry includes
package mirrors plus the public presentation fields that are repeated across README and
website surfaces:

```json
{
  "catalogueNumber": "008",
  "publicationState": "published",
  "id": "pet-id",
  "displayName": "Pet Name",
  "description": "The exact runtime and installer description.",
  "spriteVersionNumber": 2,
  "spritesheetPath": "pets/pet-id/spritesheet.webp",
  "previewPath": "pets/pet-id/preview.gif",
  "installPage": "https://senyo888.github.io/codex-pets/install/pet-id/",
  "sha256": "<authoritative spritesheet SHA-256>",
  "presentation": {
    "shortRole": "Compact public role",
    "summary": "Canonical collection and website-card summary.",
    "traits": ["Trait one", "Trait two", "Trait three"],
    "previewAlt": "Pet Name's idle animation"
  }
}
```

See the [catalogue contract](docs/CATALOG_CONTRACT.md) for field ownership, preview
cache busting, installer derivation, update rules, and approval gates.

### Canonical README package properties

Every `pets/<pet-id>/README.md` must use this exact property list and order in its
`## Package` table. Keep identity in `pet.json` and catalogue numbering in
`catalog.json`; the package table is reserved for the stable technical contract.

| Property | Required value |
| --- | --- |
| Pet id | Lowercase package directory ID |
| Sprite contract | Declared sprite version, currently `v2` |
| Atlas | `` `1536 × 2288` WebP `` |
| Cell size | `` `192 × 208` `` |
| Animation rows | `9 standard + 2 look-direction rows` |
| SHA-256 | Exact hash of the published `spritesheet.webp` |

Run `python3 scripts/validate_catalog.py` to enforce the property names, order, and
values across every pet README, together with catalogue identity, root README truth,
hashes, previews, validation summaries, website cards, installer queries, and local
references.

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

The cache token is the first 12 lowercase characters of the exact referenced preview
file's SHA-256. Package README references hash `pets/<pet-id>/preview.gif`; website and
installer references hash `site/assets/<pet-id>-preview.gif`. The two previews may
differ after documented presentation-only cleanup.

## Change matrix

| Change | Required updates |
| --- | --- |
| New pet | Complete package and QA, catalogue entry, every dynamic root README block, site preview/card/installer |
| Atlas artwork upgrade | New spritesheet hash and QA, previews/tokens, package and root README hashes, affected copy, site |
| Preview-only update | Changed preview file and every cache token that references that exact file |
| Metadata or description | `pet.json`, catalogue mirror, decoded installer links, and affected README/site copy |
| Sprite-contract version | Every version, compatibility, validation, README, site, and installer surface |
| Display-name correction | Every exact name, alt text, heading, link label, and installer parameter; keep ID and number |
| ID correction | Explicit migration with old-route compatibility; never silently rename a published path |

## Acceptance bar

- The atlas is transparent WebP or PNG and follows the declared Codex sprite version.
- A v2 atlas is exactly `1536 × 2288`, using `192 × 208` cells in an `8 × 11` layout.
- Standard rows have the correct state semantics and contain no detached effects, shadows, guide marks, or opaque backgrounds.
- Look directions preserve identity and pass the four cardinal gates: up, screen-right, down, and screen-left.
- Deterministic validation reports no errors.
- The preview and QA images were produced from the exact submitted atlas.
- `catalog.json`, every affected root README block, and the one-click install link are updated in the same pull request.
- Maintainer-initiated site content, installer copy, previews, alt text, and cache tokens agree before merge.

Do not submit an unreviewed generated atlas, a flattened image without transparency, or a package whose metadata and spritesheet disagree.

## Pull request checklist

- [ ] Pet package added under `pets/<pet-id>/`
- [ ] `pet.json` and atlas version agree
- [ ] Pet README uses the canonical Package property list and order
- [ ] `catalog.json` contains the assigned number and canonical presentation fields
- [ ] Root README count, previews, names, collection row, installer row, and checksum row agree
- [ ] Preview cache tokens match the exact referenced preview bytes
- [ ] Website card and installer content were manually initiated and approved by a maintainer
- [ ] Atlas dimensions and alpha channel validated
- [ ] Standard animations visually reviewed
- [ ] V2 look directions and continuity reviewed
- [ ] SHA-256 recorded in `catalog.json` and the validation summary
- [ ] Decoded install link matches the canonical public HTTPS spritesheet URL and metadata
- [ ] `python3 scripts/validate_catalog.py` passes
- [ ] Desktop and 390 px mobile layouts, keyboard focus, and console output reviewed
- [ ] Artwork is original or licensed for redistribution

Keep each pull request focused on one pet or one coherent update to an existing pet.
