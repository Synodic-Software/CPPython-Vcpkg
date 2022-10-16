"""Definitions for the plugin"""
from pathlib import Path

from cppython_core.schema import CPPythonModel
from pydantic import Field, HttpUrl
from pydantic.types import DirectoryPath


class VcpkgData(CPPythonModel):
    """Resolved vcpkg data"""

    install_path: DirectoryPath
    manifest_path: DirectoryPath


class VcpkgConfiguration(CPPythonModel):
    """vcpkg provider data"""

    install_path: Path = Field(
        default=Path("build"),
        alias="install-path",
        description="The referenced dependencies defined by the local vcpkg.json manifest file",
    )

    manifest_path: Path = Field(
        default=Path(), alias="manifest-path", description="The directory to store the manifest file, vcpkg.json"
    )


class VcpkgDependency(CPPythonModel):
    """Vcpkg dependency type"""

    name: str


class Manifest(CPPythonModel):
    """The manifest schema"""

    name: str

    version: str
    homepage: HttpUrl | None = Field(default=None)
    dependencies: list[VcpkgDependency] = Field(default=[])
