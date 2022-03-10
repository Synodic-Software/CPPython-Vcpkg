"""
TODO
"""
from os import scandir
from pathlib import Path
from typing import Type

from cppython.schema import Generator, GeneratorData, PyProject
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

    @staticmethod
    def name() -> str:
        return "vcpkg"

    @staticmethod
    def data_type() -> Type[GeneratorData]:
        return VcpkgData

    def generator_downloaded(self) -> bool:
        """
        TODO
        """
        value = False
        try:
            if any(scandir(self.data.install_path)):
                value = True
        except NotADirectoryError:
            pass
        except FileNotFoundError:
            pass
        return value

    def download_generator(self) -> None:
        """
        TODO
        """

    def update_generator(self) -> None:
        """
        TODO
        """

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
