---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.7
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Cosmic Observables Documentation

Cosmic Observables organizes empirical astronomy reference data for
simulation validation and human exploration.

```{toctree}
:maxdepth: 2
:caption: Contents:

sne-ia/index
ROADMAP
adr/index
```

## Quick Look: Pantheon+ Hubble Diagram

The first validation product delivered is the **Pantheon+ SH0ES** standardized distance sample. This diagram is generated live from the 1,701 supernovae in the `sne-ia-cosmology-distances` artifact.

```{code-cell} python3
:tags: [hide-input]

import csv
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Paths
artifact_path = Path("../artifacts/sne-ia/sne-ia-cosmology-distances.csv")

# Load data using csv module
data = []
with open(artifact_path, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append({
            'redshift': float(row['redshift']),
            'distance_modulus': float(row['distance_modulus']),
            'distance_modulus_err': float(row['distance_modulus_err'])
        })

redshifts = np.array([d['redshift'] for d in data])
mus = np.array([d['distance_modulus'] for d in data])
mu_errs = np.array([d['distance_modulus_err'] for d in data])

# Filter for low-z to fit H_0 (where the linear relation holds best)
# We typically fit in the range 0.02 < z < 0.15
fit_mask = (redshifts > 0.02) & (redshifts < 0.15)
z_fit = redshifts[fit_mask]
mu_fit_data = mus[fit_mask]
mu_err_fit = mu_errs[fit_mask]

# Theory: mu = 5 * log10(z) + A
# where A = 25 + 5 * log10(c / H0)
# We solve for A using weighted least squares (weights = 1/err^2)
z_term = 5 * np.log10(z_fit)
weights = 1.0 / mu_err_fit**2
A_fit = np.average(mu_fit_data - z_term, weights=weights)

# Calculate H_0 from A
# H0 = c * 10^((25-A)/5)
c = 299792.458 # km/s
H0 = c * 10**((25 - A_fit) / 5)

# Generate fit line for plotting across the full range
z_range = np.geomspace(redshifts.min(), redshifts.max(), 100)
mu_model = 5 * np.log10(z_range) + A_fit

# Plot
plt.figure(figsize=(10, 6))
plt.errorbar(redshifts, mus, yerr=mu_errs,
             fmt='o', markersize=2, alpha=0.2, label='Pantheon+ SH0ES Data', color='gray')
plt.plot(z_range, mu_model, color='red', lw=2, label=f'Best fit: $H_0 \\approx {H0:.1f}$ km/s/Mpc')

plt.xscale('log')
plt.xlabel('Redshift ($z_{cmb}$)')
plt.ylabel('Distance Modulus ($\mu$ [mag])')
plt.title('Hubble Diagram & $H_0$ Fit (Pantheon+ SH0ES)')
plt.grid(True, which="both", ls="-", alpha=0.1)
plt.legend()
plt.show()
```

## Quick Look: Nearby Calibration Light Curves (CSP DR3)

New in Phase 4: multi-band photometry for nearby supernovae. Below are the $B$ and $V$ light curves for **SN 2005am** from the **CSP DR3** validation artifact.

```{code-cell} python3
:tags: [hide-input]

import csv
import matplotlib.pyplot as plt
from pathlib import Path

# Paths
lc_path = Path("../artifacts/sne-ia/sne-ia-nearby-calibrators.csv")

# Load data
lc_data = []
if lc_path.exists():
    with open(lc_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['object_id'] == 'sn-2005am':
                lc_data.append({
                    'mjd': float(row['mjd']),
                    'mag': float(row['magnitude']),
                    'err': float(row['magnitude_err']),
                    'filter': row['filter']
                })

if lc_data:
    plt.figure(figsize=(10, 5))

    colors = {'csp-dr3-b': 'blue', 'csp-dr3-v': 'green'}
    for band in ['csp-dr3-b', 'csp-dr3-v']:
        points = [d for d in lc_data if d['filter'] == band]
        if points:
            mjds = [p['mjd'] for p in points]
            mags = [p['mag'] for p in points]
            errs = [p['err'] for p in points]

            # Find t_max (approximate)
            t_max = mjds[mags.index(min(mags))]
            phases = [t - t_max for t in mjds]

            plt.errorbar(phases, mags, yerr=errs, fmt='o', label=band.upper(), color=colors.get(band, 'gray'))

    plt.gca().invert_yaxis()
    plt.xlabel('Relative Phase [days]')
    plt.ylabel('Apparent Magnitude')
    plt.title('Light Curve: SN 2005am (CSP DR3)')
    plt.grid(alpha=0.2)
    plt.legend()
    plt.show()
else:
    print("No data found for SN 2005am in artifact.")
```

## Getting Started

Start with the [Type Ia supernova observables](sne-ia/index) or review the [Architectural Decision Records](adr/index).
