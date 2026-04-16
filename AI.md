# Agent Instructions

These instructions apply to all AI agents working in this repository.

## Development rules

Branch, PR, commit-size, history, and attribution discipline is
identical to `cosmic-foundry/cosmic-foundry`. Read `AI.md` in that
repository at the start of every session — it is the authoritative
source. The notes below cover only the details that differ for this
repository.

### Fork and upstream remotes

- Upstream repository: `cosmic-foundry/cosmic-observables`
- Fork (push target): `cosmic-foundry-development/cosmic-observables`

Open pull requests against the upstream:

```bash
gh pr create \
  --repo cosmic-foundry/cosmic-observables \
  --base main \
  --head cosmic-foundry-development:<topic-branch>
```

Do not rely on `gh`'s default-repo inference — state it explicitly,
as directed in `cosmic-foundry/cosmic-foundry` AI.md.

### Environment

This repository has no compiled or GPU dependencies. CI uses
`pip install -e .[test]` with Python 3.11. No conda environment is
required for CI, and there is no `agent_health_check.sh` here. For
local development, any environment with `jsonschema`, `pyyaml`, and
`pytest` is sufficient — the `cosmic_foundry` conda environment from
`cosmic-foundry/cosmic-foundry` provides a superset of these and
works fine if it is already active.

## Data rules

- Treat upstream archives and survey releases as authoritative for
  their own products. This repository records catalog metadata,
  provenance, schemas, manifests, and derived validation products.
- Record source licensing or access terms before adding generated
  artifacts.
- Every validation set must state:
  - the scientific question it validates,
  - the upstream catalogs it depends on,
  - the selection cuts or quality cuts applied,
  - the observables and units exposed to simulations,
  - known caveats and open questions.
- Large data artifacts should not be added directly to git unless a
  project decision explicitly approves it.

## Repository coordination

Reusable simulation-engine changes belong in `cosmic-foundry`.
Application-layer observational registry, data-model, and explorer
work belongs here. If a task spans repositories, use separate branches
and pull requests for each repository.
