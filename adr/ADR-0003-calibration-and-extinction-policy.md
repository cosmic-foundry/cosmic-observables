# ADR-0003 — Calibration and extinction policy for photometric observables

- **Status:** Proposed
- **Date:** 2026-04-17
- **Deciders:** Agent

## Context

Photometric light curves (magnitudes and fluxes) are reported differently across astronomical surveys. Some releases provide "as-observed" (instrumental or calibrated observer-frame) values, while others apply corrections for:
1. **Galactic Extinction**: Dust in our own Milky Way that reddens and dims the light.
2. **K-correction**: Shifting the spectrum from the observer's frame to the rest frame (or a standard bandpass) to account for cosmological expansion.

Simulations in `cosmic-foundry` generally model these physical effects themselves. Comparing a simulation output to an observational validation set requires knowing exactly which corrections have already been applied to the empirical data to avoid "double-correcting" or comparing incompatible quantities.

## Decision

All normalized photometric artifacts in this repository must explicitly record the status of physical corrections at the row level.

1.  **Mandatory Columns**: Every photometry artifact must include `galactic_extinction_corrected` and `k_corrected` boolean columns.
2.  **Raw Preference**: Adapters should favor "as-observed" (uncorrected) observer-frame data whenever available. If the upstream source provides both corrected and uncorrected columns, the uncorrected ones should be used for the primary `magnitude` and `flux` columns, and the flags set to `false`.
3.  **Corrected Data Handling**: If an upstream source *only* provides corrected data, or if a specific validation set requires corrected data (e.g., for simple luminosity-distance comparisons), the flags must be set to `true`.
4.  **Metadata Requirement**: When `galactic_extinction_corrected` or `k_corrected` is `true`, the adapter author must record the specific model, law, or reference used for the correction (e.g., "Schlafly & Finkbeiner 2011", "Fitzpatrick 1999 $R_V=3.1$") in the `caveats` section of the validation-set manifest or in the `notes` of the artifact provenance sidecar.

## Consequences

- **Positive**: Eliminates ambiguity in simulation-to-observation comparisons. Ensures that "double-correction" errors are caught by inspecting the artifact metadata.
- **Negative**: Adds a small amount of overhead to adapter development, requiring authors to explicitly confirm the correction status of upstream data rather than assuming defaults.
- **Neutral**: Most initial Type Ia adapters (CSP DR3, Foundation) default to `false` as they provide high-quality observer-frame data.

## Alternatives considered

**Implicit "raw" default (no columns).**
Rejected because "raw" is not a universally shared default in the literature; many compilations (like those in Pantheon+) only provide corrected or standardized magnitudes.

**Validation-set level flags (single flag for the whole file).**
Rejected because some catalogs (like CfA) may be distributed as a mix of corrected and uncorrected measurements depending on the specific release table used. Row-level flags are more robust.

**IVOA/UCD mapping for corrections.**
Rejected as premature for Phase 4. While IVOA has concepts for corrected vs. uncorrected data, the simple boolean flags are sufficient for current simulation needs and are easier for human reviewers to verify.
