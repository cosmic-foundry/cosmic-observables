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

### ADR and documentation

Every new architectural decision (ADR) under `adr/` must be accompanied by a corresponding documentation stub in `docs/adr/`. The documentation stub must use the Sphinx `{include}` directive to pull in the content from the root-level ADR file. This ensures the ADR is indexed by the documentation site and prevents `sphinx-build` failures for missing cross-references.

Example stub (`docs/adr/ADR-NNNN-title.md`):
```markdown
# ADR-NNNN: Title

```{include} ../../adr/ADR-NNNN-title.md
```
```

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

## Roadmap Discipline

To ensure continuity across sessions and clarity for reviewers:

1.  **Handshake**: At the start of every session, read `ROADMAP.md` in full to identify the current active Phase and completed deliverables.
2.  **Alignment**: Every PR must include a "Roadmap Alignment" section (see PR template) stating which Phase/Deliverable it addresses.
3.  **Progression**: If a task completes a Roadmap deliverable, propose an update to `ROADMAP.md` (checking the box or updating the Status) as part of the same PR.
4.  **Phase Transition Review**: Upon completion of a Roadmap Phase (all deliverables checked, status marked Complete), the agent MUST perform a comprehensive review of the codebase, roadmap, and architecture documents. The goal is to identify learnings from the completed phase that necessitate updates to future phase goals or architectural ADRs before initiating work on the next phase.
5.  **Hand-off**: In the final turn of a session, explicitly state the current Roadmap status (e.g., "Phase 3 is 100% complete; pending Phase Transition Review").

## Technical Reasoning

Astronomy data is heterogeneous and prone to ID collisions. When resolving cross-catalog identities or recording physical quantities:

1.  **Skepticism**: Do not assume two objects with the same ID string are the same physical event. Verify using coordinates (RA/Dec separation) and redshifts.
2.  **Order of Magnitude**: Perform "sanity check" calculations for discrepancies. (e.g., a 50-degree separation is a different constellation; a 5-arcmin separation is a host-galaxy-scale disagreement).
3.  **Physical Context**: Validate metadata against physical reality (e.g., does the reported redshift match the recession velocity of the assigned host galaxy?).
4.  **Evidence over Truth**: Use the `disagreements` schema and `manual` match-type notes to record conflicting evidence rather than silently averaging or selecting one "truth."

## Bot Etiquette and Identity

This repository uses a centralized `HTTPClient` for external data access. Agents must distinguish between research and automated identities:

1.  **Research Identity**: For one-time tasks such as initial data ingestion, schema research, or building a new adapter, use the `STANDARD_UA` (browser-like) and disable strict `robots.txt` enforcement. This represents the agent acting as a human researcher.
2.  **Automated Identity**: For recurring tasks, published code, CI workflows, and user-facing APIs, use the `BOT_UA` (`CosmicFoundryBot`) and enforce `robots.txt` strictly. This ensures the project remains a transparent and accountable citizen of the astronomical data community.
