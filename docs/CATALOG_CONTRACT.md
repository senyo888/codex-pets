# Codex Pets catalogue contract

This document defines how a pet package becomes consistent public catalogue truth.
It covers repository content and review. It does not authorize publishing, merging,
or autonomous website maintenance.

## Authority hierarchy

1. The authoritative spritesheet and `pets/<pet-id>/pet.json` define the runtime
   package.
2. `catalog.json` defines collection membership, stable numbering, order, publication
   state, package pins, and repeated presentation facts.
3. Per-pet validation evidence proves the reviewed package; it does not replace the
   asset.
4. The root README, website cards, and installer pages are manually authored
   presentations of canonical package and catalogue truth.
5. The deployed Pages site is a published snapshot of approved `site/` files.

`catalog.json` is the single collection-membership and ordering source. Entries are
sorted by immutable `catalogueNumber`. Published numbers are never reused or changed.

## Field ownership

| Field | Owner | Repeated use |
| --- | --- | --- |
| Pet ID | Package directory and `pet.json.id` | Catalogue, paths, URLs, and parser hooks must match |
| Display name | `pet.json.displayName` | Exact catalogue mirror, README, website, installer |
| Runtime description | `pet.json.description` | Exact catalogue mirror and decoded installer query |
| Catalogue number | `catalog.json.catalogueNumber` | Root collection, website card, installer |
| Publication state | `catalog.json.publicationState` | Published count and active presentation |
| Short role | `catalog.json.presentation.shortRole` | Website card |
| Collection summary | `catalog.json.presentation.summary` | Root collection row and website card |
| Traits | `catalog.json.presentation.traits` | Website card |
| Preview alt text | `catalog.json.presentation.previewAlt` | Root, per-pet, website, and installer previews |
| Sprite version | `pet.json.spriteVersionNumber` | Exact catalogue mirror, README, website, installer, QA |
| Installer page | `catalog.json.installPage` | Root and per-pet README links |
| Deep link | Derived from package identity, description, version, and raw spritesheet URL | Per-pet README and installer page |
| Checksum | Computed from the authoritative spritesheet | Catalogue pin, QA evidence, and README tables |
| Validation status | QA core reconciled by the validator | Derived `Validated vN` presentation |

Long-form personality, design, movement, and attribution prose remains manually
maintained in each per-pet README. It must stay truthful but is not generated from the
catalogue.

## Root README contract

Keep this section order:

1. Brand hero and collection overview.
2. Independent-community disclaimer.
3. The collection.
4. Install a pet.
5. Quality bar.
6. Repository layout.
7. Compatibility.
8. Contributing.
9. License.

The pet count, hero previews, linked names, catalogue rows, installer rows, package
IDs, preview tokens, alt text, sprite versions, validation status, checksums, and
validation links must contain exactly the published catalogue entries in canonical
order. Invariant prose must not enumerate only part of the collection.

## Website contract

Website content is maintainer-initiated manual work. The Pages workflow only deploys
approved `site/` bytes after merge; it does not create or autonomously update content.

Each published landing-page card contains:

- `data-pet-id`, catalogue number, display name, and package README link;
- derived validation status and sprite version;
- canonical short role, summary, and three traits;
- the site preview, its cache token, and canonical alt text;
- installer and package-inspection actions.

Each installer contains canonical identity, number, version, preview, alt text,
runtime description, decoded `codex://` parameters, package README link, permission
guidance, and raw package fallbacks.

For normal additions and upgrades, package, root README, and manually maintained site
content merge in the same pull request. Do not introduce a silent website-lag state.
The short post-merge deployment window closes only after the Pages run succeeds and
the live routes are read back.

## Preview cache busting

Use this exact token:

```text
?v=<first 12 lowercase characters of the referenced preview file's SHA-256>
```

- Root and per-pet README references hash `pets/<pet-id>/preview.gif`.
- Website cards and installers hash `site/assets/<pet-id>-preview.gif`.
- Package and site previews may differ when a documented presentation-only cleanup is
  required. Each surface hashes its own file.
- Preview changes do not change the authoritative spritesheet checksum.

## Change requirements

| Change | Required catalogue surfaces |
| --- | --- |
| New pet | Package, QA, catalogue, every dynamic root README block, site preview/card/installer, validation |
| Atlas artwork upgrade | Spritesheet hash, QA, previews/tokens, package and root README hashes, affected copy, site |
| Preview-only update | Changed preview file and every token that references that exact file |
| Metadata or description | Package metadata, catalogue mirror, deep links, affected README/site copy |
| Sprite-contract version | Every version, format, compatibility, validation, README, site, and installer surface |
| Display-name correction | Every exact name, alt text, heading, link label, and installer parameter; keep ID and number |
| ID correction | Explicit migration with old-route compatibility; never silently rename published paths |

Schema version 2 supports published entries. Retirement or withdrawal requires an
explicit contract update that preserves the historical ID and catalogue number; do
not delete or renumber a published pet.

## Validation

Contributors run:

```bash
python3 scripts/validate_catalog.py
git diff --check
```

The required pull-request check also compares the branch against its base commit so a
published pet cannot be removed or renumbered unnoticed.

Deterministic checks do not replace manual review of artwork, wording, rights,
desktop/mobile layout, keyboard order, focus visibility, reduced motion, console
output, external availability, or real desktop-app installer behaviour.

## Approval gates

- Maintainer initiation is required before website content work.
- Maintainer approval is required before merge.
- A successful Pages deployment and live readback are required before publication is
  declared complete.
- No validator, agent, workflow, or generated output may approve its own work.
