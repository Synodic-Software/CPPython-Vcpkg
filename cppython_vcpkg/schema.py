"""Definitions for the plugin"""
from pathlib import Path

from cppython_core.schema import CPPythonModel, SyncData
from pydantic import Field, FilePath, HttpUrl
from pydantic.types import DirectoryPath


class VcpkgSyncData(SyncData):
    """Vcpkg sync type"""

    toolchain: FilePath


class VcpkgDependency(CPPythonModel):
    """Vcpkg dependency type"""

    name: str


class VcpkgData(CPPythonModel):
    """Resolved vcpkg data"""

    install_directory: DirectoryPath
    manifest_directory: DirectoryPath
    dependencies: list[VcpkgDependency]


class VcpkgConfiguration(CPPythonModel):
    """vcpkg provider data"""

    install_directory: Path = Field(
        default=Path("build"),
        alias="install-directory",
        description="The referenced dependencies defined by the local vcpkg.json manifest file",
    )

    manifest_directory: Path = Field(
        default=Path(), alias="manifest-directory", description="The directory to store the manifest file, vcpkg.json"
    )

    dependencies: list[VcpkgDependency] = Field(
        default=[], description="The directory to store the manifest file, vcpkg.json"
    )


class Manifest(CPPythonModel):
    """The manifest schema"""

    name: str

    version: str
    homepage: HttpUrl | None = Field(default=None)
    dependencies: list[VcpkgDependency] = Field(default=[])
