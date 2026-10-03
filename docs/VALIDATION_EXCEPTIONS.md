# Maintainer validation exceptions

A catalogue consistency pass does not mean every strict artwork check passed.
Exceptions are explicit maintainer decisions for a named pet and exact atlas hash.
They retain the original failed measurements and require honest public presentation.
They do not permit missing files, corrupt assets, identity mismatches, undisclosed
findings, or changes to global validation thresholds.

## Áureo 008

**Decision:** Accept Áureo's original submitted design with the recorded chroma-edge
and left-look limitations. Preserve its artwork, emblem and jumping choreography.
Keep the strict failures visible and label the package "Reviewed with limitations".

- Decision date: 3 October 2026.
- Exception ID: `aureo-original-2026-10-03`.
- Pet ID: `aureo`; catalogue number: `008`.
- Atlas SHA-256: `614dabf05306723f15415b2ae7ecae47ba4e9437ffd5083a437303f763e67098`.
- [Contributor submission](https://github.com/senyo888/codex-pets/issues/24).
- [Package and attribution](../pets/aureo/README.md).
- [Measured strict results](../pets/aureo/qa/atlas-validation.json).
- [Summary and exception record](../pets/aureo/qa/validation-summary.json).

Geometry, RGBA transparency, populated/unused cells and transparent RGB residue pass.
The full strict atlas result remains `ok: false`: it flags 11 partially transparent
green edge pixels across eight cells. Native-size visual severity has not been established.
The four cardinal gaze checks remain three passes and one failure: the screen-left
look frame faces right, as do several other left-sector poses. Sixteen populated look
cells are not represented as sixteen verified gaze directions. Native runtime behavior
has not been certified.

The catalogue validator recognizes only this pet ID and exact atlas hash. It also
pins the independent evidence file to SHA-256
`5be4d2822e06def461a34b1edfb88cca79360d7c772cb260df4a9abcbe76385d` and checks that the
summary preserves the failed results. All ordinary package, metadata, checksum,
preview, README, installer and identity checks still apply. Card and installer copy
must disclose the directional limitation; a strict "Validated" badge is not allowed.

This exception does not apply to another pet or a changed atlas. A new exception
requires its own explicit maintainer review and a separately reviewable contract
change; contributors cannot grant themselves an exception by adding a JSON flag.
Other pets continue to require the existing strict pass. CI exercises attempts to
reuse the exception, alter findings, or omit/corrupt assets.
