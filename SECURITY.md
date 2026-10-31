# Security policy

## Report a vulnerability privately

Use [GitHub private vulnerability reporting](https://github.com/senyo888/codex-pets/security/advisories/new)
to contact this repository's maintainers. Please avoid posting exploit details,
credentials, or personal information in public issues or pull requests while a
report is being assessed.

Include the affected commit or release, file or dependency, reproduction steps,
expected and actual behaviour, and the practical impact. A minimal example with
synthetic data is preferable to real credentials or private files. Coordinate
public disclosure through the private report so a fix and upgrade guidance can
be prepared.

## Versions and updates

Use the current `main` branch or the
[latest published release](https://github.com/senyo888/codex-pets/releases/latest)
when checking for security fixes. Reports about older releases are welcome;
include the exact version and whether the issue also affects current code.
Historical release tags and assets are retained rather than rewritten.

Repository tooling dependencies and pet package versions are separate. Follow the
[maintenance instructions](docs/MAINTENANCE.md) to update the Python environment;
a tooling fix does not necessarily require reinstalling pets or changing their
sprite version.

## System and trust boundaries

Codex Pets contains pet artwork and metadata under `pets/`, a static catalogue and
installer pages under `site/`, Python maintenance and validation tools under
`scripts/`, and GitHub Actions workflows under `.github/workflows/`. It has no
repository-owned application backend or account service. The desktop app owns
installed pet playback and handling of installation links.

Contributed images, metadata, source changes, and pull requests are untrusted
inputs. Local tools process files selected by their operator; CI also processes
contributed files on GitHub-hosted runners. Maintainer review and repository
permissions separate contributions from published packages and the public site.
Pull-request code execution is not an image sandbox and must not be given
publication credentials.

## Security properties

- Image tooling must bound encoded input, dimensions, and frame counts before
  expensive decoding or allocation, and reject malformed or unsupported inputs.
- Catalogue metadata, package paths, recorded hashes, previews, and installer
  references must remain consistent with the reviewed package assets.
- Pull-request validation must not expose secrets or obtain release or site
  deployment authority. Workflow permissions should be limited to their purpose.
- Credentials, private machine paths, and private maintainer records must not be
  published in repository files, generated artifacts, or logs.

## Assessment and limitations

Report reachable failures in these boundaries, vulnerable dependencies, unsafe
workflow permissions, credential exposure, or malicious package and installer
behaviour. Include how an attacker controls the input and who or what is affected;
this helps distinguish a security issue from a rendering or quality defect. These
examples do not exclude other security findings.

CodeQL, Gitleaks, dependency alerts, and catalogue/image checks provide different
forms of evidence. Passing them does not prove that arbitrary artwork is safe,
that dependencies have no undiscovered vulnerabilities, or that the external
desktop runtime is secure. Catalogue hashes check consistency; they do not by
themselves authenticate a download. Links that use `main` can change as new commits
are published. See [maintenance and security checks](docs/MAINTENANCE.md) for the
controls currently configured.
