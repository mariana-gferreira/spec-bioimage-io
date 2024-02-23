from typing import Literal, Optional

from bioimageio.spec._internal.base_nodes import Node
from bioimageio.spec._internal.types import NotebookId as NotebookId
from bioimageio.spec.generic.v0_3 import AbsoluteFilePath as AbsoluteFilePath
from bioimageio.spec.generic.v0_3 import Author as Author
from bioimageio.spec.generic.v0_3 import BadgeDescr as BadgeDescr
from bioimageio.spec.generic.v0_3 import CiteEntry as CiteEntry
from bioimageio.spec.generic.v0_3 import Doi as Doi
from bioimageio.spec.generic.v0_3 import FileDescr as FileDescr
from bioimageio.spec.generic.v0_3 import GenericDescrBase
from bioimageio.spec.generic.v0_3 import HttpUrl as HttpUrl
from bioimageio.spec.generic.v0_3 import LinkedResource as LinkedResource
from bioimageio.spec.generic.v0_3 import Maintainer as Maintainer
from bioimageio.spec.generic.v0_3 import OrcidId as OrcidId
from bioimageio.spec.generic.v0_3 import RelativeFilePath as RelativeFilePath
from bioimageio.spec.generic.v0_3 import ResourceId as ResourceId
from bioimageio.spec.generic.v0_3 import Sha256 as Sha256
from bioimageio.spec.generic.v0_3 import Uploader as Uploader
from bioimageio.spec.notebook.v0_2 import NotebookSource as NotebookSource


class NotebookDescr(GenericDescrBase, title="bioimage.io notebook specification"):
    """Bioimage.io description of a Jupyter notebook."""

    type: Literal["notebook"] = "notebook"

    id: Optional[NotebookId] = None
    """Model zoo (bioimage.io) wide, unique identifier (assigned by bioimage.io)"""

    source: NotebookSource
    """The Jupyter notebook"""


class LinkedNotebook(Node):
    """Reference to a bioimage.io notebook."""

    id: NotebookId
    """A valid notebook `id` from the bioimage.io collection."""

    version: int
    """notebook version"""
