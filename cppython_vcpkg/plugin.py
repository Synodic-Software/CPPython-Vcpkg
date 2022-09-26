"""
TODO
"""
import json
from os import name as system_name
from pathlib import Path, PosixPath, WindowsPath
from typing import Optional, Type

from cppython_core.exceptions import ProcessError
from cppython_core.schema import (
    ConfigurePreset,
    CPPythonDataResolved,
    CPPythonModel,
    Provider,
    ProviderConfiguration,
    ProviderData,
    ProviderDataResolved,
    PEP621Resolved,
    ProjectConfiguration,
)
from cppython_core.utility import subprocess_call
from pydantic import Field, HttpUrl
from pydantic.types import DirectoryPath


class VcpkgDataResolved(ProviderDataResolved):
    """
    TODO
    """

    install_path: DirectoryPath
    manifest_path: DirectoryPath


class VcpkgData(ProviderData[VcpkgDataResolved]):
    """
    TODO
    """

    # TODO: Make relative to CPPython:build_path
    install_path: Path = Field(
        default=Path("build"),
        alias="install-path",
        description="The referenced dependencies defined by the local vcpkg.json manifest file",
    )

    manifest_path: Path = Field(
        default=Path(), alias="manifest-path", description="The directory to store the manifest file, vcpkg.json"
    )

    def resolve(self, project_configuration: ProjectConfiguration) -> VcpkgDataResolved:
        modified = self.copy(deep=True)

        root_directory = project_configuration.pyproject_file.parent.absolute()

        # Add the project location to all relative paths
        if not modified.install_path.is_absolute():
            modified.install_path = root_directory / modified.install_path

        if not modified.manifest_path.is_absolute():
            modified.manifest_path = root_directory / modified.manifest_path

        # Create directories
        modified.install_path.mkdir(parents=True, exist_ok=True)
        modified.manifest_path.mkdir(parents=True, exist_ok=True)

        return VcpkgDataResolved(**modified.dict())


class VcpkgDependency(CPPythonModel):
    """
    Vcpkg dependency type
    """

    name: str


class Manifest(CPPythonModel):
    """
    The manifest schema
    """

    name: str

    # TODO: Support other version types
    version: str
    homepage: Optional[HttpUrl] = Field(default=None)
    dependencies: list[VcpkgDependency] = Field(default=[])


class VcpkgProvider(Provider[VcpkgData, VcpkgDataResolved]):
    """
    _summary_

    Arguments:
        Provider {_type_} -- _description_
    """

    def __init__(
        self,
        configuration: ProviderConfiguration,
        project: PEP621Resolved,
        cppython: CPPythonDataResolved,
        provider: VcpkgDataResolved,
    ) -> None:
        """
        Modify the vcpkg settings based on Provider configuration before passing it to the base
            provider
        """
        super().__init__(configuration, project, cppython, provider)

    @classmethod
    def _update_provider(cls, path: Path):
        # TODO: Identify why Shell is needed and refactor
        try:
            if system_name == "nt":
                subprocess_call([str(WindowsPath("bootstrap-vcpkg.bat"))], logger=cls.logger, cwd=path, shell=True)
            elif system_name == "posix":
                subprocess_call(["sh", str(PosixPath("bootstrap-vcpkg.sh"))], logger=cls.logger, cwd=path, shell=True)
        except ProcessError:
            cls.logger.error("Unable to bootstrap the vcpkg repository", exc_info=True)
            raise

    def _extract_manifest(self) -> Manifest:
        """
        TODO
        """
        base_dependencies = self.cppython.dependencies

        vcpkg_dependencies: list[VcpkgDependency] = []
        for dependency in base_dependencies:
            vcpkg_dependency = VcpkgDependency(name=dependency.name)
            vcpkg_dependencies.append(vcpkg_dependency)

        # Create the manifest

        # Version is known to not be None, and has been filled
        # TODO: Type for ResolvedProject
        version = self.project.version
        assert version is not None

        return Manifest(name=self.project.name, version=version, dependencies=vcpkg_dependencies)

    @staticmethod
    def name() -> str:
        return "vcpkg"

    @staticmethod
    def data_type() -> Type[VcpkgData]:
        return VcpkgData

    @staticmethod
    def resolved_data_type() -> Type[VcpkgDataResolved]:
        return VcpkgDataResolved

    @classmethod
    def provider_downloaded(cls, path: DirectoryPath) -> bool:
        try:
            # Hide output, given an error output is a logic conditional
            subprocess_call(
                ["git", "rev-parse", "--is-inside-work-tree"],
                logger=cls.logger,
                suppress=True,
                cwd=path,
            )

        except ProcessError:
            return False

        return True

    @classmethod
    def download_provider(cls, path: DirectoryPath) -> None:
        try:
            # The entire history is need for vcpkg 'baseline' information
            subprocess_call(
                ["git", "clone", "https://github.com/microsoft/vcpkg", "."],
                logger=cls.logger,
                cwd=path,
            )

        except ProcessError:
            cls.logger.error("Unable to clone the vcpkg repository", exc_info=True)
            raise

        cls._update_provider(path)

    @classmethod
    def update_provider(cls, path: DirectoryPath) -> None:
        try:
            # The entire history is need for vcpkg 'baseline' information
            subprocess_call(["git", "fetch", "origin"], logger=cls.logger, cwd=path)
            subprocess_call(["git", "pull"], logger=cls.logger, cwd=path)
        except ProcessError:
            cls.logger.error("Unable to update the vcpkg repository", exc_info=True)
            raise

        cls._update_provider(path)

    def install(self) -> None:
        """
        TODO
        """
        manifest_path = self.provider.manifest_path
        manifest = self._extract_manifest()

        # Write out the manifest
        serialized = json.loads(manifest.json(exclude_none=True))
        with open(manifest_path / "vcpkg.json", "w", encoding="utf8") as file:
            json.dump(serialized, file, ensure_ascii=False, indent=4)

        vcpkg_path = self.cppython.install_path / self.name()

        executable = vcpkg_path / "vcpkg"

        try:
            subprocess_call(
                [
                    executable,
                    "install",
                    f"--x-install-root={self.provider.install_path}",
                    f"--x-manifest-root={self.provider.manifest_path}",
                ],
                logger=self.logger,
                cwd=self.cppython.build_path,
            )
        except ProcessError:
            self.logger.error("Unable to install project dependencies", exc_info=True)
            raise

    def update(self) -> None:
        """
        TODO
        """
        manifest_path = self.provider.manifest_path
        manifest = self._extract_manifest()

        # Write out the manifest
        serialized = json.loads(manifest.json(exclude_none=True))
        with open(manifest_path / "vcpkg.json", "w", encoding="utf8") as file:
            json.dump(serialized, file, ensure_ascii=False, indent=4)

        vcpkg_path = self.cppython.install_path / self.name()

        executable = vcpkg_path / "vcpkg"

        try:
            subprocess_call(
                [
                    executable,
                    "install",
                    f"--x-install-root={self.provider.install_path}",
                    f"--x-manifest-root={self.provider.manifest_path}",
                ],
                logger=self.logger,
                cwd=self.cppython.build_path,
            )
        except ProcessError:
            self.logger.error("Unable to install project dependencies", exc_info=True)
            raise

    def generate_cmake_config(self) -> ConfigurePreset:
        toolchain_file = self.cppython.install_path / self.name() / "scripts/buildsystems/vcpkg.cmake"

        configure_preset = ConfigurePreset(name=self.name(), toolchainFile=str(toolchain_file))

        return configure_preset
