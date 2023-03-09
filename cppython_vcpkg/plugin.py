"""The vcpkg provider implementation
"""

import json
from os import name as system_name
from pathlib import Path, PosixPath, WindowsPath
from typing import Any

from cppython_core.exceptions import NotSupportedError, ProcessError
from cppython_core.plugin_schema.provider import Provider, ProviderData
from cppython_core.schema import CorePluginData, SyncData
from cppython_core.utility import subprocess_call

from cppython_vcpkg.resolution import generate_manifest, resolve_vcpkg_data


class VcpkgProvider(Provider):
    """vcpkg Provider"""

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

    def configure(self, group_data: ProviderData, core_data: CorePluginData) -> None:
        """Called when plugin data is ready

        Args:
            data: The input data table
        """

        self.group_data = group_data
        self.core_data = core_data

    def activate(self, configuration_data: dict[str, Any]) -> None:
        """Called when plugin data is ready

        Args:
            configuration_data: The input data table
        """

        self.data = resolve_vcpkg_data(configuration_data, self.core_data)

    def sync_data(self, generator_name: str) -> SyncData:
        """Gathers a data object for the given generator

        Args:
            generator_name: The input generator token

        Raises:
            NotSupportedError: If not supported

        Returns:
            The synch data object
        """

        if generator_name != "cmake":
            raise NotSupportedError(f"The generator '{generator_name}' is not supported by the 'vcpkg' plugin")

        toolchain_file = self.core_data.cppython_data.install_path / "scripts/buildsystems/vcpkg.cmake"

        return SyncData(provider_name="vcpkg")

    @classmethod
    def tooling_downloaded(cls, path: Path) -> bool:
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
    async def download_tooling(cls, path: Path) -> None:
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
        manifest = generate_manifest(self.core_data)

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
        manifest = generate_manifest(self.core_data)

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
