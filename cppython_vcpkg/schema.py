"""Definitions for the plugin"""
from pathlib import Path

from cppython_core.schema import CPPythonModel
from pydantic import Field, HttpUrl, validator
from pydantic.types import DirectoryPath, FilePath


class VcpkgData(CPPythonModel):
    """Resolved vcpkg data"""

    install_path: DirectoryPath
    manifest_path: DirectoryPath
    settings_files: list[FilePath]


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

    settings_files: list[FilePath] = Field(
        default=["CMakeSettings.json"],
        alias="settings-files",
        description="List of CMakeSettings files that will be injected with the CPPython toolchain",
    )

    @validator("injection")
    @classmethod
    def validate_injection_name(cls, value: Path) -> Path:
        """Validates the path naming scheme

        Args:
            value: The input path

        Raises:
            ValueError: If the naming doesn't conform

        Returns:
            The output path
        """

        if not value.name == "CMakeSettings.json":
            raise ValueError("The given files must be valid 'CMakeSettings.json' files")

        return value


class VcpkgDependency(CPPythonModel):
    """Vcpkg dependency type"""

    name: str


class Manifest(CPPythonModel):
    """The manifest schema"""

    name: str

    version: str
    homepage: HttpUrl | None = Field(default=None)
    dependencies: list[VcpkgDependency] = Field(default=[])
