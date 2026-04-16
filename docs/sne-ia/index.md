# Type Ia Supernova Data Landscape

Type Ia observational data is distributed across identity services,
spectral archives, survey releases, historical literature tables, and
cosmology compilations. This repository starts by representing those
products as catalog manifests and validation-set definitions.

## Working model

- TNS anchors object identity and classification reports.
- WISeREP anchors spectra and related supernova data products.
- Survey releases anchor calibrated photometry and source-native
  sample definitions.
- Cosmology compilations anchor standardized-distance products and
  covariance.

## First validation products

1. Standardized distance validation from Pantheon+.
2. Nearby calibration-quality multi-band light curves from CSP,
   Foundation, CfA, and CNIa0.02.
3. Spectral feature and velocity benchmarks from WISeREP.

## Open questions

- Which upstream licenses allow redistribution of normalized tables?
- Which object-identity service should be canonical when TNS,
  historical names, survey IDs, and catalog aliases disagree?
- Which filter metadata source is authoritative for each survey
  passband?
- Which validation products are reserved for testing rather than
  tuning simulation parameters?
