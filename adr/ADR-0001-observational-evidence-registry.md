# ADR-0001 -- Observational evidence registry rather than archive mirror

- **Status:** Proposed
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

The repository records source manifests, schemas, reproducible
normalization instructions, validation-set definitions, and small test
fixtures. Large upstream data remains in source archives unless a
specific derived artifact is approved for local storage. Every
validation set names the upstream sources, applied cuts, exposed
observables, units, provenance, and known caveats.

The first domain is Type Ia supernovae, but core schema concepts use
generic terms such as `object`, `observation`, `data_product`,
`source`, and `validation_set` so later domains can reuse them.

## Consequences

Positive:

- Avoids becoming a stale copy of TNS, WISeREP, or survey data
  releases.
- Keeps the repository focused on evidence that simulation workflows
  and human readers can audit.
- Makes later astronomy domains easier to add without rewriting a
  supernova-only data model.

Negative:

- Users need network access or downloaded upstream products to rebuild
  most artifacts.
- The repo must maintain adapters and source manifests instead of
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
