"""
TODO
"""
import subprocess
from os import name as system_name
from pathlib import Path
from typing import Type

from cppython_core.schema import Generator, GeneratorData, PyProject
from pydantic.fields import Field


def _default_install_location() -> Path:

    # TODO: Find sane default per platform
    if system_name == "nt":
        return Path()

    if system_name == "posix":
        return Path()

    raise Exception


class VcpkgData(GeneratorData):
    """
    TODO
    """

    install_path: Path = Field(alias="install-path", default_factory=_default_install_location)


class VcpkgGenerator(Generator):
    """
    _summary_

    Arguments:
        Generator {_type_} -- _description_
    """

    def __init__(self, pyproject: PyProject, generator_data: VcpkgData) -> None:
        """
        TODO
        """
        self.data = generator_data

        super().__init__(pyproject, generator_data)

    def _update_generator(self):

        if system_name == "nt":
            subprocess.run([".\vcpkg\bootstrap-vcpkg.bat"], cwd=self.data.install_path, check=True)
        elif system_name == "posix":
            subprocess.run(["sh", "./vcpkg/bootstrap-vcpkg.sh"], cwd=self.data.install_path, check=True)

    @staticmethod
    def name() -> str:
        return "vcpkg"

    @staticmethod
    def data_type() -> Type[GeneratorData]:
        return VcpkgData

    def generator_downloaded(self) -> bool:
        try:
            subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=self.data.install_path, check=True)

        except subprocess.CalledProcessError:
            return False

        return True

    def download_generator(self) -> None:
        subprocess.run(
            ["git", "clone", "-–depth", "1", "https://github.com/microsoft/vcpkg"],
            cwd=self.data.install_path,
            check=True,
        )
        self._update_generator()

    def update_generator(self) -> None:
        subprocess.run(["git", "fetch", "origin", "-–depth", "1"], cwd=self.data.install_path, check=True)
        subprocess.run(["git", "pull"], cwd=self.data.install_path, check=True)
        self._update_generator()

    def install(self) -> None:
        """
        TODO
        """

    def update(self) -> None:
        """
        TODO
        """

    def build(self) -> None:
        """
        TODO
        """
