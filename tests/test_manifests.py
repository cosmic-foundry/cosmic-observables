from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def _load_schema(name: str) -> dict:
    return json.loads((ROOT / "schemas" / name).read_text())


def _load_yaml(path: Path) -> dict:
    loaded = yaml.safe_load(path.read_text())
    assert isinstance(loaded, dict), f"{path} did not parse to a mapping"
    return loaded


def test_source_manifests_match_schema() -> None:
    schema = _load_schema("source.schema.json")
    validator = Draft202012Validator(schema)
    paths = sorted((ROOT / "observables" / "sne-ia" / "sources").glob("*.yaml"))
    assert paths

    for path in paths:
        manifest = _load_yaml(path)
        validator.validate(manifest)
        assert manifest["id"] == path.stem


def test_validation_set_manifests_match_schema() -> None:
    schema = _load_schema("validation-set.schema.json")
    validator = Draft202012Validator(schema)
    paths = sorted(
        (ROOT / "observables" / "sne-ia" / "validation-sets").glob("*.yaml")
    )
    assert paths

    for path in paths:
        manifest = _load_yaml(path)
        validator.validate(manifest)
