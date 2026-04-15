# Agent Instructions

These instructions apply to all AI agents working in this repository.

## Development rules

- Work on topic branches and land changes via pull request.
- Keep commits small and logically scoped.
- Do not commit API keys, tokens, or credentials.
- Do not include local absolute filesystem paths in commit messages,
  pull request titles, pull request descriptions, ADRs, or persistent
  metadata.
- When changing observational facts, cite the upstream source in the
  changed file.
- Do not hand-edit normalized data products. Add or update a scripted
  adapter instead.

## Data rules

- Treat upstream archives and survey releases as authoritative for
  their own products. This repository records source metadata,
  provenance, schemas, manifests, and derived validation products.
- Record source licensing or access terms before adding generated
  artifacts.
- Every validation set must state:
  - the scientific question it validates,
  - the upstream sources it depends on,
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
