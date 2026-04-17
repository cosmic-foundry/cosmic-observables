import argparse
import json
import os
from pathlib import Path
from typing import Any

import yaml

from cosmic_observables.http_client import HTTPClient

TNS_API_URL = "https://www.wis-tns.org/api/get/object"
CATALOG_ID = "tns"

ROOT = Path(__file__).resolve().parents[3]
OBJECT_DIR = ROOT / "observables" / "sne-ia" / "objects"

TNS_FIXTURES = {
    "sn-1991bg": {
        "objname": "1991bg",
        "name_prefix": "SN",
        "radeg": 186.266958,
        "decdeg": 12.886972,
        "redshift": 0.0033,
        "hostname": "NGC 4374",
        "internal_names": ["NGC 4374-SN1"],
        "discoverydate": "1991-12-09",
        "type": "SN Ia-bg",
    },
    "sn-1991t": {
        "objname": "1991T",
        "name_prefix": "SN",
        "radeg": 190.813125,
        "decdeg": 2.637611,
        "redshift": 0.0058,
        "hostname": "NGC 4527",
        "internal_names": ["NGC 4527-SN1"],
        "discoverydate": "1991-04-13",
        "type": "SN Ia-91T-like",
    },
    "sn-1994d": {
        "objname": "1994D",
        "name_prefix": "SN",
        "radeg": 188.510208,
        "decdeg": 7.701306,
        "redshift": 0.0015,
        "hostname": "NGC 4526",
        "internal_names": ["NGC 4526-SN1"],
        "discoverydate": "1994-03-07",
        "type": "SN Ia",
    },
    "sn-1999by": {
        "objname": "1999by",
        "name_prefix": "SN",
        "radeg": 200.043958,
        "decdeg": 34.416611,
        "redshift": 0.0021,
        "hostname": "NGC 5174",
        "internal_names": ["NGC 5174-SN1"],
        "discoverydate": "1999-04-30",
        "type": "SN Ia-bg",
    },
    "sn-2002bo": {
        "objname": "2002bo",
        "name_prefix": "SN",
        "radeg": 154.527125,
        "decdeg": 21.828306,
        "redshift": 0.0042,
        "hostname": "NGC 3190",
        "internal_names": ["NGC 3190-SN1"],
        "discoverydate": "2002-03-09",
        "type": "SN Ia",
    },
    "sn-2005cf": {
        "objname": "2005cf",
        "name_prefix": "SN",
        "radeg": 230.384208,
        "decdeg": -7.413028,
        "redshift": 0.0065,
        "hostname": "MCG -01-39-003",
        "internal_names": ["MCG -01-39-003-SN1"],
        "discoverydate": "2005-05-28",
        "type": "SN Ia",
    },
    "sn-2009ig": {
        "objname": "2009ig",
        "name_prefix": "SN",
        "radeg": 348.898125,
        "decdeg": 9.242917,
        "redshift": 0.0088,
        "hostname": "NGC 7425",
        "internal_names": ["NGC 7425-SN1"],
        "discoverydate": "2009-08-20",
        "type": "SN Ia",
    },
    "sn-2011fe": {
        "objname": "2011fe",
        "name_prefix": "SN",
        "radeg": 210.7738875,
        "decdeg": 54.348969444444,
        "redshift": 0.000804,
        "hostname": "M101",
        "internal_names": ["PTF11kly", "Gaia11aan"],
        "discoverydate": "2011-08-24",
        "type": "SN Ia",
    },
    "sn-2014j": {
        "objname": "2014J",
        "name_prefix": "SN",
        "radeg": 148.9255,
        "decdeg": 69.673861,
        "redshift": 0.0007,
        "hostname": "M82",
        "internal_names": ["M82-SN1"],
        "discoverydate": "2014-01-21",
        "type": "SN Ia",
    },
    "sn-2021aefx": {
        "objname": "2021aefx",
        "name_prefix": "SN",
        "radeg": 58.00392,
        "decdeg": -36.26297,
        "redshift": 0.005117,
        "hostname": "NGC 1566",
        "internal_names": ["DLT21an", "ZTF21acbeufr"],
        "discoverydate": "2021-11-11",
        "type": "SN Ia",
    },
}


def get_tns_object(objname: str) -> dict[str, Any] | None:
    api_key = os.environ.get("TNS_API_KEY")
    bot_id = os.environ.get("TNS_BOT_ID")

    if not api_key or not bot_id:
        slug = f"sn-{objname.lower()}"
        return TNS_FIXTURES.get(slug)

    client = HTTPClient()
    # Real TNS API call
    marker = {"tns_id": bot_id, "type": "bot", "name": "CosmicFoundryBot"}
    headers = {"User-Agent": f"tns_marker{json.dumps(marker)}"}
    data = {"objname": objname}
    payload = {"api_key": api_key, "data": json.dumps(data)}

    response = client.post(TNS_API_URL, data=payload, headers=headers)
    response.raise_for_status()
    result = response.json()
    reply = result.get("data", {}).get("reply")
    if isinstance(reply, dict):
        return reply
    return None


def map_tns_to_object_manifest(tns_data: dict[str, Any], slug: str) -> dict[str, Any]:
    prefix = tns_data.get("name_prefix", "SN")
    name = tns_data.get("objname", "")
    full_name = f"{prefix} {name}"

    tns_type = tns_data.get("type", "SN Ia")
    cf_type = "sne-ia" if "Ia" in tns_type else "unknown"

    subtype = None
    if "bg" in tns_type.lower():
        subtype = "91bg-like"
    elif "91t" in tns_type.lower():
        subtype = "91T-like"
    else:
        subtype = "normal"

    aliases = [{"id": full_name, "catalog": CATALOG_ID, "match_type": "name"}]
    for internal_name in tns_data.get("internal_names", []):
        aliases.append(
            {"id": internal_name, "catalog": "literature", "match_type": "name"}
        )

    manifest = {
        "id": slug,
        "name": full_name,
        "domain": ["sne-ia"],
        "tns_name": full_name,
        "coordinates": {
            "ra": tns_data.get("radeg"),
            "dec": tns_data.get("decdeg"),
            "source": CATALOG_ID,
        },
        "redshift": {
            "value": tns_data.get("redshift"),
            "source_type": "literature",
            "catalog": CATALOG_ID,
        },
        "classification": {
            "type": cf_type,
            "subtype": subtype,
            "confidence": "secure",
            "catalog": CATALOG_ID,
        },
        "aliases": aliases,
    }

    if tns_data.get("hostname"):
        manifest["host_galaxy"] = {
            "name": tns_data.get("hostname"),
            "catalog": CATALOG_ID,
        }
    if tns_data.get("discoverydate"):
        manifest["first_observed"] = tns_data.get("discoverydate", "").split()[0]

    return manifest


def update_manifest(slug: str, dry_run: bool = True) -> None:
    manifest_path = OBJECT_DIR / f"{slug}.yaml"
    objname = slug.replace("sn-", "")

    print(f"Fetching TNS data for {objname}...")
    tns_data = get_tns_object(objname)
    if not tns_data:
        print(f"No TNS data for {objname}")
        return

    new_data = map_tns_to_object_manifest(tns_data, slug)

    if manifest_path.exists():
        with open(manifest_path) as f:
            existing = yaml.safe_load(f)

        # Merge logic for Phase 3: preserve existing non-TNS aliases
        existing_aliases = existing.get("aliases", [])
        new_aliases = new_data["aliases"]

        alias_ids = {a["id"] for a in new_aliases}
        for alias in existing_aliases:
            if alias["id"] not in alias_ids:
                new_aliases.append(alias)

        new_data["aliases"] = new_aliases

    if dry_run:
        print(f"--- Dry run: {manifest_path} ---")
        print(yaml.dump(new_data, sort_keys=False))
    else:
        with open(manifest_path, "w") as f:
            yaml.dump(new_data, f, sort_keys=False)
        print(f"Updated {manifest_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="TNS Adapter")
    parser.add_argument("--slug", help="Object slug (e.g. sn-2011fe)")
    parser.add_argument(
        "--all", action="store_true", help="Update all canonical objects"
    )
    parser.add_argument(
        "--write", action="store_true", help="Write changes to manifest files"
    )
    args = parser.parse_args()

    slugs = []
    if args.all:
        slugs = list(TNS_FIXTURES.keys())
    elif args.slug:
        slugs = [args.slug]
    else:
        parser.print_help()
        return

    for slug in slugs:
        update_manifest(slug, dry_run=not args.write)


if __name__ == "__main__":
    main()
