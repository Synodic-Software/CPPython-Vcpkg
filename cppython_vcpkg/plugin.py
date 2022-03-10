"""
TODO
"""
from os import scandir
from pathlib import Path
from typing import Type

from cppython.schema import Generator, GeneratorData, PyProject
from git import Git, Repo
from pydantic.fields import Field


def _default_install_location() -> Path:
    """
    TODO
    """
    return Path()


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

    @staticmethod
    def name() -> str:
        return "vcpkg"

    @staticmethod
    def data_type() -> Type[GeneratorData]:
        return VcpkgData

    def generator_downloaded(self) -> bool:
        repository = Repo(self.data.install_path)
        return not repository.bare

    def download_generator(self) -> None:

        repository = Repo(self.data.install_path)

        # Shallow clone
        repository.clone("https://github.com/microsoft/vcpkg", filter=["tree:0", "blob:none"], sparse=True)

    def update_generator(self) -> None:
        repository = Repo(self.data.install_path)

        remote = repository.remotes["origin"]
        remote.pull()

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
