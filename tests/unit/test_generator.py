"""
TODO
"""
from typing import Type

import pytest
from pytest_cppython.plugin import GeneratorUnitTests

from cppython_vcpkg.plugin import VcpkgData, VcpkgGenerator


class TestCPPythonGenerator(GeneratorUnitTests[VcpkgGenerator, VcpkgData]):
    """
    The tests for the PDM interface
    """

    @pytest.fixture(name="generator_data")
    def fixture_generator_data(self) -> VcpkgData:
        """
        A required testing hook that allows GeneratorData generation
        """
        return VcpkgData()

    @pytest.fixture(name="generator_type")
    def fixture_generator_type(self) -> Type[VcpkgGenerator]:
        """
        A required testing hook that allows type generation
        """
        return VcpkgGenerator
