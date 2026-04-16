# ADR-0001 -- Observational evidence registry rather than archive mirror

- **Status:** Accepted
- **Date:** 2026-04-15

## Context

The initial use case is organizing published Type Ia supernova
observations so Cosmic Foundry simulations can be validated against a
rich empirical reference set. The astronomy community already has
important upstream archives and survey releases: TNS for naming and
classification reports, WISeREP for supernova spectra and related
data, and survey-specific releases such as Pantheon+, DES-SN, ZTF,
CSP, Foundation, CfA, SDSS-II SN, and CNIa0.02.

Mirroring all of those products would duplicate community archives,
make licensing and storage harder, and still would not solve the
simulation-validation problem. Validation depends on provenance,
selection functions, calibration state, covariance, units, and source
caveats as much as on the measurements themselves.

## Decision

Cosmic Observables is an observational evidence registry and
validation-product repository, not a primary archive mirror.

The repository records catalog manifests, schemas, reproducible
normalization instructions, validation-set definitions, and small test
fixtures. Large upstream data remains in source archives unless a
specific derived artifact is approved for local storage. Every
validation set names the upstream catalogs, applied cuts, exposed
observables, units, build plan, and known caveats.

The first domain is Type Ia supernovae, but core schema concepts use
generic terms such as `object`, `observation`, `data_product`,
`catalog`, and `validation_set` so later domains can reuse them.

### Vocabulary

The following terms have specific meanings in this repository:

- **catalog** — an upstream data resource: an archive, survey release,
  compilation, or bibliographic service. Represented by a manifest in
  `observables/*/catalogs/`. The word "source" is deliberately avoided
  because in astronomy "source" means an astronomical object; using it
  for a data provider would cause ambiguity when object-identity
  schemas are introduced (Phase 1).

- **validation_set** — a curated selection of empirical measurements
  with explicit selection cuts, observable definitions, units, upstream
  catalog references, and known caveats. Intended for direct comparison
  against simulation outputs.

- **build_plan** — the planning record on a validation set: which
  catalog manifests it will be built from, and whether the artifact
  needs to be rebuilt. This is distinct from artifact provenance
  (content hashes, adapter scripts, upstream release pins), which will
  be formalized in Phase 1 data-model hardening.

- **object**, **observation**, **data_product** — reserved vocabulary
  for Phase 1 data-model hardening. These terms are not yet defined as
  schemas. Phase 1 will introduce object identity, photometry, spectra,
  filters, and provenance record schemas using these names.

- **domain** — an astrophysical domain tag. Valid values are defined as
  an enum in `schemas/catalog.schema.json` and
  `schemas/validation-set.schema.json`. Selection qualifiers such as
  "low-redshift" or "volume-limited" are not domain tags; they belong
  in selection cuts or the catalog role description.

## Consequences

Positive:

- Avoids becoming a stale copy of TNS, WISeREP, or survey data
  releases.
- Keeps the repository focused on evidence that simulation workflows
  and human readers can audit.
- Makes later astronomy domains easier to add without rewriting a
  supernova-only data model.
- The `catalog` / `object` vocabulary distinction prevents the naming
  collision that would arise in Phase 3 object-identity work if
  "source" were used for both data providers and astronomical objects.

Negative:

- Users need network access or downloaded upstream products to rebuild
  most artifacts.
- The repo must maintain adapters and catalog manifests instead of
  simply checking in tables.
- Some validation workflows will need release artifacts outside git.

## Alternatives considered

- **Mirror all available Type Ia data.** Simple for offline use, but
  duplicates authoritative archives and creates licensing, storage,
  and freshness problems.
- **Only link to external archives.** Easy to maintain, but does not
  provide normalized validation products, schemas, or reproducible
  comparison artifacts.
- **Start with a supernova-only schema.** Faster for the first target,
  but likely to obstruct later transient, stellar, galaxy, and
  cosmology observables.
- **Use "source" for data providers.** Natural language choice, but
  "source" is the standard astronomy term for an astronomical object
  (a source of radiation). Using it for data providers would create an
  unresolvable naming collision in Phase 3 when object-identity schemas
  are introduced. "Catalog" is the correct term for a curated data
  collection.

## Amendments

- **2026-04-15:** Accepted. Vocabulary section added to define
  `catalog`, `validation_set`, `build_plan`, `domain`, and the
  reserved terms `object`/`observation`/`data_product`. "Source"
  renamed to "catalog" throughout schemas, manifests, and tests to
  prevent naming collision with the astronomical meaning of "source".
  `provenance` on validation sets renamed to `build_plan` with
  `planned_from` (was `created_from`) to distinguish planning intent
  from artifact provenance, which is deferred to Phase 1.
