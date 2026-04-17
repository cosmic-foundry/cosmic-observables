from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "observables" / "sne-ia" / "catalogs"
OBJECT_DIR = ROOT / "observables" / "sne-ia" / "objects"
VALIDATION_SET_DIR = ROOT / "observables" / "sne-ia" / "validation-sets"
LITERATURE_SENTINEL = "literature"


def _load_schema(name: str) -> dict:
    return json.loads((ROOT / "schemas" / name).read_text())


def _load_yaml(path: Path) -> dict:
    loaded = yaml.safe_load(path.read_text())
    assert isinstance(loaded, dict), f"{path} did not parse to a mapping"
    return loaded


def _valid_artifact_provenance_manifest() -> dict:
    return {
        "validation_set_id": "sne-ia-cosmology-distances",
        "built_at": "2026-04-16T13:00:00Z",
        "adapter": {
            "script": "src/cosmic_observables/adapters/pantheon_plus.py",
            "version": "0123456789abcdef0123456789abcdef01234567",
        },
        "upstream": {
            "catalog": "pantheon-plus",
            "release": "Pantheon+SH0ES",
            "url": "https://example.org/pantheon-plus.tar.gz",
            "retrieved_at": "2026-04-16T12:00:00Z",
            "content_hash": {
                "algorithm": "sha256",
                "value": "a" * 64,
            },
        },
        "artifact": {
            "path": "artifacts/sne-ia/sne-ia-cosmology-distances.parquet",
            "content_hash": {
                "algorithm": "sha256",
                "value": "b" * 64,
            },
            "row_count": 1701,
        },
    }


def _catalog_ids() -> set[str]:
    return {path.stem for path in CATALOG_DIR.glob("*.yaml")}


def _validation_set_ids() -> set[str]:
    return {path.stem for path in VALIDATION_SET_DIR.glob("*.yaml")}


def _provenance_paths() -> list[Path]:
    return sorted(
        path for path in ROOT.rglob("*.provenance.yaml") if ".git" not in path.parts
    )


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


def test_object_manifests_match_schema() -> None:
    schema = _load_schema("object.schema.json")
    validator = Draft202012Validator(
        schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    paths = sorted(OBJECT_DIR.glob("*.yaml"))
    assert paths

    for path in paths:
        manifest = _load_yaml(path)
        validator.validate(manifest)
        assert manifest["id"] == path.stem


def test_object_alias_catalogs_exist() -> None:
    allowed_catalogs = _catalog_ids() | {LITERATURE_SENTINEL}
    assert allowed_catalogs

    for path in sorted(OBJECT_DIR.glob("*.yaml")):
        manifest = _load_yaml(path)
        for alias in manifest.get("aliases", []):
            assert alias["catalog"] in allowed_catalogs, (
                f"{path.name}: alias id '{alias['id']}' references "
                f"unknown catalog '{alias['catalog']}'"
            )


def test_object_provenance_catalogs_exist_or_are_literature() -> None:
    allowed_sources = _catalog_ids() | {LITERATURE_SENTINEL}
    assert allowed_sources

    for path in sorted(OBJECT_DIR.glob("*.yaml")):
        manifest = _load_yaml(path)
        references = {
            "coordinates.source": manifest["coordinates"]["source"],
            "redshift.catalog": manifest["redshift"]["catalog"],
            "classification.catalog": manifest["classification"]["catalog"],
        }
        if "host_galaxy" in manifest and "catalog" in manifest["host_galaxy"]:
            references["host_galaxy.catalog"] = manifest["host_galaxy"]["catalog"]

        for field, value in references.items():
            assert value in allowed_sources, (
                f"{path.name}: {field} references unknown provenance source "
                f"'{value}'"
            )


def test_manifest_ids_are_globally_unique() -> None:
    seen: dict[str, Path] = {}
    manifest_paths = [
        *CATALOG_DIR.glob("*.yaml"),
        *OBJECT_DIR.glob("*.yaml"),
        *VALIDATION_SET_DIR.glob("*.yaml"),
    ]
    assert manifest_paths

    for path in sorted(manifest_paths):
        manifest = _load_yaml(path)
        manifest_id = manifest["id"]
        assert manifest_id not in seen, (
            f"{path}: duplicate manifest id '{manifest_id}' already used by "
            f"{seen[manifest_id]}"
        )
        seen[manifest_id] = path


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
        assert manifest["id"] == path.stem


def test_validation_sets_reference_existing_catalogs() -> None:
    catalog_ids = _catalog_ids()
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


def test_adapter_ready_validation_sets_use_release_pinned_catalogs() -> None:
    catalogs = {path.stem: _load_yaml(path) for path in CATALOG_DIR.glob("*.yaml")}
    assert catalogs

    for path in sorted(VALIDATION_SET_DIR.glob("*.yaml")):
        manifest = _load_yaml(path)
        if manifest["status"] not in {"implementing", "available"}:
            continue

        for catalog_id in manifest["upstream_catalogs"]:
            assert "release" in catalogs[catalog_id], (
                f"{path.name}: adapter-ready validation set references "
                f"catalog '{catalog_id}' without a release pin"
            )


def test_available_validation_sets_reject_source_native_units() -> None:
    schema = _load_schema("validation-set.schema.json")
    validator = Draft202012Validator(
        schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    manifest = _load_yaml(VALIDATION_SET_DIR / "sne-ia-nearby-calibrators.yaml")
    manifest["status"] = "available"

    with pytest.raises(ValidationError):
        validator.validate(manifest)


def test_artifact_provenance_sidecars_match_schema() -> None:
    schema = _load_schema("artifact-provenance.schema.json")
    validator = Draft202012Validator(
        schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    paths = _provenance_paths()
    assert paths

    for path in paths:
        manifest = _load_yaml(path)
        validator.validate(manifest)


def test_artifact_provenance_sidecars_reference_existing_manifests() -> None:
    catalog_ids = _catalog_ids()
    validation_set_ids = _validation_set_ids()

    for path in _provenance_paths():
        manifest = _load_yaml(path)
        assert manifest["validation_set_id"] in validation_set_ids, (
            f"{path}: references unknown validation set "
            f"'{manifest['validation_set_id']}'"
        )
        assert manifest["upstream"]["catalog"] in catalog_ids, (
            f"{path}: references unknown upstream catalog "
            f"'{manifest['upstream']['catalog']}'"
        )


def test_artifact_provenance_sidecars_reference_existing_adapter_scripts() -> None:
    for path in _provenance_paths():
        manifest = _load_yaml(path)
        adapter_path = ROOT / manifest["adapter"]["script"]
        assert adapter_path.is_file(), (
            f"{path}: references missing adapter script "
            f"{manifest['adapter']['script']}"
        )


def test_artifact_provenance_schema_accepts_minimal_sidecar() -> None:
    schema = _load_schema("artifact-provenance.schema.json")
    validator = Draft202012Validator(
        schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    manifest = _valid_artifact_provenance_manifest()

    validator.validate(manifest)


@pytest.mark.parametrize(
    "missing_field",
    ["adapter", "upstream", "artifact"],
)
def test_artifact_provenance_schema_requires_provenance_blocks(
    missing_field: str,
) -> None:
    schema = _load_schema("artifact-provenance.schema.json")
    validator = Draft202012Validator(
        schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    manifest = _valid_artifact_provenance_manifest()
    del manifest[missing_field]

    with pytest.raises(ValidationError):
        validator.validate(manifest)


@pytest.mark.parametrize(
    ("field_path", "value"),
    [
        (("upstream", "content_hash", "algorithm"), "md5"),
        (("upstream", "content_hash", "value"), "abc"),
        (("artifact", "content_hash", "value"), "A" * 64),
        (("artifact", "row_count"), -1),
        (("artifact", "path"), "/tmp/generated.parquet"),
        (("artifact", "path"), "../generated.parquet"),
    ],
)
def test_artifact_provenance_schema_rejects_ambiguous_artifacts(
    field_path: tuple[str, ...],
    value: object,
) -> None:
    schema = _load_schema("artifact-provenance.schema.json")
    validator = Draft202012Validator(
        schema,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    manifest = _valid_artifact_provenance_manifest()
    target = manifest
    for key in field_path[:-1]:
        target = target[key]
    target[field_path[-1]] = value

    with pytest.raises(ValidationError):
        validator.validate(manifest)
