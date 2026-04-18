# Closure Note — cosmic-observables

## What happened

The project adopted a platform/application repository architecture
(recorded in cosmic-foundry ADR-0014). Under that architecture:

- **cosmic-foundry** is the organizational platform. It provides all
  reusable computation and data-pipeline infrastructure.
- **Application repositories** (one per simulation domain) provide
  domain-specific physics implementations and domain-specific
  observational validation data.

This repository accumulated two distinct categories of content that
now belong in two different places:

1. **Data-pipeline infrastructure** — the HTTP client, `ValidationAdapter`
   protocol, `Provenance` dataclass, bibliography generator, and base
   JSON schemas. These are general across all simulation domains and
   belong in the platform.

2. **SNIa observational content** — the Pantheon+, CSP DR3, Foundation,
   and TNS adapters; the cross-matching and alias-table utilities; the
   YAML manifests (catalogs, validation sets, objects, filters,
   filter-matches); domain-specific JSON schemas; and the built
   artifacts. These belong in the stellar-physics application repository,
   alongside the simulation code that will compare against them.

The data-pipeline infrastructure (category 1) has already been
migrated: `cosmic_foundry.manifests` now lives in cosmic-foundry and
ships as the `[observational]` optional extra. The SNIa content
(category 2) has not been migrated yet — it remains here until the
stellar-physics application repository is ready to receive it.

## Current state

- This repository is **not yet archived**. It remains in its last
  working state and its tests continue to pass.
- cosmic-foundry PR #89 (which lands `cosmic_foundry.manifests`)
  is pending merge as of the time this note was written.
- The stellar-physics application repository does not exist yet.

## Migration plan for the SNIa content

When the stellar-physics application repository is ready, the following
content moves there:

**Adapters and utilities**
- `src/cosmic_observables/adapters/` — Pantheon+, CSP DR3, Foundation,
  TNS adapters; update imports to use `cosmic_foundry.manifests`
  (`ValidationAdapter`, `Provenance`, `HTTPClient`) instead of the
  local equivalents.
- `src/cosmic_observables/alias_table.py` and `cross_match.py`.

**Manifests and schemas**
- `observables/sne-ia/` — catalog, validation-set, object, filter,
  and filter-match YAML manifests.
- `schemas/` — domain-specific JSON schemas (`photometry`, `filter`,
  `filter-match`, `object`); these extend the platform base schemas
  from `cosmic_foundry.manifests`.

**Artifacts**
- `artifacts/sne-ia/` — built artifact files and provenance sidecars.

**ADRs**
- `adr/ADR-0001`, `ADR-0002`, `ADR-0003` — recontextualize for their
  new home before migrating.

**Tests**
- `tests/` — migrate and update alongside the code they cover.

After migration, this repository should be archived on GitHub with a
pointer to its two successor locations.

## What does NOT move to the stellar-physics application repository

The infrastructure that was in `src/cosmic_observables/http_client.py`,
`provenance.py`, `bibliography.py`, and the base schema validation
machinery now lives in `cosmic_foundry.manifests` (cosmic-foundry
`[observational]` extra). The `ValidationAdapter` protocol
(`adapter.py`) also lives there — the stellar-physics application
repository implements the protocol, it does not re-define it. All
application repos should depend on `cosmic_foundry.manifests`, not
re-implement any of it.
