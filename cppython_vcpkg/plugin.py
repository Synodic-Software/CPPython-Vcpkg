"""
TODO
"""
import subprocess
from os import name as system_name
from pathlib import Path, PosixPath, WindowsPath
from typing import Type

from cppython_core.schema import (
    PEP621,
    CPPythonData,
    Generator,
    GeneratorConfiguration,
    GeneratorData,
)
from cppython_core.utility import subprocess_call
from pydantic import Field


class VcpkgData(GeneratorData):
    """
    TODO
    """

    # TODO: Make relative to CPPython:install_path
    install_path: Path = Field(
        default="build", description="The referenced dependencies defined by the local vcpkg.json manifest file"
    )


class VcpkgGenerator(Generator):
    """
    _summary_

    Arguments:
        Generator {_type_} -- _description_
    """

    def __init__(self, configuration: GeneratorConfiguration, project: PEP621, cppython: CPPythonData) -> None:
        """
        TODO
        """
        super().__init__(configuration, project, cppython)

    def _update_generator(self, path: Path):

        # TODO: Identify why Shell is needed and refactor
        try:
            if system_name == "nt":
                subprocess_call([str(WindowsPath("bootstrap-vcpkg.bat"))], cwd=path, shell=True)
            elif system_name == "posix":
                subprocess_call(["sh", str(PosixPath("bootstrap-vcpkg.sh"))], cwd=path, shell=True)
        except subprocess.CalledProcessError:
            self.logger.error("Unable to bootstrap the vcpkg repository", exc_info=True)
            raise

    @staticmethod
    def name() -> str:
        return "vcpkg"

    @staticmethod
    def data_type() -> Type[GeneratorData]:
        return VcpkgData

    def generator_downloaded(self, path: Path) -> bool:

        try:
            # Hide output, given an error output is a logic conditional
            subprocess_call(
                ["git", "rev-parse", "--is-inside-work-tree"],
                suppress=True,
                cwd=path,
            )

        except subprocess.CalledProcessError:
            return False

        return True

    def download_generator(self, path: Path) -> None:

        try:
            # The entire history is need for vcpkg 'baseline' information
            subprocess_call(
                ["git", "clone", "https://github.com/microsoft/vcpkg", "."],
                cwd=path,
            )

        except subprocess.CalledProcessError:
            self.logger.error("Unable to clone the vcpkg repository", exc_info=True)
            raise

        self._update_generator(path)

    def update_generator(self, path: Path) -> None:
        try:
            # The entire history is need for vcpkg 'baseline' information
            subprocess_call(["git", "fetch", "origin"], cwd=path)
            subprocess_call(["git", "pull"], cwd=path)
        except subprocess.CalledProcessError:
            self.logger.error("Unable to update the vcpkg repository", exc_info=True)
            raise

        self._update_generator(path)

    def install(self) -> Path:
        """
        TODO
        """
        vcpkg_path = self.cppython.install_path / self.name()

        executable = vcpkg_path / "vcpkg"

        try:
            subprocess_call(
                [executable, "install", f"--x-install-root={self.cppython.vcpkg.install_path}"],
                cwd=self.cppython.build_path,
            )
        except subprocess.CalledProcessError:
            self.logger.error("Unable to install project dependencies", exc_info=True)
            raise

        return vcpkg_path / "scripts/buildsystems/vcpkg.cmake"

    def update(self) -> Path:
        """
        TODO
        """
        vcpkg_path = self.cppython.install_path / self.name()

        executable = vcpkg_path / "vcpkg"

        try:
            subprocess_call(
                [executable, "install", f"--x-install-root={self.cppython.vcpkg.install_path}"],
                cwd=self.cppython.build_path,
            )
        except subprocess.CalledProcessError:
            self.logger.error("Unable to install project dependencies", exc_info=True)
            raise

        return vcpkg_path / "scripts/buildsystems/vcpkg.cmake"
