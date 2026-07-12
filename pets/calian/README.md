<div align="center">

# Calian

**The Code Sentinel**

<img src="preview.gif" alt="Calian idle animation" width="240">

*A composed agent warrior built to defend code and keep complex systems under deliberate control.*

[**Install Calian**](https://senyo888.github.io/codex-pets/install/calian/)

</div>

## Personality

Calian is calm, tactical, and steady under pressure. She watches the whole execution path, identifies the real point of failure, and acts once with purpose.

Her role is defensive engineering: hold the line against unsafe changes, resolve threats without drama, and leave the system clearer than she found it.

## Package

| Property | Value |
| --- | --- |
| Pet id | `calian` |
| Sprite contract | v2 |
| Atlas | `1536 × 2288` WebP |
| Cell size | `192 × 208` |
| Animation rows | 9 standard + 2 look-direction rows |
| SHA-256 | `86658fefbf53dde647575a26acc35ad0fd104409308afa183ca3732640837f34` |

The package contains the exact validated spritesheet and matching sanitized metadata. No rescaling, recompression, or post-validation sprite editing was applied before publication.

## Install

Use the button above, or open this URI with the Codex desktop app:

```text
codex://pets/install?name=Calian&imageUrl=https%3A%2F%2Fraw.githubusercontent.com%2Fsenyo888%2Fcodex-pets%2Fmain%2Fpets%2Fcalian%2Fspritesheet.webp&description=A%20calm%2C%20disciplined%20agent%20warrior%20who%20defends%20code%2C%20resolves%20threats%2C%20and%20keeps%20complex%20systems%20under%20deliberate%20control.&spriteVersionNumber=2
```

Then select Calian in **Settings → Pets** and use `/pet` to wake or tuck her away.

## Validation

Calian passed the v2 atlas validator with:

- correct `8 × 11` geometry and alpha transparency;
- no structural errors or validator warnings;
- no transparent-pixel RGB residue;
- all four cardinal look directions confirmed;
- no failed semantic direction verdicts;
- reviewed intermediate-direction and continuity warnings with no visible reversal, clipping, identity drift, or broken attachment.

[Read the validation summary](qa/validation-summary.json)

<details>
<summary><strong>View all animation cells</strong></summary>

![Calian animation contact sheet](qa/contact-sheet.png)

</details>

<details>
<summary><strong>View the 16-direction QA sheet</strong></summary>

![Calian look-direction QA](qa/look-directions.png)

</details>

## Attribution

Calian is created and maintained by **Senyo** and published under [CC BY 4.0](../../LICENSE). If you remix or redistribute her, retain attribution and link back to this repository.
