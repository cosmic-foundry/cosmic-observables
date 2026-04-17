import csv
import hashlib
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

from cosmic_observables.cross_match import load_object_resolver
from cosmic_observables.http_client import STANDARD_UA, HTTPClient

TABLE2_URL = "https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-source=J/MNRAS/475/193/table2&-out.all"
TABLE6_URL = "https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-source=J/MNRAS/475/193/table6&-out.all"
CATALOG_ID = "foundation"
VALIDATION_SET_ID = "sne-ia-nearby-calibrators"

ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_DIR = ROOT / "artifacts" / "sne-ia"
ARTIFACT_PATH = ARTIFACT_DIR / f"{VALIDATION_SET_ID}.csv"
PROVENANCE_PATH = ARTIFACT_DIR / f"{VALIDATION_SET_ID}.provenance.yaml"

# Filter mapping: VizieR filter strings to our registry IDs
FILTER_MAP = {
    "gP1": "foundation-g",
    "rP1": "foundation-r",
    "iP1": "foundation-i",
    "zP1": "foundation-z",
}


def get_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_tsv(url: str) -> tuple[str, str]:
    client = HTTPClient(user_agent=STANDARD_UA, respect_robots=False)
    print(f"Fetching {url}...")
    response = client.get(url)
    response.raise_for_status()
    content = response.text
    return content, get_sha256(content.encode("utf-8"))


def parse_vizier_tsv(content: str) -> list[list[str]]:
    lines = content.splitlines()
    data_start = 0
    for i, line in enumerate(lines):
        if line.startswith("-------"):
            data_start = i + 1
            break
    if data_start == 0:
        return []

    data = []
    for line in lines[data_start:]:
        parts = line.split("\t")
        data.append([p.strip() for p in parts])
    return data


def normalize_data(
    table2_content: str, table6_content: str
) -> tuple[list[dict[str, str]], int]:
    resolver = load_object_resolver()

    # 1. Parse Table 6 for MJDpeak and Redshift
    # Columns: recno, SN, zhelio, e_zhelio, zCMB, e_zCMB, MJDpeak, e_MJDpeak, ...
    # SN: 1, zhelio: 2, MJDpeak: 6, e_MJDpeak: 7
    sn_params = {}
    table6_data = parse_vizier_tsv(table6_content)
    for parts in table6_data:
        if len(parts) < 8:
            continue
        sn_name = parts[1]
        try:
            sn_params[sn_name] = {
                "z": float(parts[2]),
                "tmax": float(parts[6]),
                "e_tmax": float(parts[7]),
            }
        except ValueError:
            continue

    # 2. Parse Table 2 and Join
    # Columns: recno, SN, MJD, Filter, l_mag, mag, e_mag, Flux, e_Flux
    # SN: 1, MJD: 2, Filter: 3, mag: 5, e_mag: 6, Flux: 7, e_Flux: 8
    output_rows = []
    table2_data = parse_vizier_tsv(table2_content)
    for parts in table2_data:
        if len(parts) < 9:
            continue

        raw_sn = parts[1]
        mjd_str = parts[2]
        filter_raw = parts[3]
        mag_str = parts[5]
        mag_err_str = parts[6]
        flux_str = parts[7]
        flux_err_str = parts[8]

        # Resolve Object Slug
        slug = resolver.get(raw_sn)
        if not slug:
            # Try removing common prefixes if any
            slug = resolver.get(raw_sn.replace("SN", ""))

        if not slug:
            continue

        if not mag_str or not mag_err_str:
            continue

        params = sn_params.get(raw_sn)
        if not params:
            continue

        try:
            mjd = float(mjd_str)
            phase_obs = mjd - params["tmax"]
            phase_rest = phase_obs / (1.0 + params["z"])
            phase_err = params["e_tmax"]  # Simplification: phase error ~ tmax error
        except (ValueError, ZeroDivisionError):
            continue

        filter_id = FILTER_MAP.get(filter_raw, f"foundation-{filter_raw.lower()}")

        output_rows.append(
            {
                "object_id": slug,
                "mjd": f"{mjd:.3f}",
                "magnitude": mag_str,
                "magnitude_err": mag_err_str,
                "flux": flux_str,
                "flux_err": flux_err_str,
                "filter": filter_id,
                "magnitude_system": "AB",
                "time_system": "MJD",
                "phase_observer": f"{phase_obs:.3f}",
                "phase_rest": f"{phase_rest:.3f}",
                "phase_err": f"{phase_err:.2f}",
                "quality_flag": "",
                "galactic_extinction_corrected": "false",
                "k_corrected": "false",
            }
        )

    return output_rows, len(output_rows)


def write_provenance(
    table2_hash: str, table6_hash: str, artifact_hash: str, row_count: int
) -> None:
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
            "release": "Foley+2018",
            "tables": [
                {"name": "table2", "url": TABLE2_URL, "hash": table2_hash},
                {"name": "table6", "url": TABLE6_URL, "hash": table6_hash},
            ],
            "retrieved_at": now,
        },
        "artifact": {
            "path": str(ARTIFACT_PATH.relative_to(ROOT)),
            "content_hash": {"algorithm": "sha256", "value": artifact_hash},
            "row_count": row_count,
        },
    }
    with open(PROVENANCE_PATH, "w") as f:
        yaml.dump(provenance, f, sort_keys=False)
    print(f"Wrote provenance to {PROVENANCE_PATH}")


def main() -> None:
    sys.path.append(str(ROOT / "src"))
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    t2_content, t2_hash = fetch_tsv(TABLE2_URL)
    t6_content, t6_hash = fetch_tsv(TABLE6_URL)

    rows, row_count = normalize_data(t2_content, t6_content)

    fieldnames = [
        "object_id",
        "mjd",
        "magnitude",
        "magnitude_err",
        "flux",
        "flux_err",
        "filter",
        "magnitude_system",
        "time_system",
        "phase_observer",
        "phase_rest",
        "phase_err",
        "quality_flag",
        "galactic_extinction_corrected",
        "k_corrected",
    ]

    # Note: This overwrites or appends?
    # Roadmap says: "Normalization adapters for CSP DR3 and Foundation releases."
    # CSP DR3 already wrote to ARTIFACT_PATH.
    # We should probably combine them if they target the same validation set.

    existing_rows = []
    if ARTIFACT_PATH.exists():
        with open(ARTIFACT_PATH) as f:
            reader = csv.DictReader(f)
            existing_rows = list(reader)

    # Filter out existing foundation rows if we are re-running
    existing_rows = [
        r for r in existing_rows if not r["filter"].startswith("foundation-")
    ]

    all_rows = existing_rows + rows

    with open(ARTIFACT_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    with open(ARTIFACT_PATH, "rb") as f:
        artifact_hash = get_sha256(f.read())

    print(
        f"Wrote {len(all_rows)} total photometry points to {ARTIFACT_PATH} "
        f"({row_count} from Foundation)"
    )
    write_provenance(t2_hash, t6_hash, artifact_hash, len(all_rows))


if __name__ == "__main__":
    main()
