<div align="center">

# ✨ Codex Pets

**Small companions. Serious sprites.**

Custom animated pets for the Codex desktop app, packaged with one-click install links and reviewable validation evidence.

![Pets](https://img.shields.io/badge/pets-2-67e8f9?style=flat-square)
![Sprite format](https://img.shields.io/badge/sprite%20format-v2-a78bfa?style=flat-square)
![License](https://img.shields.io/badge/license-CC%20BY%204.0-fbbf24?style=flat-square)

<img src="pets/bella/preview.gif" alt="Bella idle animation" width="180">
<img src="pets/aethercore/preview.gif" alt="AetherCore idle animation" width="180">

### Bella · AetherCore

*Crystal clarity meets clockwork continuity.*

[**Install Bella**](https://senyo888.github.io/codex-pets/install/bella/) · [**Install AetherCore**](https://senyo888.github.io/codex-pets/install/aethercore/)

</div>

## The collection

| Pet | Personality | Format | Status |
| --- | --- | --- | --- |
| [**Bella**](pets/bella/README.md) | A crystalline guardian of clarity, truth, and deterministic coherence. | Codex sprite v2 | Validated and ready |
| [**AetherCore**](pets/aethercore/README.md) | A calm clockwork governance engine for continuity, coherence, and visible drift. | Codex sprite v2 | Validated and ready |

More small beings will arrive when they are properly hatched, tested, and house-trained.

## Install a pet

The HTTPS install page opens the Codex pet installation flow when Pets are enabled for your account. It also keeps a visible fallback button because GitHub intentionally removes custom `codex://` links from rendered README files.

### Bella

```text
codex://pets/install?name=Bella&imageUrl=https%3A%2F%2Fraw.githubusercontent.com%2Fsenyo888%2Fcodex-pets%2Fmain%2Fpets%2Fbella%2Fspritesheet.webp&description=The%201%20True%20Source%2C%20a%20calm%20crystalline%20harmonic%20source%20engine%20that%20restores%20deterministic%20coherence.&spriteVersionNumber=2
```

### AetherCore

```text
codex://pets/install?name=AetherCore&imageUrl=https%3A%2F%2Fraw.githubusercontent.com%2Fsenyo888%2Fcodex-pets%2Fmain%2Fpets%2Faethercore%2Fspritesheet.webp&description=A%20calm%20governance-engine%20pet%20for%20Humidity%20Intelligence%20continuity%20and%20coherence.&spriteVersionNumber=2
```

After installation, open **Settings → Pets**, choose your companion, and wake it with `/pet`.

### Manual installation

If the deep link is unavailable, place both package files in your local Codex pet directory:

```bash
PET_ID=aethercore # or bella
mkdir -p "${CODEX_HOME:-$HOME/.codex}/pets/$PET_ID"
curl -fL "https://raw.githubusercontent.com/senyo888/codex-pets/main/pets/$PET_ID/pet.json" \
  -o "${CODEX_HOME:-$HOME/.codex}/pets/$PET_ID/pet.json"
curl -fL "https://raw.githubusercontent.com/senyo888/codex-pets/main/pets/$PET_ID/spritesheet.webp" \
  -o "${CODEX_HOME:-$HOME/.codex}/pets/$PET_ID/spritesheet.webp"
```

Refresh **Settings → Pets** after copying the files.

## Quality bar

Every published pet must include:

- a transparent, structurally valid Codex sprite atlas;
- matching metadata with an explicit sprite version;
- a human-readable preview;
- deterministic validation with no structural errors;
- visual review of every standard animation state;
- direction and continuity review for v2 pets.

Bella and AetherCore each ship as an exact `1536 × 2288` v2 WebP atlas. Every published spritesheet matches its fully reviewed local package byte-for-byte. See [Bella's validation](pets/bella/qa/validation-summary.json) and [AetherCore's validation](pets/aethercore/qa/validation-summary.json).

## Repository layout

```text
codex-pets/
├── catalog.json
├── pets/
│   └── <pet-id>/
│       ├── pet.json
│       ├── spritesheet.webp
│       ├── preview.gif
│       ├── README.md
│       └── qa/
└── CONTRIBUTING.md
```

## Compatibility

- **Codex desktop app:** v2 package with the full floating-pet animation and look-direction contract.
- **Codex CLI:** compatible terminals can select locally installed custom pets with `/pets`.
- **ChatGPT web:** custom uploads currently use a separate v1 upload contract, so this v2 package is intended for desktop and compatible CLI use.

See the official [Pets documentation](https://learn.chatgpt.com/docs/pets?surface=app) for current platform availability and controls.

## Contributing

New pets are welcome once they meet the same packaging and QA bar. Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

The pet artwork, animations, previews, and repository documentation are available under the [Creative Commons Attribution 4.0 International License](LICENSE).

Credit: **Senyo** · Source: `senyo888/codex-pets`
