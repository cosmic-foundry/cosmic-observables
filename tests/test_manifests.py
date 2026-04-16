from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "observables" / "sne-ia" / "sources"
VALIDATION_SET_DIR = ROOT / "observables" / "sne-ia" / "validation-sets"


def _load_schema(name: str) -> dict:
    return json.loads((ROOT / "schemas" / name).read_text())


def _load_yaml(path: Path) -> dict:
    loaded = yaml.safe_load(path.read_text())
    assert isinstance(loaded, dict), f"{path} did not parse to a mapping"
    return loaded


def test_source_manifests_match_schema() -> None:
    schema = _load_schema("source.schema.json")
    validator = Draft202012Validator(
        schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    paths = sorted(SOURCE_DIR.glob("*.yaml"))
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


def test_validation_sets_reference_existing_sources() -> None:
    source_ids = {path.stem for path in SOURCE_DIR.glob("*.yaml")}
    assert source_ids

    for path in sorted(VALIDATION_SET_DIR.glob("*.yaml")):
        manifest = _load_yaml(path)
        missing = set(manifest["upstream_sources"]) - source_ids
        assert not missing, f"{path} references unknown sources: {sorted(missing)}"


def test_validation_set_provenance_paths_exist() -> None:
    for path in sorted(VALIDATION_SET_DIR.glob("*.yaml")):
        manifest = _load_yaml(path)
        for source_path in manifest["provenance"]["created_from"]:
            resolved = ROOT / source_path
            assert resolved.is_file(), f"{path} references missing path: {source_path}"
