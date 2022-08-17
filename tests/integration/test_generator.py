"""
TODO
"""
from typing import Type

import pytest
from cppython_core.schema import PEP621, CPPythonData, PyProject, TargetEnum, ToolData
from pytest_cppython.plugin import GeneratorIntegrationTests

from cppython_vcpkg.plugin import VcpkgData, VcpkgGenerator

default_pep621 = PEP621(name="test_name", version="1.0")
default_cppython_data = CPPythonData(target=TargetEnum.EXE)
default_tool_data = ToolData(cppython=default_cppython_data)
default_pyproject = PyProject(project=default_pep621, tool=default_tool_data)
default_vcpkg_data = VcpkgData()


class TestCPPythonGenerator(GeneratorIntegrationTests[VcpkgGenerator, VcpkgData]):
    """
    The tests for the PDM generator
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
