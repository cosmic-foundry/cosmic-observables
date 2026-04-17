import hashlib
from datetime import UTC, datetime
from pathlib import Path

import yaml

from cosmic_observables.http_client import HTTPClient

UPSTREAM_URL = "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat"
CATALOG_ID = "pantheon-plus"
RELEASE_COMMIT = "c447f0f"
VALIDATION_SET_ID = "sne-ia-cosmology-distances"

ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_DIR = ROOT / "artifacts" / "sne-ia"
ARTIFACT_PATH = ARTIFACT_DIR / f"{VALIDATION_SET_ID}.csv"
PROVENANCE_PATH = ARTIFACT_DIR / f"{VALIDATION_SET_ID}.provenance.yaml"


def get_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_data() -> tuple[bytes, str]:
    client = HTTPClient()
    print(f"Fetching {UPSTREAM_URL}...")
    response = client.get(UPSTREAM_URL)
    response.raise_for_status()
    content = response.content
    return content, get_sha256(content)


def normalize_data(content: bytes) -> tuple[str, int, str]:
    lines = content.decode("utf-8").splitlines()
    header = lines[0].split()

    # CID IDSURVEY zHD zHDERR zCMB zCMBERR zHEL zHELERR
    # m_b_corr m_b_corr_err_DIAG MU_SH0ES MU_SH0ES_ERR_DIAG ...
    # We want: CID, zCMB, MU_SH0ES, MU_SH0ES_ERR_DIAG
    try:
        idx_cid = header.index("CID")
        idx_zcmb = header.index("zCMB")
        idx_mu = header.index("MU_SH0ES")
        idx_mu_err = header.index("MU_SH0ES_ERR_DIAG")
    except ValueError as e:
        raise ValueError(f"Missing expected column in header: {e}") from None

    output_rows = ["object_id,redshift,distance_modulus,distance_modulus_err"]
    row_count = 0

    for line in lines[1:]:
        parts = line.split()
        if not parts:
            continue

        cid = parts[idx_cid]
        zcmb = parts[idx_zcmb]
        mu = parts[idx_mu]
        mu_err = parts[idx_mu_err]

        output_rows.append(f"{cid},{zcmb},{mu},{mu_err}")
        row_count += 1

    output_content = "\n".join(output_rows) + "\n"
    return output_content, row_count, get_sha256(output_content.encode("utf-8"))


def write_provenance(upstream_hash: str, artifact_hash: str, row_count: int) -> None:
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    provenance = {
        "validation_set_id": VALIDATION_SET_ID,
        "built_at": now,
        "adapter": {
            "script": str(Path(__file__).relative_to(ROOT)),
            "version": "1483f37a5dcfc5b6291ecfbdfc6cd37881aed4ad",
        },
        "upstream": {
            "catalog": CATALOG_ID,
            "release": RELEASE_COMMIT,
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
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    upstream_bytes, upstream_hash = fetch_data()
    output_text, row_count, artifact_hash = normalize_data(upstream_bytes)

    with open(ARTIFACT_PATH, "w") as f:
        f.write(output_text)
    print(f"Wrote {row_count} rows to {ARTIFACT_PATH}")

    write_provenance(upstream_hash, artifact_hash, row_count)


if __name__ == "__main__":
    main()
