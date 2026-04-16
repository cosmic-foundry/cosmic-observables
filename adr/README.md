# Architectural Decision Records

This directory records architectural decisions for Cosmic Observables.

## Index

- [ADR-0001](ADR-0001-observational-evidence-registry.md) --
  Observational evidence registry rather than archive mirror.
- [ADR-0002](ADR-0002-phase1-data-model.md) *(Accepted)* --
  Phase 1 data model: object identity (repo-internal slug IDs, cross-
  catalog alias records with match_type evidence), units policy (enum
  of valid unit strings, filter/system as separate fields), and artifact
  provenance (sidecar YAML written by adapters alongside each artifact).
