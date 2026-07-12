<div align="center">

<img src="site/assets/brand/codex-pets-header.png" alt="Codex Pets orbital-paw brand header" width="92%">

# Codex Pets

**Small companions. Serious sprites.**

An independent community catalogue of custom animated pets for the Codex desktop app, packaged with one-click install links and reviewable validation evidence.

![Pets](https://img.shields.io/badge/pets-6-67e8f9?style=flat-square)
![Sprite format](https://img.shields.io/badge/sprite%20format-v2-a78bfa?style=flat-square)
![License](https://img.shields.io/badge/license-CC%20BY%204.0-fbbf24?style=flat-square)

<img src="pets/bella/preview.gif" alt="Bella idle animation" width="150">
<img src="pets/aethercore/preview.gif" alt="AetherCore idle animation" width="150">
<img src="pets/aethermite/preview.gif" alt="AetherMite idle animation" width="150">
<img src="pets/aetherbite/preview.gif" alt="Aetherbite idle animation" width="150">
<img src="pets/calian/preview.gif" alt="Calian idle animation" width="150">
<img src="pets/scarlet/preview.gif" alt="Scarlet idle animation" width="150">

### Bella · AetherCore · AetherMite · Aetherbite · Calian · Scarlet

*Six distinct companions, each shipped as a transparent and inspectable v2 package.*

[**Browse the catalogue**](https://senyo888.github.io/codex-pets/) · [**Brand guide**](docs/brand/BRAND_GUIDE.md) · [**Contributing guide**](CONTRIBUTING.md)

</div>

> [!IMPORTANT]
> This is an independent community project. It is not affiliated with or endorsed by OpenAI.

## The collection

| Pet | Personality | Format | Status |
| --- | --- | --- | --- |
| [**Bella**](pets/bella/README.md) | A crystalline guardian of clarity, truth, and deterministic coherence. | Sprite v2 | Validated and ready |
| [**AetherCore**](pets/aethercore/README.md) | A calm clockwork governance engine for continuity, coherence, and visible drift. | Sprite v2 | Validated and ready |
| [**AetherMite**](pets/aethermite/README.md) | A systems tinkerer for diagnostics, refinement, and deterministic micro-innovation. | Sprite v2 | Validated and ready |
| [**Aetherbite**](pets/aetherbite/README.md) | A refined bio-digital champion with crystalline wings and expressive motion. | Sprite v2 | Validated and ready |
| [**Calian**](pets/calian/README.md) | A disciplined code sentinel who resolves threats and keeps systems under control. | Sprite v2 | Validated and ready |
| [**Scarlet**](pets/scarlet/README.md) | A poised execution defender who counters drift and protects runtime integrity. | Sprite v2 | Validated and ready |

## Install a pet

Each HTTPS install page opens the pet installation flow when Pets are enabled for your account. It also provides direct package downloads as a fallback because GitHub removes custom `codex://` links from rendered README files.

| Pet | Installer | Package |
| --- | --- | --- |
| Bella | [Open installer](https://senyo888.github.io/codex-pets/install/bella/) | [Inspect files](pets/bella) |
| AetherCore | [Open installer](https://senyo888.github.io/codex-pets/install/aethercore/) | [Inspect files](pets/aethercore) |
| AetherMite | [Open installer](https://senyo888.github.io/codex-pets/install/aethermite/) | [Inspect files](pets/aethermite) |
| Aetherbite | [Open installer](https://senyo888.github.io/codex-pets/install/aetherbite/) | [Inspect files](pets/aetherbite) |
| Calian | [Open installer](https://senyo888.github.io/codex-pets/install/calian/) | [Inspect files](pets/calian) |
| Scarlet | [Open installer](https://senyo888.github.io/codex-pets/install/scarlet/) | [Inspect files](pets/scarlet) |

After installation, open **Settings → Pets**, choose your companion, and wake it with `/pet`.

### Manual installation

If the deep link is unavailable, place both package files in your local pet directory:

```bash
PET_ID=calian # bella, aethercore, aethermite, aetherbite, calian, or scarlet
mkdir -p "${CODEX_HOME:-$HOME/.codex}/pets/$PET_ID"
curl -fL "https://raw.githubusercontent.com/senyo888/codex-pets/main/pets/$PET_ID/pet.json" \
  -o "${CODEX_HOME:-$HOME/.codex}/pets/$PET_ID/pet.json"
curl -fL "https://raw.githubusercontent.com/senyo888/codex-pets/main/pets/$PET_ID/spritesheet.webp" \
  -o "${CODEX_HOME:-$HOME/.codex}/pets/$PET_ID/spritesheet.webp"
```

Refresh **Settings → Pets** after copying the files.

## Quality bar

Every published pet includes:

- a transparent, structurally valid v2 sprite atlas;
- matching metadata with an explicit sprite version;
- a human-readable animated preview;
- deterministic validation with no structural errors;
- visual review of all standard animation states;
- direction and continuity review;
- public QA sheets and a sanitized validation summary.

All six pets ship as exact `1536 × 2288` RGBA WebP atlases. Their published spritesheets match their fully reviewed local packages byte-for-byte.

| Pet | SHA-256 | Validation |
| --- | --- | --- |
| Bella | `ea6eb944f421c673d76e142e1f88ad09e5d3bc13bb4043619ea120cea5a11db5` | [Summary](pets/bella/qa/validation-summary.json) |
| AetherCore | `de543a1dc1ad397a9cf0bd9f51235ffe78408b01d2b37f4a44cdd9cbd1a98205` | [Summary](pets/aethercore/qa/validation-summary.json) |
| AetherMite | `d49b0269b6d9ed530311ec81c5dbd52c3024fc317d5d3731a1f154dce18aaf75` | [Summary](pets/aethermite/qa/validation-summary.json) |
| Aetherbite | `92803b181a6dc20fbdf65a4867f5f1b34593c918bb3baacb1f73f07199b81a37` | [Summary](pets/aetherbite/qa/validation-summary.json) |
| Calian | `86658fefbf53dde647575a26acc35ad0fd104409308afa183ca3732640837f34` | [Summary](pets/calian/qa/validation-summary.json) |
| Scarlet | `41cf2190cb49895fb6d444f8885c5dc9712e8187fbd13a785754d0ce5603f24b` | [Summary](pets/scarlet/qa/validation-summary.json) |

## Repository layout

```text
codex-pets/
├── catalog.json
├── docs/brand/
│   ├── BRAND_GUIDE.md
│   └── BRAND_PROMPT.md
├── pets/
│   └── <pet-id>/
│       ├── pet.json
│       ├── spritesheet.webp
│       ├── preview.gif
│       ├── README.md
│       └── qa/
├── site/
│   ├── assets/brand/
│   └── install/<pet-id>/
└── CONTRIBUTING.md
```

## Compatibility

- **Codex desktop app:** v2 packages with the full floating-pet animation and look-direction contract.
- **Codex CLI:** compatible terminals can select locally installed custom pets with `/pets`.
- **ChatGPT web:** custom uploads use a separate upload contract, so these packages target desktop and compatible CLI use.

See the [Pets documentation](https://learn.chatgpt.com/docs/pets?surface=app) for current platform availability and controls.

## Contributing

New pets are welcome once they meet the same packaging and QA bar. Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

The pet artwork, animations, previews, and repository documentation are available under the [Creative Commons Attribution 4.0 International License](LICENSE).

Credit: **Senyo** · Source: `senyo888/codex-pets`
