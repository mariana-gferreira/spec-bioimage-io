from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pytest

from bioimageio.spec._internal.constants import WARNING
from bioimageio.spec._internal.validation_context import ValidationContext
from bioimageio.spec.generic.v0_3 import GenericDescr
from tests.utils import check_node

EXAMPLE_DOT_COM = "https://example.com/"
EXAMPLE_DOT_COM_FILE = "https://example.com/file"


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(
            authors=[{"name": "Me"}],
            cite=[dict(text="lala", url=EXAMPLE_DOT_COM)],
            description="the description",
            format_version=GenericDescr.implemented_format_version,
            license="BSD-2-Clause-FreeBSD",
            name="my name",
            type="my_type",
            unknown_extra_field="present",
            version="1.0",
        ),
        dict(
            attachments={"files": [EXAMPLE_DOT_COM_FILE], "something": 42},
            authors=[{"name": "Me"}],
            cite=[dict(text="lala", url=EXAMPLE_DOT_COM)],
            description="my description",
            format_version=GenericDescr.implemented_format_version,
            license="BSD-2-Clause-FreeBSD",
            name="your name",
            type="my_type",
            version="0.1.0",
        ),
    ],
)
def test_generic_valid(kwargs: Dict[str, Any]):
    check_node(GenericDescr, kwargs, context=ValidationContext(perform_io_checks=False))


@pytest.mark.parametrize(
    "kwargs,context",
    [
        pytest.param(
            dict(
                format_version=GenericDescr.implemented_format_version,
                name="my name",
                description="my description",
                authors=[{"name": "Me"}],
                type="my_type",
                version="1.0",
                license="BSD-2-Clause-FreeBSD",
                cite=[dict(text="lala", url=EXAMPLE_DOT_COM)],
            ),
            ValidationContext(warning_level=WARNING, perform_io_checks=False),
            id="deprecated license",
        ),
        (
            dict(
                format_version=GenericDescr.implemented_format_version,
                version="0.1.0",
                type="my_type",
                name="their name",
            ),
            ValidationContext(perform_io_checks=False),
        ),
        (
            dict(
                format_version=GenericDescr.implemented_format_version,
                version="0.1.0",
                type="my_type",
                name="its name",
                attachments={"files": [Path(__file__), "missing"], "something": 42},
            ),
            ValidationContext(perform_io_checks=False),
        ),
    ],
)
def test_generic_invalid(kwargs: Dict[str, Any], context: ValidationContext):
    check_node(GenericDescr, kwargs, context=context, is_invalid=True)
