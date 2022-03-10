"""
TODO
"""
import pytest
from cppython.plugins.test.data import default_pyproject
from cppython.plugins.test.pytest import GeneratorIntegrationTests

from cppython_vcpkg.plugin import VcpkgData, VcpkgGenerator


class TestCPPythonGenerator(GeneratorIntegrationTests):
    """
    The tests for the PDM generator
    """

    @pytest.fixture(name="generator")
    def fixture_generator(self) -> VcpkgGenerator:
        """
        Override of the plugin provided generator fixture.
        """
        vcpkg_data = VcpkgData()
        return VcpkgGenerator(default_pyproject, vcpkg_data)
