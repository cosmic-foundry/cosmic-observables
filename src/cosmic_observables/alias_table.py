import sys
from pathlib import Path
from typing import Any

import numpy as np  # type: ignore
import yaml

from cosmic_observables.http_client import HTTPClient

# Paths
ROOT = Path(__file__).resolve().parents[2]
OBJECT_ROOT = ROOT / "observables" / "sne-ia" / "objects"
PANTHEON_URL = "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/Pantheon%2B_Data/4_DISTANCES_AND_COVAR/Pantheon%2BSH0ES.dat"


def get_canonical_objects() -> list[dict[str, Any]]:
    objects = []
    for path in OBJECT_ROOT.glob("*.yaml"):
        with open(path) as f:
            objects.append(yaml.safe_load(f))
    return objects


def angular_separation(ra1: Any, dec1: Any, ra2: Any, dec2: Any) -> Any:
    """Simple angular separation in degrees."""
    ra1, dec1, ra2, dec2 = map(np.radians, [ra1, dec1, ra2, dec2])
    cos_val = np.sin(dec1) * np.sin(dec2) + np.cos(dec1) * np.cos(dec2) * np.cos(
        ra1 - ra2
    )
    cos_val = np.clip(cos_val, -1.0, 1.0)
    return np.degrees(np.arccos(cos_val))


def main() -> None:
    # 1. Fetch Pantheon+ data
    sys.path.append(str(ROOT / "src"))

    client = HTTPClient()
    print(f"Fetching Pantheon+ metadata from {PANTHEON_URL}...")
    resp = client.get(PANTHEON_URL)
    resp.raise_for_status()

    lines = resp.text.splitlines()
    header = lines[0].split()
    idx_cid = header.index("CID")
    idx_ra = header.index("RA")
    idx_dec = header.index("DEC")

    # 2. Extract unique Pantheon+ objects with coordinates
    pantheon_objects = {}
    for line in lines[1:]:
        parts = line.split()
        cid = parts[idx_cid]
        ra = float(parts[idx_ra])
        dec = float(parts[idx_dec])
        if cid not in pantheon_objects:
            pantheon_objects[cid] = {"ra": ra, "dec": dec}

    # 3. Match against canonical manifests
    canonical_objs = get_canonical_objects()
    matches = []
    unmatched = []

    # Hardened threshold: names must match AND coordinates must be within 10 arcmin
    # (Allows for 2011fe's 4.5 arcmin discrepancy while rejecting the 2009ig collision)
    match_threshold_deg = 10.0 / 60.0

    for cid, p_obj in pantheon_objects.items():
        found = False
        for c_obj in canonical_objs:
            # 1. Check if name is a potential match
            c_names = [c_obj["id"], c_obj["name"], c_obj.get("tns_name", "")]
            for alias in c_obj.get("aliases", []):
                c_names.append(alias["id"])

            clean_names = [n.replace("SN ", "").lower() for n in c_names if n]
            name_potential = cid.lower() in clean_names

            # 2. Calculate separation
            sep = angular_separation(
                p_obj["ra"],
                p_obj["dec"],
                c_obj["coordinates"]["ra"],
                c_obj["coordinates"]["dec"],
            )

            # 3. Final matching rule:
            # Require EITHER a tight coordinate match (< 30 arcsec)
            # OR a name match verified by a loose coordinate check (< 10 arcmin)
            is_match = (sep < (30.0 / 3600.0)) or (
                name_potential and sep < match_threshold_deg
            )

            if is_match:
                matches.append(
                    {
                        "pantheon_cid": cid,
                        "canonical_slug": c_obj["id"],
                        "separation_arcsec": float(sep * 3600.0),
                        "match_basis": (
                            "name-verified-by-coordinate"
                            if name_potential
                            else "coordinate-match"
                        ),
                    }
                )
                found = True
                break

        if not found:
            unmatched.append(
                {"pantheon_cid": cid, "ra": p_obj["ra"], "dec": p_obj["dec"]}
            )

    # 4. Output the alias table
    output_path = ROOT / "observables" / "sne-ia" / "pantheon_plus_aliases.yaml"
    with open(output_path, "w") as f:
        yaml.dump(
            {
                "catalog": "pantheon-plus",
                "matches": matches,
                "unmatched_count": len(unmatched),
                "unmatched_samples": unmatched[:10],
            },
            f,
            sort_keys=False,
        )

    print(f"Generated alias table at {output_path}")
    print(f"Matches: {len(matches)}")
    print(f"Unmatched: {len(unmatched)}")


if __name__ == "__main__":
    main()
