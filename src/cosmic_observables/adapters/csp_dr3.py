import csv
import hashlib
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

from cosmic_observables.cross_match import load_object_resolver
from cosmic_observables.http_client import STANDARD_UA, HTTPClient

UPSTREAM_URL = "https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-source=J/AJ/154/211/OptPhot&-out.all"
CATALOG_ID = "csp-dr3"
VALIDATION_SET_ID = "sne-ia-nearby-calibrators"

ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_DIR = ROOT / "artifacts" / "sne-ia"
ARTIFACT_PATH = ARTIFACT_DIR / f"{VALIDATION_SET_ID}.csv"
PROVENANCE_PATH = ARTIFACT_DIR / f"{VALIDATION_SET_ID}.provenance.yaml"

# Filter mapping: VizieR column names to our registry IDs
FILTER_MAP = {
    "Bmag": "csp-dr3-b",
    "Vmag": "csp-dr3-v",
}
ERROR_MAP = {
    "Bmag": "e_Bmag",
    "Vmag": "e_Vmag",
}


def get_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_data() -> tuple[str, str]:
    # Use Research Mode for ingestion
    client = HTTPClient(user_agent=STANDARD_UA, respect_robots=False)
    print(f"Fetching {UPSTREAM_URL}...")
    response = client.get(UPSTREAM_URL)
    response.raise_for_status()
    content = response.text
    return content, get_sha256(content.encode("utf-8"))


def normalize_data(content: str) -> tuple[list[dict[str, str]], int]:
    resolver = load_object_resolver()
    lines = content.splitlines()

    # 1. Locate data section (after header comments and dashed lines)
    data_start = 0
    for i, line in enumerate(lines):
        if line.startswith("-------"):
            data_start = i + 1
            break

    if data_start == 0:
        return [], 0

    # 2. Parse TSV data
    # Columns: recno, Camera, SN, JD, umag, e_umag, gmag, e_gmag, rmag, e_rmag,
    # imag, e_imag, Bmag, e_Bmag, Vmag, e_Vmag
    # Index mapping:
    # SN: 2, JD: 3, Bmag: 12, e_Bmag: 13, Vmag: 14, e_Vmag: 15
    output_rows = []

    for line in lines[data_start:]:
        parts = line.split("\t")
        if len(parts) < 15:
            continue

        raw_sn = parts[2].strip()
        jd = parts[3].strip()

        # Resolve Object Slug
        sn_query = raw_sn.replace("SN", "")
        slug = resolver.get(sn_query) or resolver.get(raw_sn)
        if not slug:
            continue

        # Convert JD to MJD: MJD = JD - 2400000.5
        try:
            mjd = float(jd) - 2400000.5
        except ValueError:
            continue

        # Extract B and V bands
        for mag_col, filter_id in FILTER_MAP.items():
            idx_mag = 12 if mag_col == "Bmag" else 14
            idx_err = 13 if mag_col == "Bmag" else 15

            mag_val = parts[idx_mag].strip()
            err_val = parts[idx_err].strip()

            if mag_val and err_val:
                output_rows.append(
                    {
                        "object_id": slug,
                        "mjd": f"{mjd:.2f}",
                        "magnitude": mag_val,
                        "magnitude_err": err_val,
                        "filter": filter_id,
                        "magnitude_system": "Vega",
                        "time_system": "MJD",
                        "galactic_extinction_corrected": "false",
                        "k_corrected": "false",
                    }
                )

    return output_rows, len(output_rows)


def write_provenance(upstream_hash: str, artifact_hash: str, row_count: int) -> None:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    import subprocess

    try:
        git_version = (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .decode("utf-8")
            .strip()
        )
    except Exception:
        git_version = "unknown"

    provenance = {
        "validation_set_id": VALIDATION_SET_ID,
        "built_at": now,
        "adapter": {
            "script": str(Path(__file__).relative_to(ROOT)),
            "version": git_version,
        },
        "upstream": {
            "catalog": CATALOG_ID,
            "release": "DR3",
            "url": UPSTREAM_URL,
            "retrieved_at": now,
            "content_hash": {
                "algorithm": "sha256",
                "value": upstream_hash,
            },
        },
        "artifact": {
            "path": str(ARTIFACT_PATH.relative_to(ROOT)),
            "content_hash": {
                "algorithm": "sha256",
                "value": artifact_hash,
            },
            "row_count": row_count,
        },
    }

    with open(PROVENANCE_PATH, "w") as f:
        yaml.dump(provenance, f, sort_keys=False)
    print(f"Wrote provenance to {PROVENANCE_PATH}")


def main() -> None:
    sys.path.append(str(ROOT / "src"))
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    content, upstream_hash = fetch_data()
    rows, row_count = normalize_data(content)

    fieldnames = [
        "object_id",
        "mjd",
        "magnitude",
        "magnitude_err",
        "filter",
        "magnitude_system",
        "time_system",
        "galactic_extinction_corrected",
        "k_corrected",
    ]

    with open(ARTIFACT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with open(ARTIFACT_PATH, "rb") as f:
        artifact_hash = get_sha256(f.read())

    print(f"Wrote {row_count} photometry points to {ARTIFACT_PATH}")
    write_provenance(upstream_hash, artifact_hash, row_count)


if __name__ == "__main__":
    main()
