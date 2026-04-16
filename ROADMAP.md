# Cosmic Observables Roadmap

This roadmap is a living plan for turning Cosmic Observables from an
evidence-registry scaffold into a reusable validation layer for Cosmic
Foundry simulations and for human exploration of published astronomy
data.

The first domain is Type Ia supernovae. The architecture should stay
general enough to later support other transient classes, stellar
observables, galaxy surveys, and cosmology products.

## Guiding principles

- **Evidence before aggregation.** A row in a normalized table is only
  useful if its source, calibration, selection cuts, units, and caveats
  are still traceable.
- **Adapters before hand edits.** Derived products are rebuilt from
  source manifests and adapter code. Normalized data is not edited by
  hand.
- **Small reference fixtures before large mirrors.** Keep git focused
  on schemas, manifests, docs, tests, and small fixtures. Store large
  artifacts in release assets, object storage, Git LFS, or upstream
  archives with recorded hashes.
- **Machine validation and human explanation share one source of
  truth.** The same manifests that drive simulation comparisons should
  drive documentation and explorer pages.
- **Generalize after the first hard case.** Type Ia supernovae are
  complex enough to force identity, photometry, spectra, cosmology,
  selection, and provenance questions. Solve those carefully before
  widening the domain model.

## Phase 0 -- Bootstrap the evidence registry

Status: in progress.

Goal: make the repository reviewable and give future data work a
stable shape.

Deliverables:

- Repository instructions and data policy.
- ADR-0001 defining this repo as an evidence registry rather than an
  archive mirror.
- Initial Type Ia source manifests for TNS, WISeREP, Pantheon+,
  DES-SN 5YR, ZTF DR1, CSP DR3, Foundation, CfA, SDSS-II SN, and
  CNIa0.02.
- Initial validation-set manifests for standardized distances, nearby
  calibration light curves, and spectral feature evolution.
- JSON Schemas and tests for manifest shape, URL/date formats, source
  references, and provenance paths.

Exit criteria:

- All manifests validate in CI.
- The README and docs explain what belongs in this repo versus
  `cosmic-foundry`.
- A reviewer can tell which source should be adapted first and why.

## Phase 1 -- Data-model hardening

Goal: define the minimal stable vocabulary needed before ingestion
code starts producing artifacts.

Deliverables:

- Schemas for object identity, observations, photometric points,
  spectra, filters, data products, provenance records, and selection
  functions.
- A source-ID and validation-set-ID convention that can survive
  multiple astronomy domains.
- Explicit units policy, including where to use IVOA, Astropy,
  specutils, SVO Filter Profile Service, FITS, VOTable, Parquet, or
  Zarr conventions.
- A provenance model for publication references, release versions,
  retrieval dates, file hashes, transformation scripts, and generated
  artifact hashes.
- A decision on how source licenses and archive terms are represented
  before artifacts are stored.

Exit criteria:

- The schemas can represent one photometric source, one spectral
  source, and one cosmology compilation without source-specific
  escape hatches.
- Tests reject missing units, missing provenance, invalid source
  references, and ambiguous generated-artifact hashes.

## Phase 2 -- First reproducible Type Ia validation product

Goal: build one complete end-to-end validation product instead of
spreading effort thinly across every source.

Recommended first product: Pantheon+ standardized-distance validation.

Deliverables:

- Adapter that fetches or consumes the Pantheon+ release from a
  pinned source.
- Manifest recording source version, expected row counts, covariance
  dimensions, file hashes, and citation metadata.
- Normalized artifact for distance modulus, redshift, uncertainty,
  covariance, and sample metadata.
- Tests for row count, required columns, covariance shape, units, and
  a small set of known reference values.
- Documentation explaining what this product validates and what it
  does not validate.

Exit criteria:

- A fresh checkout can rebuild or verify the Pantheon+ validation
  product from recorded inputs.
- A simulation-facing API can load the product without knowing the
  upstream file layout.

## Phase 3 -- Object identity and source cross-matching

Goal: make object-level exploration reliable enough for humans and
for multi-source validation sets.

Deliverables:

- TNS adapter for metadata, names, aliases, coordinates,
  classifications, reports, and redshift / host fields where
  available.
- Alias table linking TNS names, historical SN names, survey IDs, and
  archive-specific object identifiers.
- Cross-match checks for Pantheon+ objects against TNS and source
  survey manifests.
- Rules for conflicts: coordinates, classification labels, host
  associations, redshifts, and duplicate aliases.

Exit criteria:

- The repo can answer "what do we know about this SN Ia?" for the
  first curated object set.
- Cross-source identifiers are represented as evidence, not silently
  collapsed into one canonical truth.

## Phase 4 -- Nearby photometric calibration set

Goal: create the first source-rich light-curve validation product for
synthetic Type Ia observables.

Recommended sources: CSP DR3 first, then Foundation, CNIa0.02, and
selected CfA releases.

Deliverables:

- Photometry schema with filter system, magnitude / flux convention,
  uncertainty, time system, observer/rest-frame phase metadata, and
  calibration provenance.
- Filter metadata policy using source-native passbands plus SVO or
  another documented passband reference where appropriate.
- Small fixture set of canonical nearby SNe Ia for tests and human
  explorer pages.
- Normalization adapters for one source at a time, beginning with CSP
  DR3 if access and terms are acceptable.
- Validation-set documentation for light-curve color, luminosity, and
  phase evolution comparisons.

Exit criteria:

- A synthetic light curve can be compared against a named nearby
  validation set with explicit filters, units, and source caveats.
- Cross-source calibration is not inferred without a recorded
  transformation.

## Phase 5 -- Spectral availability and feature benchmarks

Goal: establish spectral validation without prematurely bulk-mirroring
WISeREP.

Deliverables:

- Metadata-only WISeREP availability index for the first curated
  object set.
- Spectrum schema aligned with IVOA/specutils concepts: wavelength,
  flux density, units, frame, phase, calibration notes, source file,
  and citation.
- Benchmark definitions for Si II 6355 and other Type Ia spectral
  features, including measurement method metadata.
- Tests for wavelength coverage, phase availability, and feature
  extraction on small fixtures.

Exit criteria:

- A user can identify which spectra are suitable for a named feature
  benchmark.
- Derived velocities are reproducible from the recorded spectra and
  method metadata.

## Phase 6 -- Human explorer and documentation site

Goal: make the evidence graph understandable without requiring users
to read YAML files.

Deliverables:

- Static documentation pages generated from source manifests,
  validation-set manifests, and curated object metadata.
- Object pages for the first canonical SNe Ia.
- Source pages explaining provenance, terms, known caveats, and
  ingestion status.
- Validation-set pages explaining selection, observables, caveats, and
  intended simulation comparisons.
- Basic search or index pages by object, source, validation product,
  wavelength coverage, photometric band, and redshift range.

Exit criteria:

- A human can trace a validation value back to source data and caveats
  through the docs.
- Documentation generation fails when manifests are incomplete or
  internally inconsistent.

## Phase 7 -- Cosmic Foundry integration contract

Goal: define the stable boundary between empirical observables and
simulation outputs.

Deliverables:

- Python API for loading validation products by ID.
- Artifact format decision for simulation-facing products: likely
  tables plus covariance for scalar products, Zarr for larger gridded
  or time-series products, and source-native files retained as
  provenance inputs.
- Comparison-result schema for synthetic-observable validation runs:
  simulation run ID, validation product ID, metric, units, tolerance,
  covariance handling, plots, and provenance.
- Example integration with a lightweight synthetic Type Ia output or
  placeholder fixture until `cosmic-foundry` has the relevant physics.

Exit criteria:

- `cosmic-foundry` can consume a named validation product without
  depending on upstream archive-specific formats.
- Validation outputs can be linked back to the empirical product and
  displayed in the human explorer.

## Phase 8 -- Widen beyond Type Ia supernovae

Goal: use lessons from Type Ia data to decide how broad the repository
should become.

Candidate domains:

- Core-collapse and stripped-envelope supernovae.
- Kilonovae and gravitational-wave electromagnetic counterparts.
- Stellar evolution observables: HR diagrams, asteroseismology,
  surface abundances, clusters, and binary populations.
- Galaxy observables: luminosity functions, stellar mass functions,
  metallicity relations, star-formation histories, CGM/IGM absorption.
- Cosmology products: BAO, weak lensing, CMB-derived summaries,
  cluster counts, halo mass functions, and large-scale-structure
  statistics.

Decision points:

- Keep all observables in one repository or split mature domains into
  domain-specific repos.
- Which schema concepts are truly generic and which should remain
  domain-local.
- Which products are validation references and which are training /
  calibration references that should be kept separate.

Exit criteria:

- The Type Ia schema experience has been codified into an ADR before
  adding a second major domain.
- New domains can reuse the source, provenance, and validation-set
  machinery without copying supernova-specific assumptions.

## Open architectural questions

- Should normalized artifacts be versioned by git tag, release asset,
  DVC-like metadata, object-storage URI, or Zenodo DOI?
- How should private or rate-limited upstream APIs be represented in a
  reproducible open workflow?
- What is the minimum useful representation of a survey selection
  function?
- How do we distinguish validation data from calibration / fitting data
  when the same source release can serve both roles?
- Which passband and zeropoint source is authoritative for each
  photometric system?
- How much should the repo depend on Astropy ecosystem packages versus
  plain schemas and tables?
- What governance should approve adding large generated artifacts?

## Near-term issue backlog

- Add CI for `pytest`.
- Add schema validation for duplicate IDs across all manifest types.
- Add catalog license / terms fields with structured status instead of
  free text.
- Add a first object-identity schema and a 10-object canonical Type Ia
  fixture set.
- Choose the first Pantheon+ adapter strategy and pin exact upstream
  release inputs. Add a `release` field to the Pantheon+ catalog
  manifest before building the adapter — the current `provenance.accessed`
  date is not a release pin.
- Decide whether docs should use Sphinx/MyST, MkDocs, or a lighter
  static generator.
- Add a manifest changelog convention so observational fact updates
  are easy to review.

## Known deferred decisions (tracked risks)

These decisions are explicitly deferred and must be resolved before
the phase that first requires them.

### Units policy (required before Phase 2)

Several observables carry `unit: source-native` as an accepted
placeholder. Phase 1 data-model hardening must define an explicit units
policy before Phase 2 adapter work produces normalized artifacts.
Until then, `source-native` signals a known gap, not a resolved unit.
Phase 2 work on any catalog that uses `source-native` observables is
gated on Phase 1 delivering a units decision for that observable type.

### Comparison-result schema (required before stellar-foundry first comparison)

When a domain repository (e.g., `stellar-foundry`) runs a simulation
comparison against a validation product, the output format must be
defined before implementation begins. The comparison-result schema —
carrying simulation run ID, validation-product ID, metric, value,
units, tolerance, covariance handling, and provenance — should live in
`cosmic-observables` as the empirical side of the contract. This
ensures all domain repositories produce interoperable comparison
outputs and the human explorer (Phase 6) can display them uniformly.
This decision should be recorded as an ADR before the first comparison
is implemented in any domain repository.

### Artifact provenance model (required before Phase 2)

The `build_plan` on validation sets is a planning record only. It
records which catalog manifests a validation set will be built from,
but carries no content hashes, adapter script references, or upstream
release pins. Phase 1 data-model hardening must define the artifact
provenance concept — a separate schema capturing the full reproducible
record of how an artifact was produced — before Phase 2 builds the
first real adapter output.
