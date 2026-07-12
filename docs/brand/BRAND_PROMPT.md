# Codex Pets Brand and Website Execution Prompt

Act as a senior brand designer and frontend engineer working on the public
`senyo888/codex-pets` catalogue.

## Objective

Reinstate **Codex Pets** as the proud, unmistakable top-level title across the
website and repository README. Build a cohesive, reusable visual identity that
feels professional, technically trustworthy, playful, and independent.

## Brand direction

- Use the existing deep-navy, cyan, blue, violet, and warm-gold visual language.
- Create an original **orbital paw** mark: a strong, compact silhouette that
  combines a pet paw with subtle digital/faceted geometry and an open orbital
  ring. It must not copy or imply endorsement by any platform vendor.
- Keep the identity precise and restrained: crisp geometry, luminous facets,
  generous negative space, and no generic cartoon-paw treatment.
- Use the name **Codex Pets** verbatim. The website and README must own this text
  as real HTML/Markdown, not depend on rasterized text for accessibility or SEO.
- Preserve the independent-community disclaimer.

## Image deliverables

1. A reusable square logo mark with a transparent background, suitable for site
   navigation, documentation, social avatars, and future repository assets.
2. A wide branded header artwork using the same orbital-paw language, with a
   dark atmospheric field, subtle orbital paths, crystalline/pixel facets, and
   clean negative space. Do not render pets, UI screenshots, words, watermarks,
   or vendor marks inside the artwork.

Use the image-generation workflow for both assets. Keep the logo simple enough
for reliable chroma-key extraction, validate its alpha channel, and retain the
final assets inside `site/assets/brand/`.

## Website implementation

- Make **Codex Pets** the first and largest hero heading on the homepage.
- Replace the understated text-only navigation treatment with the logo plus a
  confident wordmark lockup.
- Use the shared header artwork as a real hero backdrop with a dark overlay so
  live text always remains readable.
- Retain the existing catalogue, truthful per-pet metrics, installers, package
  links, and four equal pet cards.
- Do not modify or regenerate authoritative pet spritesheets or package assets.
- Maintain semantic heading order, meaningful alt text, keyboard focus,
  reduced-motion support, high contrast, no horizontal overflow, and robust
  mobile behavior at 390 px.

## README and durable brand system

- Carry the same header artwork and logo into the README while keeping
  **Codex Pets** as the visible top-level heading.
- Add concise, durable usage guidance covering the mark, header, palette,
  typography, clear space, minimum size, and prohibited treatments.
- Record the final image-generation prompts so future assets can stay coherent.

## Validation

- Inspect the generated images for composition, unwanted text, watermarks, and
  mark consistency.
- Confirm the logo has transparent corners and clean subject coverage.
- Validate public paths, catalogue/package integrity, privacy, secrets, and
  whitespace.
- Render and inspect the homepage on desktop and at 390 px; confirm zero
  horizontal overflow and no console errors.
- Report exactly what changed, why, runtime/UI impact, migration or restart
  requirements, and any validation limits.

## Executed image prompts

The assets were generated with the built-in image-generation workflow using the
following production prompts.

### Orbital-paw logo

```text
Use case: logo-brand
Asset type: reusable square logo mark for website navigation, README, social avatar, and future brand assets
Primary request: create an original “orbital paw” symbol for Codex Pets, combining a confident pet paw silhouette with subtle digital faceted geometry and one open orbital ring
Scene/backdrop: perfectly flat solid #00ff00 chroma-key background for background removal
Subject: one compact emblem; four small faceted toe pads orbiting a larger angular paw pad, embraced by a single incomplete orbital ring with one tiny square node
Style/medium: clean vector-like logo mark, flat crisp shapes, minimal, premium, scalable, technically precise
Composition/framing: centered square composition, strong silhouette, balanced negative space, generous uniform padding
Color palette: deep navy, luminous cyan, electric blue, restrained violet, one small warm-gold accent; do not use green
Materials/textures: mostly flat color with only very subtle crystalline facet separation inside the mark
Constraints: original design only; no text; no letters; no wordmark; no vendor marks; no watermark; no mockup; no 3D; no extra icons; background must be one perfectly uniform #00ff00 with no shadows, gradients, texture, reflections, floor plane, or lighting variation; crisp isolated edges; no cast shadow or contact shadow
Avoid: generic clip-art paw, mascot face, cat or dog silhouette, speech bubble, starburst, OpenAI-like knot geometry, busy circuitry, fine hairlines
```

### Wide brand header

```text
Use case: stylized-concept
Asset type: reusable wide brand header artwork for the Codex Pets website hero and repository README
Primary request: create a cinematic but restrained panoramic brand field built around the same original “orbital paw” language: an angular paw pad, four crystalline toe facets, an incomplete orbital ring, and one tiny square node
Scene/backdrop: deep navy atmospheric field with subtle layered depth, faint orbital paths, sparse pixel facets, and restrained crystalline light
Subject: the orbital-paw emblem appears large and luminous on the right third; abstract orbit lines and a few tiny facets extend gently across the canvas
Style/medium: premium digital illustration with vector-like geometric clarity, polished open-source product branding, technically trustworthy and playful
Composition/framing: very wide panoramic header; emblem anchored in the right third; generous calm negative space across the left and center for live HTML/Markdown title treatment; safe crop at desktop and mobile
Lighting/mood: controlled cyan-blue glow with restrained violet and a tiny warm-gold accent; confident, calm, welcoming
Color palette: deep navy #06111f, cyan #64e6f5, electric blue, restrained violet, small warm-gold highlight
Materials/textures: crisp luminous facets, subtle matte grain, clean orbital arcs
Constraints: no text; no letters; no words; no pets or animal characters; no UI screenshots; no vendor marks; no watermark; no official-affiliation cues; preserve clean negative space; avoid important detail at extreme edges
Avoid: generic sci-fi clutter, busy star field, neon overload, gradients that crush text contrast, photorealism, mascot characters, OpenAI-like knot geometry
```
