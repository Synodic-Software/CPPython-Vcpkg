"""The vcpkg provider implementation
"""

import json
from os import name as system_name
from pathlib import Path, PosixPath, WindowsPath
from typing import Any

from cppython_core.exceptions import ProcessError
from cppython_core.plugin_schema.provider import Provider, ProviderData
from cppython_core.schema import CorePluginData, CPPythonModel
from cppython_core.utility import subprocess_call
from pydantic import Field, HttpUrl
from pydantic.types import DirectoryPath


class VcpkgDataResolved(CPPythonModel):
    """Resolved vcpkg data"""

    install_path: DirectoryPath
    manifest_path: DirectoryPath


class VcpkgData(CPPythonModel):
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


class VcpkgProvider(Provider):
    """vcpkg Provider"""

    def __init__(self, group_data: ProviderData, core_data: CorePluginData) -> None:
        super().__init__(group_data, core_data)

        # Default the provider data
        self.data = self._resolve_data(VcpkgData())

    def _resolve_data(self, data: VcpkgData) -> VcpkgDataResolved:
        """_summary_

        Args:
            data: _description_

        Returns:
            _description_
        """

        root_directory = self.core_data.project_data.pyproject_file.parent.absolute()

        modified_install_path = data.install_path
        modified_manifest_path = data.manifest_path

        # Add the project location to all relative paths
        if not modified_install_path.is_absolute():
            modified_install_path = root_directory / modified_install_path

        if not modified_manifest_path.is_absolute():
            modified_manifest_path = root_directory / modified_manifest_path

        # Create directories
        modified_install_path.mkdir(parents=True, exist_ok=True)
        modified_manifest_path.mkdir(parents=True, exist_ok=True)

        return VcpkgDataResolved(install_path=modified_install_path, manifest_path=modified_manifest_path)

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
        base_dependencies = self.core_data.cppython_data.dependencies

        vcpkg_dependencies: list[VcpkgDependency] = []
        for dependency in base_dependencies:
            vcpkg_dependency = VcpkgDependency(name=dependency.name)
            vcpkg_dependencies.append(vcpkg_dependency)

        return Manifest(
            name=self.core_data.pep621_data.name,
            version=self.core_data.pep621_data.version,
            dependencies=vcpkg_dependencies,
        )

    @staticmethod
    def name() -> str:
        """The string that is matched with the [tool.cppython.provider] string

        Returns:
            Plugin name
        """
        return "vcpkg"

    def activate(self, data: dict[str, Any]) -> None:
        """_summary_

        Args:
            data: _description_
        """

        input_data = VcpkgData(**data)

        self.data = self._resolve_data(input_data)

    def supports_generator(self, name: str) -> bool:
        """_summary_

        Args:
            name: _description_

        Returns:
            _description_
        """

        if name == "cmake":
            return True

        return False

    def gather_input(self, name: str) -> Any:
        return None

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
        manifest_path = self.data.manifest_path
        manifest = self._extract_manifest()

        # Write out the manifest
        serialized = json.loads(manifest.json(exclude_none=True))
        with open(manifest_path / "vcpkg.json", "w", encoding="utf8") as file:
            json.dump(serialized, file, ensure_ascii=False, indent=4)

        executable = self.core_data.cppython_data.install_path / "vcpkg"
        logger = self.logger()
        try:
            subprocess_call(
                [
                    executable,
                    "install",
                    f"--x-install-root={self.data.install_path}",
                    f"--x-manifest-root={self.data.manifest_path}",
                ],
                logger=logger,
                cwd=self.core_data.cppython_data.build_path,
            )
        except ProcessError:
            logger.error("Unable to install project dependencies", exc_info=True)
            raise

    def update(self) -> None:
        """Called when dependencies need to be updated and written to the lock file.

        Raises:
            ProcessError: Failed vcpkg calls
        """
        manifest_path = self.data.manifest_path
        manifest = self._extract_manifest()

        # Write out the manifest
        serialized = json.loads(manifest.json(exclude_none=True))
        with open(manifest_path / "vcpkg.json", "w", encoding="utf8") as file:
            json.dump(serialized, file, ensure_ascii=False, indent=4)

        executable = self.core_data.cppython_data.install_path / "vcpkg"
        logger = self.logger()
        try:
            subprocess_call(
                [
                    executable,
                    "install",
                    f"--x-install-root={self.data.install_path}",
                    f"--x-manifest-root={self.data.manifest_path}",
                ],
                logger=logger,
                cwd=self.core_data.cppython_data.build_path,
            )
        except ProcessError:
            logger.error("Unable to install project dependencies", exc_info=True)
            raise
