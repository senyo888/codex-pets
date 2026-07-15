<div align="center">

# Scarlet

**The Execution Defender**

<img src="preview.gif?v=033f7e8c9854" alt="Scarlet's calm idle animation" width="240">

*A poised agent warrior and one half of a disciplined sister act, built to trace drift, protect execution integrity, and close gaps cleanly.*

[**Install Scarlet**](https://senyo888.github.io/codex-pets/install/scarlet/)

</div>

## Personality

Scarlet is poised, vigilant, and exacting. She follows weak signals across the full execution path, contains drift before it spreads, and closes gaps with controlled precision.

Her strength is sustained coverage: she keeps the wider system in view and follows every correction through to verification.

## The sister act

[Calian](../calian/README.md) and Scarlet work as a coordinated pair. Calian provides stabilising judgement while Scarlet extends their execution coverage. Together, their combined diligence is unmatched from first assessment to final verification.

## Package

| Property | Value |
| --- | --- |
| Pet id | `scarlet` |
| Sprite contract | v2 |
| Atlas | `1536 × 2288` WebP |
| Cell size | `192 × 208` |
| Animation rows | 9 standard + 2 look-direction rows |
| SHA-256 | `41cf2190cb49895fb6d444f8885c5dc9712e8187fbd13a785754d0ce5603f24b` |

The package contains the exact validated spritesheet and matching sanitized metadata. No rescaling, recompression, or post-validation sprite editing was applied before publication.

## Install

Use the button above, or open this URI with the Codex desktop app:

```text
codex://pets/install?name=Scarlet&imageUrl=https%3A%2F%2Fraw.githubusercontent.com%2Fsenyo888%2Fcodex-pets%2Fmain%2Fpets%2Fscarlet%2Fspritesheet.webp&description=One%20half%20of%20a%20disciplined%20sister%20act%2C%20Scarlet%20is%20a%20poised%2C%20vigilant%20agent%20warrior%20who%20traces%20drift%20and%20protects%20execution%20integrity.&spriteVersionNumber=2
```

Then select Scarlet in **Settings → Pets** and use `/pet` to wake or tuck her away.

## Validation

Scarlet passed the v2 atlas validator with:

- correct `8 × 11` geometry and alpha transparency;
- no structural errors or validator warnings;
- no transparent-pixel RGB residue;
- all four cardinal look directions confirmed;
- no failed semantic direction verdicts;
- reviewed intermediate-direction and continuity warnings with no visible reversal, clipping, identity drift, or broken attachment.

[Read the validation summary](qa/validation-summary.json)

<details>
<summary><strong>View all animation cells</strong></summary>

![Scarlet animation contact sheet](qa/contact-sheet.png)

</details>

<details>
<summary><strong>View the 16-direction QA sheet</strong></summary>

![Scarlet look-direction QA](qa/look-directions.png)

</details>

## Attribution

Scarlet is created and maintained by **Senyo** and published under [CC BY 4.0](../../LICENSE). If you remix or redistribute her, retain attribution and link back to this repository.
