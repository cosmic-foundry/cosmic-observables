# ADR-0002 — Phase 1 data model: object identity, units, and artifact provenance

- **Status:** Proposed
- **Date:** 2026-04-16

## Context

Phase 0 established catalog manifests, validation-set manifests, and
JSON schemas for both. The next layer — Phase 1 data-model hardening —
requires three decisions before any adapter can produce a normalized
artifact:

1. **Object identity.** Every validation set ultimately asks about a
   physical astronomical event (a Type Ia supernova) observed by
   multiple independent catalogs. Before photometry, spectra, or
   distances can be compared, there must be a schema for what an
   "object" is and for how cross-catalog ID matches are recorded.

2. **Units.** Several existing observables carry `unit: source-native`
   as a placeholder. Adapter code cannot produce usable output without
   a declared units policy. The units decision gates Phase 2.

3. **Artifact provenance.** The `build_plan` on validation sets is a
   planning record only (ADR-0001). Adapter outputs need a separate,
   machine-checkable provenance record — content hashes, adapter
   identity, upstream release pin — before reproducibility can be
   verified.

These three topics are addressed in one ADR because they are coupled:
units belong to observations, observations belong to objects, and the
artifact provenance record references both the upstream catalog release
and the normalized output that downstream validation sets consume.

### What "object" means here

A Type Ia supernova is a transient event: a white dwarf star explodes
at a specific location in the sky at a specific time. Multiple teams
observe it, name it independently, and publish measurements in separate
data releases. There is no community-wide shared primary key. Cross-
catalog matching is done by sky-coordinate proximity and name agreement,
and that matching is probabilistic — not a database join.

The community has relevant tools: TNS (the IAU-endorsed naming
authority for transients since 2016), SIMBAD, and NED maintain cross-
ID databases. These are queryable services, not pinnable data artifacts.
The astronomy community has partially solved the "are these the same
object?" question. What this repository needs to solve is narrower:
how to record cross-catalog matches as explicit, reproducible,
citable evidence so that a simulation validation can be audited.

Most objects in the first fixture set predate TNS (SN 1991bg, SN
1991T, SN 2005cf, SN 2011fe, and similar well-calibrated nearby
Type Ia supernovae were named before 2016). TNS coverage for
pre-2016 objects is incomplete and retroactive.

### What "units" means here

Astronomical photometry is reported in magnitudes, not in physical
flux units, and "magnitude" is not a single unit: it depends on
which filter (B, V, r, i, …) and which calibration system (Vega,
AB, SDSS). Spectra are reported as flux density per wavelength or
as relative (uncalibrated) flux. Different surveys use different
magnitude systems and filter profiles.

The `unit: source-native` placeholder in the current schemas defers
this entirely. Phase 1 must define a unit vocabulary that is
explicit enough for simulations to consume validation data without
guessing the calibration system, while remaining narrow enough to
implement without becoming a full IVOA integration.

### What "artifact provenance" means here

A validation artifact is the normalized data product consumed by
simulations: a table of distance moduli, a set of light curves, a
collection of spectral features. The current `build_plan.planned_from`
on validation-set manifests records planning intent only. A
reproducibility record requires: which adapter produced the artifact,
which upstream release was used (with content hash or pinned tag),
when it was produced, and what hash the output has. This information
lives alongside the artifact, not inside the validation-set manifest
(which describes the *intent*, not the *history*).

## Decision

### 1. Object identity

An object is represented as a YAML file under
`observables/<domain>/objects/`. The file records a repo-internal
canonical identifier, a human-readable name, coordinates, redshift,
classification, host galaxy, and a list of cross-catalog alias
records. Each alias record carries the external catalog ID, the
catalog name, and the match type (how this correspondence was
established).

**Canonical ID.** The repo-internal ID is a lowercase hyphen-slug
derived from the well-known historical name: `sn-2011fe`,
`sn-1991bg`. It is not the TNS name directly (TNS names contain
spaces and may not exist for pre-2016 objects), but the TNS
designation is recorded as a field when it exists. The ID matches
the filename stem.

**Coordinates, redshift, classification.** Each carries a `catalog`
field naming which data source provided the value. For Phase 1 the
schema records one working value per field, not a list of all
reported values. Tracking disagreements across catalogs is a Phase 3
concern.

**Alias records.** Each alias record has:
- `id`: the ID as it appears in that catalog
- `catalog`: the catalog manifest ID (must resolve to a manifest in
  `observables/<domain>/catalogs/`)
- `match_type`: one of `name`, `coordinate`, `name-and-coordinate`,
  `manual`
- `notes`: optional free-text explanation of the match evidence

`match_type: manual` is used when a human reviewer asserted the
match without a systematic coordinate or name check. It must include
a `notes` entry explaining the basis for the assertion.

**Fixture set.** Phase 1 delivers a 10-object canonical fixture set
of nearby well-studied Type Ia supernovae. These objects are chosen
because they appear across multiple catalogs in the Phase 0 inventory
and because they have published photometry suitable for validating
synthetic light curves. The specific objects are chosen in the
implementing PR.

### 2. Units policy

Unit strings are an enum. Only values from the list below are valid
in `observables[].unit` on validation-set manifests and in any
observation schema introduced in Phase 1 and later.

**Valid unit strings:**

| Unit string | Meaning |
|---|---|
| `mag` | Magnitude (filter and system declared separately) |
| `mag2` | Magnitude squared (covariance matrices) |
| `erg/s/cm2/Angstrom` | Spectral flux density, absolute calibration |
| `relative` | Spectral flux or photometry on an arbitrary scale; not flux-calibrated |
| `Angstrom` | Wavelength |
| `km/s` | Velocity (Doppler) |
| `day` | Time or phase |
| `dimensionless` | Dimensionless ratio (e.g. redshift) |
| `source-native` | Accepted placeholder — see below |

**`source-native` remains valid as an explicit deferral.** It signals
that the adapter or schema author has not yet resolved the unit for
this observable. It must not appear in any artifact that is marked
`status: available` on the validation set. Phase 2 adapter work on
any observable carrying `source-native` is blocked until that
observable's unit is resolved and the enum updated.

**Magnitude system and filter.** For photometric observables, `unit:
mag` alone is insufficient to make a measurement usable. Any schema
that introduces photometric observations must also carry:
- `filter`: a named passband (e.g. `CSP-B`, `PS1-g`, `SDSS-r`)
- `magnitude_system`: one of `AB`, `Vega`, `SDSS`, `source-native`

These are separate fields because the unit (mag) does not change
with filter or system; only the calibration context changes.

**Phase 2 gate.** No adapter producing photometric data may reach
`status: available` until `filter` and `magnitude_system` are
declared and non-`source-native`.

### 3. Artifact provenance

When an adapter produces a normalized artifact, it writes a provenance
sidecar file alongside the artifact. The sidecar is a YAML file named
`<validation-set-id>.provenance.yaml`. It is tracked in git for small
artifacts (fixtures, reference tables) and gitignored for large ones —
but the sidecar itself is always tracked, regardless of artifact size.

The sidecar schema requires:
- `validation_set_id`: must match the validation-set manifest `id`
- `built_at`: ISO 8601 timestamp
- `adapter.script`: repo-relative path to the script
- `adapter.version`: git commit SHA or tag at time of build
- `upstream.catalog`: catalog manifest ID
- `upstream.release`: release identifier (tag, version string, or
  commit SHA as appropriate for the upstream source)
- `upstream.url`: the URL from which the upstream data was fetched
- `upstream.retrieved_at`: ISO 8601 timestamp
- `upstream.content_hash.algorithm`: `sha256`
- `upstream.content_hash.value`: hex digest of the fetched upstream
  file(s)
- `artifact.path`: repo-relative path to the output artifact
- `artifact.content_hash.algorithm`: `sha256`
- `artifact.content_hash.value`: hex digest of the output artifact
- `artifact.row_count`: integer row count as a basic sanity check

The `build_plan` field on validation-set manifests is not modified
when a real artifact is built. It continues to record planning intent.
The sidecar is the reproducibility record; the manifest is the
human-readable description of intent.

## Consequences

**Positive:**

- Object identity is checkable: a simulation comparison can trace the
  specific alias record that links a Pantheon+ row to a TNS name to
  this repository's object file.
- Units are validated at schema level, not just by convention. The
  `source-native` placeholder remains usable but is now explicitly
  tagged as a deferral rather than silently accepted.
- Artifact provenance is machine-checkable: a reviewer can recompute
  the sha256 of the upstream input and output and compare to the
  sidecar.
- The manifest / sidecar separation keeps validation-set YAMLs
  human-editable (they describe intent) while making artifact
  history append-only (sidecars are written by adapters, not by hand).

**Negative:**

- Object files are a new schema type requiring their own JSON Schema,
  tests, and maintenance.
- The alias `match_type` vocabulary requires judgment: a contributor
  must decide whether a match is `name`, `coordinate`, or `manual`.
  This judgment is not machine-checkable.
- Sidecar files require discipline: an adapter author who forgets to
  write the sidecar leaves the artifact without a provenance record.
  CI cannot easily enforce sidecar freshness without a separate check.

**Neutral:**

- Pre-2016 objects will have `tns_name: null` or a retroactive TNS
  entry that may not be complete. This is an accurate representation
  of the state of the community's records, not a gap to be filled now.
- The fixture set of 10 objects is the first test of the object
  schema. Expect amendments when real adapter work reveals missing
  fields.

## Alternatives considered

**Canonical ID: use TNS AT/SN designation directly.**
TNS designations (e.g. "SN 2011fe") are the IAU-endorsed names and
would be most natural for post-2016 objects. Rejected because TNS
coverage of pre-2016 objects is retroactive and incomplete, TNS names
contain spaces requiring slug normalization anyway, and treating TNS
as the required canonical source would force a network dependency
(or a snapshot dependency) into the object-file creation workflow.
The repo-internal slug is stable without any external dependency.

**Canonical ID: opaque repository-local IDs (co-sne-ia-0001).**
Fully controlled and collision-free, but meaningless to a human
reading the YAML file. Rejected because the fixture set consists of
famous well-known objects; using their established names (slugified)
costs nothing and aids readability.

**Cross-catalog matches: flat alias list (IDs only, no match_type).**
Simpler. Rejected because the match_type is the core evidence: it
records *why* we believe two catalog entries are the same event. A
flat list hides the epistemological status of each match. For
simulation validation the distinction between a name-based match
(high confidence for a well-known object) and a coordinate-only match
(lower confidence, possible field confusion) is science-relevant.

**Cross-catalog matches: separate normalized cross-match table.**
Correct at large scale. Rejected as premature for a 10-object fixture
set. The alias list on the object file is simple enough to implement
and review; normalization can be extracted if Phase 3 scale demands it.

**Units: IVOA Unified Content Descriptors (UCDs).**
Formally correct and machine-interoperable with VO tools and
registries. Rejected for Phase 1 because UCDs require understanding
the IVOA vocabulary hierarchy, add a non-trivial tooling dependency,
and are unnecessary before simulation validation requires interop with
VO services. The short enum covers all observables in the current
validation sets. UCDs can be added as an annotation alongside unit
strings in a future amendment if VO interop becomes a goal.

**Artifact provenance: external build tool (DVC, Snakemake).**
Powerful and principled. Rejected because it requires all contributors
to install and understand the tool, and because the current validation
pipeline is simple enough that a sidecar YAML is the minimal
representation that makes reproducibility checkable. A build tool can
be layered on top later if the pipeline grows complex enough to
warrant it.

**Artifact provenance: embedded in the validation-set manifest.**
Would keep everything in one file per validation set. Rejected because
the manifest describes what the product *should* be; the provenance
record describes what *was* produced. These have different authors
(human for the manifest, adapter script for the sidecar) and different
update frequencies. Conflating them would require hand-editing
machine-generated content.

## Architecture stress-review note

*Run per `pr-review/architecture-checklist.md` before requesting human
review.*

**Problem boundary.** The problem is making the data-model layer of
cosmic-observables concrete enough for Phase 2 adapter work to begin.
Downstream cost being reduced: adapter authors guessing at unit
conventions (correctness), simulation comparison code assuming
cross-catalog ID matches that were never validated (correctness and
blast radius), and artifact reproducibility being unverifiable without
recorded hashes (operational). Out of scope: photometry observation
schemas (Phase 2), spectra schemas (Phase 5), full IVOA alignment
(future).

**Tiling tree** (three independent splits):

*Split 1 — Object canonical ID:*
- A. TNS name: natural for post-2016, incomplete pre-2016, requires
  network/snapshot dependency. Not chosen.
- B. Repo-internal slug from historical name: stable, human-readable,
  no external dependency, consistent across time periods. Chosen.
- C. Opaque local ID: stable but meaningless. Not chosen.
Branches are mutually exclusive (one identifier namespace); collectively
exhaustive (these cover all strategies the community uses).

*Split 2 — Cross-catalog match representation:*
- A. Flat alias list (IDs only): loses match evidence. Not chosen.
- B. Structured records with match_type: minimal, captures evidence.
  Chosen.
- C. Normalized cross-match table: correct at scale, premature for
  Phase 1. Explicitly deferred to Phase 3.
Mutually exclusive; collectively exhaustive at this design layer.

*Split 3 — Artifact provenance location:*
- A. Embedded in validation-set manifest: wrong author/frequency.
  Not chosen.
- B. Sidecar file per artifact: clean separation, minimal tooling.
  Chosen.
- C. External build tool: correct at scale, mandatory tool dependency.
  Deferred; can be layered onto B later.

**Concept ownership:**

```text
Concept          Owns                              Does not own
────────────────────────────────────────────────────────────────────
object           canonical ID, working             measurements, light
                 coordinates/redshift/              curves, spectra,
                 classification, alias evidence     derived quantities

alias            {catalog, external-id,             catalog data content
                 match_type, notes}: evidence
                 that two IDs are one event

unit string      a valid token from the enum        filter, magnitude
                                                    system (separate)

build_plan       planning intent: which catalogs    how it was actually
                 this validation set draws from     built (sidecar owns)

sidecar          how an artifact was built:         artifact content
                 adapter, upstream release,
                 content hashes, timestamp
```

**Real workflow stress tests:**

*Workflow 1 — "What do we know about SN 2011fe?"*
```
read objects/sne-ia/sn-2011fe.yaml
→ canonical ID: sn-2011fe, TNS name: SN 2011fe
→ coordinates, redshift (source: host-galaxy-spectrum, catalog: tns)
→ aliases:
    {id: PTF11kly, catalog: ptf, match_type: name-and-coordinate}
    {id: SN 2011fe, catalog: csp-dr3, match_type: name}
    ...
→ know which catalogs have data for this object
```
The API is clean: one file, all identity and provenance evidence in one place.

*Workflow 2 — "Verify the Pantheon+ adapter output is reproducible."*
```
read sne-ia-cosmology-distances.provenance.yaml
→ upstream.content_hash: sha256:abc...
→ sha256sum of local Pantheon+ download file: compare
→ artifact.content_hash: sha256:def...
→ sha256sum of local artifact file: compare
→ artifact.row_count: 1701 — does the file have 1701 rows?
```
All checks are mechanical. No interpretation required.

*Workflow 3 — "Run simulation comparison against cosmology distances."*
```
stellar-foundry loads sne-ia-cosmology-distances validation set
→ reads validation-set manifest: observables = [distance_modulus, redshift, covariance]
→ reads sidecar: artifact path, hash, row count
→ loads artifact
→ produces synthetic distance_modulus vs redshift
→ computes chi-squared against covariance
→ writes comparison result (format TBD — Phase 7)
```
The missing piece is the comparison-result schema (deferred to Phase 7
per ROADMAP). The validation set and sidecar are sufficient to load the
data; what to do with it is not this ADR's problem.

**Normalization trace:**

```
author writes object YAML
→ schema validation: required fields, alias structure, match_type enum
→ id == filename stem
→ alias.catalog resolves to existing catalog manifest (test)

adapter produces artifact:
→ fetch upstream (URL from catalog manifest)
→ record upstream content hash
→ normalize to schema (units enforced)
→ write artifact
→ record artifact content hash and row count
→ write sidecar YAML
→ CI: sidecar present and parseable; hashes are valid hex strings
```

**Ordering and fences:**
- Object file must exist before a validation set references it (to be
  enforced by a new test in the implementing PR).
- Catalog manifest must exist before an alias references it (enforced
  by extending existing reference tests).
- Upstream must be fetched before adapter runs (process ordering, not
  schema-enforced).
- Sidecar must be written atomically with artifact (convention;
  CI checks sidecar presence but not freshness in Phase 1).

**Alternative failure pass:**
- *Alias list secretly doing join-table work:* Yes. At Phase 1 scale
  (10 objects) this is fine. At Phase 3 scale (thousands of cross-
  matches) the alias list on each object file becomes a denormalized
  join table and should be extracted. This is named explicitly as a
  Phase 3 concern.
- *One coordinate record hides disagreements:* The single working
  coordinate hides the fact that CSP and TNS may report slightly
  different coordinates for the same object. Acceptable for Phase 1;
  coordinate disagreement tracking is Phase 3.
- *`match_type: manual` is uncheckable:* True. The `notes` requirement
  for manual matches is the mitigation; human review catches weak
  justifications. Machine enforcement is not possible for this type of
  judgment.
- *Sidecar discipline relies on adapter authors:* A missing sidecar
  leaves the artifact without provenance. CI can check that a sidecar
  file exists for each artifact file in the artifacts directory, but
  cannot check that the hashes are correct without re-running the
  adapter. This is a named operational risk.

**Decision delta:** Ready with named risks:
1. Alias list will need normalization at Phase 3 scale.
2. Coordinate disagreements across catalogs are unrepresented in Phase 1.
3. Sidecar freshness (stale sidecar after artifact update) requires
   adapter discipline; CI can only check presence, not correctness.
