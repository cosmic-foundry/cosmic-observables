import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
OBJECT_ROOT = ROOT / "observables" / "sne-ia" / "objects"
CATALOG_ROOT = ROOT / "observables" / "sne-ia" / "catalogs"


def load_object_resolver() -> dict[str, str]:
    """
    Creates a mapping from all known aliases/IDs to their canonical object slug.
    Returns: Dict[id_string, object_slug]
    """
    resolver: dict[str, str] = {}
    for path in OBJECT_ROOT.glob("*.yaml"):
        with open(path) as f:
            obj = yaml.safe_load(f)
            slug = obj["id"]

            # Map slug itself
            resolver[slug] = slug
            # Map name
            resolver[obj["name"]] = slug
            # Map TNS name
            if obj.get("tns_name"):
                resolver[obj["tns_name"]] = slug
            # Map all aliases
            for alias in obj.get("aliases", []):
                aid = alias["id"]
                resolver[aid] = slug
                # Also map bare version if it starts with SN
                if aid.startswith("SN "):
                    resolver[aid.replace("SN ", "")] = slug

    return resolver


def check_catalog_coverage(
    artifact_path: Path, catalog_id: str
) -> tuple[int, int, set[str]]:
    """
    Checks how many rows in an artifact match known object manifests.
    """
    resolver = load_object_resolver()

    matched_count = 0
    total_count = 0
    unmatched_ids: set[str] = set()

    matched_slugs: set[str] = set()
    with open(artifact_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_count += 1
            obj_id = row["object_id"]

            if obj_id in resolver:
                matched_count += 1
                matched_slugs.add(resolver[obj_id])
            else:
                unmatched_ids.add(obj_id)

    print(f"--- Coverage for {catalog_id} ---")
    print(f"Total rows: {total_count}")
    print(f"Matched rows: {matched_count} ({matched_count/total_count*100:.1f}%)")
    print(
        f"Matched unique objects: {len(matched_slugs)} ({sorted(list(matched_slugs))})"
    )
    print(f"Unique unmatched IDs in CSV: {len(unmatched_ids)}")

    # Check for canonical objects specifically
    all_slugs = {path.stem for path in OBJECT_ROOT.glob("*.yaml")}
    missing_slugs = all_slugs - matched_slugs
    if missing_slugs:
        print(f"Missing canonical objects: {sorted(list(missing_slugs))}")

    return matched_count, total_count, unmatched_ids


if __name__ == "__main__":
    pantheon_path = ROOT / "artifacts" / "sne-ia" / "sne-ia-cosmology-distances.csv"
    if pantheon_path.exists():
        check_catalog_coverage(pantheon_path, "pantheon-plus")
    else:
        print("Artifact not found.")
