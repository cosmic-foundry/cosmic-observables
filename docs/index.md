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

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load data from the artifact
df = pd.read_csv("../artifacts/sne-ia/sne-ia-cosmology-distances.csv")

# Plot
plt.figure(figsize=(10, 6))
plt.errorbar(df['redshift'], df['distance_modulus'], yerr=df['distance_modulus_err'],
             fmt='o', markersize=2, alpha=0.3, label='Pantheon+ SH0ES')
plt.xscale('log')
plt.xlabel('Redshift (z_cmb)')
plt.ylabel('Distance Modulus (mag)')
plt.title('Hubble Diagram - Pantheon+ SH0ES')
plt.grid(True, which="both", ls="-", alpha=0.2)
plt.legend()
plt.show()
```

## Getting Started

Start with the [Type Ia supernova observables](sne-ia/index) or review the [Architectural Decision Records](adr/index).
