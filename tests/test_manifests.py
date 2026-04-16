from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "observables" / "sne-ia" / "catalogs"
VALIDATION_SET_DIR = ROOT / "observables" / "sne-ia" / "validation-sets"


def _load_schema(name: str) -> dict:
    return json.loads((ROOT / "schemas" / name).read_text())


def _load_yaml(path: Path) -> dict:
    loaded = yaml.safe_load(path.read_text())
    assert isinstance(loaded, dict), f"{path} did not parse to a mapping"
    return loaded


def test_catalog_manifests_match_schema() -> None:
    schema = _load_schema("catalog.schema.json")
    validator = Draft202012Validator(
        schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    paths = sorted(CATALOG_DIR.glob("*.yaml"))
    assert paths

    for path in paths:
        manifest = _load_yaml(path)
        validator.validate(manifest)
        assert manifest["id"] == path.stem


def test_validation_set_manifests_match_schema() -> None:
    schema = _load_schema("validation-set.schema.json")
    validator = Draft202012Validator(
        schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    paths = sorted(VALIDATION_SET_DIR.glob("*.yaml"))
    assert paths

    for path in paths:
        manifest = _load_yaml(path)
        validator.validate(manifest)


def test_validation_sets_reference_existing_catalogs() -> None:
    catalog_ids = {path.stem for path in CATALOG_DIR.glob("*.yaml")}
    assert catalog_ids

    for path in sorted(VALIDATION_SET_DIR.glob("*.yaml")):
        manifest = _load_yaml(path)
        missing = set(manifest["upstream_catalogs"]) - catalog_ids
        assert not missing, f"{path} references unknown catalogs: {sorted(missing)}"


def test_validation_set_build_plan_paths_exist() -> None:
    for path in sorted(VALIDATION_SET_DIR.glob("*.yaml")):
        manifest = _load_yaml(path)
        for planned_path in manifest["build_plan"]["planned_from"]:
            resolved = ROOT / planned_path
            assert resolved.is_file(), f"{path} references missing path: {planned_path}"
