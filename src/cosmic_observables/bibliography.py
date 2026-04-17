from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = ROOT / "artifacts"
CATALOG_ROOT = ROOT / "observables"


def get_catalog_path(catalog_id: str) -> Path:
    # Search for catalog file in the hierarchy
    for p in CATALOG_ROOT.rglob(f"catalogs/{catalog_id}.yaml"):
        return p
    raise FileNotFoundError(f"Catalog manifest not found: {catalog_id}")


def generate_bibliography() -> str:
    used_catalogs: set[str] = set()

    # 1. Scan provenance sidecars for used catalogs
    for sidecar in ARTIFACT_DIR.rglob("*.provenance.yaml"):
        with open(sidecar) as f:
            prov = yaml.safe_load(f)
            used_catalogs.add(prov["upstream"]["catalog"])

    if not used_catalogs:
        msg = "No artifacts found. Build artifacts to populate attribution."
        return f"# Bibliography\n\n{msg}"

    # 2. Collect references from used catalogs
    lines = [
        "# Bibliography",
        "",
        "This repository uses data from the following authoritative sources.",
        "",
    ]

    for catalog_id in sorted(used_catalogs):
        path = get_catalog_path(catalog_id)
        with open(path) as f:
            cat = yaml.safe_load(f)

        lines.append(f"## {cat['title']}")
        lines.append(f"**Authority:** {cat['provenance']['authority']}")
        lines.append(f"**Status:** {cat['provenance']['access']['status']}")
        lines.append("")

        if cat.get("references"):
            lines.append("### References")
            for ref in cat["references"]:
                line = f"- [{ref['label']}]({ref['url']})"
                if ref.get("bibcode"):
                    bib = ref["bibcode"]
                    line += f" ([{bib}](https://ui.adsabs.harvard.edu/abs/{bib}))"
                lines.append(line)
            lines.append("")

    return "\n".join(lines)


def main() -> None:
    bib_content = generate_bibliography()
    bib_path = ROOT / "BIBLIOGRAPHY.md"
    with open(bib_path, "w") as f:
        f.write(bib_content)
    print(f"Generated {bib_path}")


if __name__ == "__main__":
    main()
