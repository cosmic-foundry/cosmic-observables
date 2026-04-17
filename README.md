# Cosmic Observables

## Current Status

- **Active Phase**: [Phase 3 — Object identity and source cross-matching](ROADMAP.md#phase-3----object-identity-and-source-cross-matching)
- **Latest Milestone**: First reproducible Type Ia validation product (Phase 2).
- **Full Roadmap**: See [ROADMAP.md](ROADMAP.md).

Cosmic Observables is the empirical reference layer for the Cosmic
Foundry organization. It organizes published astronomy observations
so simulation outputs can be validated against traceable, reviewable,
human-explorable evidence rather than against ad hoc tables.

The first target is Type Ia supernova observational data. The design
is deliberately broader than supernovae: the same registry and
provenance model should later cover other transients, stellar
observables, galaxy surveys, and cosmology validation products.

## Goals

- Track observational evidence with provenance, source citations,
  licensing notes, content hashes, schema versions, and reproducible
  fetch / normalization instructions.
- Separate upstream archives from local validation products. This
  repository should not become a mirror of WISeREP, TNS, survey
  releases, or journal tables.
- Preserve the context needed for simulation validation: calibration
  system, filters, selection cuts, classification confidence,
  redshift source, host association, reduction pipeline, covariance,
  and known caveats.
- Provide human-facing documentation and explorer-ready metadata so
  people can inspect why a validation set exists and what it can
  safely test.

## Initial scope: Type Ia supernovae

The Type Ia seed scope is organized around the sources in
[`observables/sne-ia/catalogs`](observables/sne-ia/catalogs) and the
validation products in
[`observables/sne-ia/validation-sets`](observables/sne-ia/validation-sets).

The initial catalog inventory covers:

- TNS for transient identity, naming, coordinates, classifications,
  and discovery / classification reports.
- WISeREP for spectra, photometry, and source-file availability.
- Pantheon+ / SH0ES for cosmology-ready standardized Type Ia
  distance products and covariance.
- DES-SN 5YR for deep rolling-survey light curves and cosmology
  samples.
- ZTF Type Ia DR1 for untargeted low-redshift discovery and light
  curves.
- CSP DR3, Foundation, CfA, SDSS-II SN, and CNIa0.02 for low-redshift
  calibration, nearby objects, and historical light-curve / spectral
  coverage.

## Repository layout

```text
ROADMAP.md                   Project roadmap and open planning questions.
adr/                         Architectural decisions for this repo.
schemas/                     JSON Schemas for evidence metadata.
observables/
  sne-ia/
    catalogs/                One manifest per upstream data catalog.
    validation-sets/         Simulation-facing validation products.
docs/                        Human-facing notes and explorer content.
src/cosmic_observables/      Future library code.
tests/                       Future schema and ingestion tests.
```

## Data policy

Large upstream data products should stay in their original archive
unless a reviewable reason exists to store a derived artifact here.
Small fixtures may live in git. Larger normalized artifacts should use
Git LFS, object storage, or archival release assets with recorded
hashes and generation scripts.

No observation should be hand-edited. Normalized products are produced
by scripted adapters from versioned upstream inputs.

## Relationship to cosmic-foundry

`cosmic-foundry` owns the simulation engine and synthetic-observable
generation. `cosmic-observables` owns empirical evidence packages,
validation-set definitions, and human-explorable observational context.
The link between the two should be a stable validation artifact:
simulation outputs are compared to named observable products with
explicit units, tolerances, covariance, and selection criteria.

## Roadmap

The projected development plan lives in [`ROADMAP.md`](ROADMAP.md).
It is intentionally a living document: update it as source adapters,
schemas, validation products, and Cosmic Foundry integration points
become concrete.
