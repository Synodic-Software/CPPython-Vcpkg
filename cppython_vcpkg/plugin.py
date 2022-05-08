"""
TODO
"""
import subprocess
from os import name as system_name
from pathlib import Path, PosixPath, WindowsPath
from typing import Type

from cppython_core.schema import (
    Generator,
    GeneratorConfiguration,
    GeneratorData,
    PyProject,
)


class VcpkgData(GeneratorData):
    """
    TODO
    """


class VcpkgGenerator(Generator):
    """
    _summary_

    Arguments:
        Generator {_type_} -- _description_
    """

    def __init__(self, configuration: GeneratorConfiguration, pyproject: PyProject) -> None:
        """
        TODO
        """
        super().__init__(configuration, pyproject)

    def _update_generator(self, path: Path):

        # TODO: Identify why Shell is needed and refactor
        try:
            # TODO: Pipe output to logger
            if system_name == "nt":
                subprocess.check_output([str(WindowsPath("bootstrap-vcpkg.bat"))], cwd=path, shell=True)
            elif system_name == "posix":
                subprocess.check_output(["sh", str(PosixPath("bootstrap-vcpkg.sh"))], cwd=path, shell=True)
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
            subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
                cwd=path,
            )

        except subprocess.CalledProcessError:
            return False

        return True

    def download_generator(self, path: Path) -> None:

        try:
            # TODO: Pipe output to logger
            subprocess.check_output(
                ["git", "clone", "--depth", "1", "https://github.com/microsoft/vcpkg", "."],
                cwd=path,
            )

        except subprocess.CalledProcessError:
            self.logger.error("Unable to clone the vcpkg repository", exc_info=True)
            raise

        self._update_generator(path)

    def update_generator(self, path: Path) -> None:
        try:
            # TODO: Pipe output to logger
            subprocess.check_output(["git", "fetch", "origin", "--depth", "1"], cwd=path)
            subprocess.check_output(["git", "pull"], cwd=path)
        except subprocess.CalledProcessError:
            self.logger.error("Unable to update the vcpkg repository", exc_info=True)
            raise

        self._update_generator(path)

    def install(self) -> Path:
        """
        TODO
        """
        tool_path = self.pyproject.tool.cppython.tool_path
        return tool_path / "scripts/buildsystems/vcpkg.cmake"

    def update(self) -> Path:
        """
        TODO
        """
        tool_path = self.pyproject.tool.cppython.tool_path
        return tool_path / "scripts/buildsystems/vcpkg.cmake"
