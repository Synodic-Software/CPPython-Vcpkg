"""The vcpkg provider implementation
"""

import json
from os import name as system_name
from pathlib import Path, PosixPath, WindowsPath

from cppython_core.exceptions import ProcessError
from cppython_core.schema import (
    CPPythonDataResolved,
    CPPythonModel,
    PEP621Resolved,
    ProjectConfiguration,
    Provider,
    ProviderConfiguration,
    ProviderData,
    ProviderDataResolved,
)
from cppython_core.utility import subprocess_call
from pydantic import Field, HttpUrl
from pydantic.types import DirectoryPath


class VcpkgDataResolved(ProviderDataResolved):
    """Resolved vcpkg data"""

    install_path: DirectoryPath
    manifest_path: DirectoryPath


class VcpkgData(ProviderData[VcpkgDataResolved]):
    """vcpkg provider data"""

    install_path: Path = Field(
        default=Path("build"),
        alias="install-path",
        description="The referenced dependencies defined by the local vcpkg.json manifest file",
    )

    manifest_path: Path = Field(
        default=Path(), alias="manifest-path", description="The directory to store the manifest file, vcpkg.json"
    )

    def resolve(self, project_configuration: ProjectConfiguration) -> VcpkgDataResolved:
        """Creates a copy and resolves dynamic attributes

        Args:
            project_configuration: The configuration data used to help the resolution

        Returns:
            The resolved provider data type
        """

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
    """Vcpkg dependency type"""

    name: str


class Manifest(CPPythonModel):
    """The manifest schema"""

    name: str

    version: str
    homepage: HttpUrl | None = Field(default=None)
    dependencies: list[VcpkgDependency] = Field(default=[])


class VcpkgProvider(Provider[VcpkgData, VcpkgDataResolved]):
    """vcpkg Provider"""

    def __init__(
        self,
        configuration: ProviderConfiguration,
        project: PEP621Resolved,
        cppython: CPPythonDataResolved,
        provider: VcpkgDataResolved,
    ) -> None:
        super().__init__(configuration, project, cppython, provider)

    @classmethod
    def _update_provider(cls, path: Path) -> None:
        """Calls the vcpkg tool install script

        Args:
            path: The path where the script is located
        """

        try:
            if system_name == "nt":
                subprocess_call([str(WindowsPath("bootstrap-vcpkg.bat"))], logger=cls.logger(), cwd=path, shell=True)
            elif system_name == "posix":
                subprocess_call(
                    ["./" + str(PosixPath("bootstrap-vcpkg.sh"))], logger=cls.logger(), cwd=path, shell=True
                )
        except ProcessError:
            cls.logger().error("Unable to bootstrap the vcpkg repository", exc_info=True)
            raise

    def _extract_manifest(self) -> Manifest:
        """From the input configuration data, construct a Vcpkg specific Manifest type

        Returns:
            The manifest
        """
        base_dependencies = self.cppython.dependencies

        vcpkg_dependencies: list[VcpkgDependency] = []
        for dependency in base_dependencies:
            vcpkg_dependency = VcpkgDependency(name=dependency.name)
            vcpkg_dependencies.append(vcpkg_dependency)

        # Create the manifest

        # Version is known to not be None, and has been filled
        version = self.project.version
        assert version is not None

        return Manifest(name=self.project.name, version=version, dependencies=vcpkg_dependencies)

    @staticmethod
    def name() -> str:
        """The string that is matched with the [tool.cppython.provider] string

        Returns:
            Plugin name
        """
        return "vcpkg"

    @staticmethod
    def data_type() -> type[VcpkgData]:
        """Returns the pydantic type to cast the provider configuration data to

        Returns:
            Plugin data type
        """
        return VcpkgData

    @staticmethod
    def resolved_data_type() -> type[VcpkgDataResolved]:
        """Returns the pydantic type to cast the resolved provider configuration data to

        Returns:
            Plugin resolved data type
        """
        return VcpkgDataResolved

    @classmethod
    def tooling_downloaded(cls, path: DirectoryPath) -> bool:
        """Returns whether the provider tooling needs to be downloaded

        Args:
            path: The directory to check for downloaded tooling

        Raises:
            ProcessError: Failed vcpkg calls

        Returns:
            Whether the tooling has been downloaded or not
        """

        try:
            # Hide output, given an error output is a logic conditional
            subprocess_call(
                ["git", "rev-parse", "--is-inside-work-tree"],
                logger=cls.logger(),
                suppress=True,
                cwd=path,
            )

        except ProcessError:
            return False

        return True

    @classmethod
    async def download_tooling(cls, path: DirectoryPath) -> None:
        """Installs the external tooling required by the provider

        Args:
            path: The directory to download any extra tooling to

        Raises:
            ProcessError: Failed vcpkg calls
        """
        logger = cls.logger()

        if cls.tooling_downloaded(path):
            try:
                # The entire history is need for vcpkg 'baseline' information
                subprocess_call(["git", "fetch", "origin"], logger=logger, cwd=path)
                subprocess_call(["git", "pull"], logger=logger, cwd=path)
            except ProcessError:
                logger.error("Unable to update the vcpkg repository", exc_info=True)
                raise
        else:
            try:
                # The entire history is need for vcpkg 'baseline' information
                subprocess_call(
                    ["git", "clone", "https://github.com/microsoft/vcpkg", "."],
                    logger=logger,
                    cwd=path,
                )

            except ProcessError:
                logger.error("Unable to clone the vcpkg repository", exc_info=True)
                raise

        cls._update_provider(path)

    def install(self) -> None:
        """Called when dependencies need to be installed from a lock file.

        Raises:
            ProcessError: Failed vcpkg calls
        """
        manifest_path = self.provider.manifest_path
        manifest = self._extract_manifest()

        # Write out the manifest
        serialized = json.loads(manifest.json(exclude_none=True))
        with open(manifest_path / "vcpkg.json", "w", encoding="utf8") as file:
            json.dump(serialized, file, ensure_ascii=False, indent=4)

        executable = self.cppython.install_path / "vcpkg"
        logger = self.logger()
        try:
            subprocess_call(
                [
                    executable,
                    "install",
                    f"--x-install-root={self.provider.install_path}",
                    f"--x-manifest-root={self.provider.manifest_path}",
                ],
                logger=logger,
                cwd=self.cppython.build_path,
            )
        except ProcessError:
            logger.error("Unable to install project dependencies", exc_info=True)
            raise

    def update(self) -> None:
        """Called when dependencies need to be updated and written to the lock file.

        Raises:
            ProcessError: Failed vcpkg calls
        """
        manifest_path = self.provider.manifest_path
        manifest = self._extract_manifest()

        # Write out the manifest
        serialized = json.loads(manifest.json(exclude_none=True))
        with open(manifest_path / "vcpkg.json", "w", encoding="utf8") as file:
            json.dump(serialized, file, ensure_ascii=False, indent=4)

        executable = self.cppython.install_path / "vcpkg"
        logger = self.logger()
        try:
            subprocess_call(
                [
                    executable,
                    "install",
                    f"--x-install-root={self.provider.install_path}",
                    f"--x-manifest-root={self.provider.manifest_path}",
                ],
                logger=logger,
                cwd=self.cppython.build_path,
            )
        except ProcessError:
            logger.error("Unable to install project dependencies", exc_info=True)
            raise
