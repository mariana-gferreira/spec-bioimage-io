from contextlib import nullcontext
from copy import deepcopy
from pathlib import Path
from typing import Any, ContextManager, Dict, Mapping, Optional, Protocol, Sequence, Set, Type, Union

import jsonschema
import pytest
from deepdiff import DeepDiff
from pydantic import (
    DirectoryPath,
    TypeAdapter,
    ValidationError,
    create_model,  # type: ignore
)
from ruamel.yaml import YAML

from bioimageio.spec._description import InvalidDescription, build_description
from bioimageio.spec._internal.base_nodes import Node
from bioimageio.spec._internal.io_utils import download
from bioimageio.spec._internal.types import HttpUrl
from bioimageio.spec._internal.validation_context import ValidationContext
from bioimageio.spec.generic._v0_2_converter import DOI_PREFIXES

yaml = YAML(typ="safe")


unset = object()


def check_node(
    node_class: Type[Node],
    kwargs: Union[Dict[str, Any], Node],
    *,
    context: Optional[ValidationContext] = None,
    expected_dump_json: Any = unset,
    expected_dump_python: Any = unset,
    is_invalid: bool = False,
):
    if is_invalid:
        assert expected_dump_json is unset
        assert expected_dump_python is unset

    error_context: ContextManager = pytest.raises(ValidationError) if is_invalid else nullcontext()  # type: ignore
    with error_context:
        node = node_class.model_validate(
            kwargs,
            context=context or ValidationContext(root=Path(__file__).parent),
        )

    if expected_dump_json is not unset:
        actual = node.model_dump(mode="json")
        assert actual, expected_dump_json

    if expected_dump_python is not unset:
        actual = node.model_dump(mode="python")
        assert actual, expected_dump_python


class DummyNodeBase(Node):
    value: Any


def check_type(
    type_: Union[Any, Type[Any]],
    value: Any,
    expected: Any = unset,
    expected_deserialized: Any = unset,
    *,
    is_invalid: bool = False,
):
    type_adapter = TypeAdapter(type_)
    error_context: ContextManager = pytest.raises(ValidationError) if is_invalid else nullcontext()  # type: ignore

    with error_context:
        actual = type_adapter.validate_python(value)

    if expected is not unset:
        assert actual == expected, (actual, expected)

    if expected_deserialized is not unset:
        actual_deserialized = type_adapter.dump_python(actual, mode="json", exclude_unset=True)
        assert actual_deserialized == expected_deserialized, (actual_deserialized, expected_deserialized)

    node = create_model("DummyNode", value=(type_, ...), __base__=DummyNodeBase)
    with error_context:
        actual_node = node.model_validate(dict(value=value))

    if expected is not unset:
        assert actual_node.value == expected, (actual_node.value, expected)

    if expected_deserialized is not unset:
        node_deserialized = actual_node.model_dump(mode="json", exclude_unset=True)
        assert node_deserialized["value"] == expected_deserialized, (node_deserialized["value"], expected_deserialized)


def check_bioimageio_yaml(
    source: Union[Path, HttpUrl],
    /,
    *,
    root: Union[DirectoryPath, HttpUrl] = Path(),
    as_latest: bool,
    exclude_fields_from_roundtrip: Set[str] = set(),
    is_invalid: bool = False,
    bioimageio_json_schema: Optional[Mapping[Any, Any]],
) -> None:
    downloaded_source = download(source)
    root = downloaded_source.original_root
    with downloaded_source.path.open(encoding="utf-8") as f:
        data = yaml.load(f)

    format_version = "latest" if as_latest else "discover"
    with ValidationContext(root=root, file_name=downloaded_source.original_file_name):
        rd = build_description(deepcopy(data), as_format=format_version)
        assert not is_invalid or (is_invalid and isinstance(rd, InvalidDescription)), "Invalid RDF passed validation"

    summary = rd.validation_summary
    assert summary is not None
    if is_invalid:
        assert summary.status == "failed", "passes despite marked as known failure case"
        assert isinstance(rd, InvalidDescription)
        return

    assert summary.status == "passed", summary.format()
    assert rd is not None

    json_data = rd.model_dump(mode="json")
    # check compatibility to our latest json schema...
    if (
        bioimageio_json_schema is not None
        and "v0_" not in downloaded_source.path.name  # ...unless it's a historic example
    ):
        try:
            jsonschema.validate(json_data, bioimageio_json_schema)
        except jsonschema.ValidationError:
            # TODO: improve error message/log
            raise ValueError(f"jsonschema validation error for {downloaded_source.path}")

    if as_latest:
        return

    # check rountrip
    exclude_from_comp = {
        "format_version",
        "timestamp",
        *exclude_fields_from_roundtrip,
    }
    deserialized = rd.model_dump(mode="json", exclude=exclude_from_comp, exclude_unset=True)
    expect_back = {k: v for k, v in data.items() if k not in exclude_from_comp}
    assert_rdf_dict_equal(deserialized, expect_back, f"roundtrip {source}\n", ignore_known_rdf_diffs=True)


def assert_rdf_dict_equal(
    actual: Dict[Any, Any], expected: Dict[Any, Any], msg: str = "", *, ignore_known_rdf_diffs: bool = False
):
    diff: Any = DeepDiff(expected, actual)
    if ignore_known_rdf_diffs:
        slim_diff = deepcopy(diff)
        VC = "values_changed"
        k: Any
        for k in diff.get(VC, {}):
            if (
                isinstance(k, str)
                and k.startswith("root['cite'][")
                and k.endswith("]['doi']")
                and any(diff[VC][k]["old_value"].startswith(dp) for dp in DOI_PREFIXES)
            ):
                # 1. we dop 'https://doi.org/' from cite.i.doi field
                slim_diff[VC].pop(k)

        if VC in slim_diff and not slim_diff[VC]:
            slim_diff.pop(VC)

        diff = slim_diff

    assert not diff, msg + diff.pretty()


class ParameterSet(Protocol):
    def __init__(self, values: Sequence[Any], marks: Any, id: str) -> None:
        super().__init__()
