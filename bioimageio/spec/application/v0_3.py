from typing import Literal, Optional

from pydantic import Field
from typing_extensions import Annotated

from bioimageio.spec._internal.types import NonRdfFileSource
from bioimageio.spec.generic.v0_3 import Author as Author
from bioimageio.spec.generic.v0_3 import BadgeDescr as BadgeDescr
from bioimageio.spec.generic.v0_3 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_3 import Doi as Doi
from bioimageio.spec.generic.v0_3 import FileDescr as FileDescr
from bioimageio.spec.generic.v0_3 import GenericDescrBase
from bioimageio.spec.generic.v0_3 import HttpUrl as HttpUrl
from bioimageio.spec.generic.v0_3 import LinkedResourceDescr as LinkedResourceDescr
from bioimageio.spec.generic.v0_3 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_3 import ResourceId as ResourceId
from bioimageio.spec.generic.v0_3 import Sha256 as Sha256


class ApplicationDescr(GenericDescrBase, title="bioimage.io application specification"):
    """Bioimage.io description of an application."""

    type: Literal["application"] = "application"

    source: Annotated[
        Optional[NonRdfFileSource], Field(description="URL or path to the source of the application")
    ] = None
    """The primary source of the application"""
