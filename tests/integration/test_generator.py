"""
TODO
"""
import pytest
from cppython.plugins.test.pytest import GeneratorIntegrationTests

from cppython_vcpkg.plugin import VcpkgPlugin


class TestCPPythonGenerator(GeneratorIntegrationTests):
    """
    The tests for the PDM generator
    """

    @pytest.fixture(name="generator")
    def fixture_generator(self) -> VcpkgPlugin:
        """
        Override of the plugin provided generator fixture.
        """
        return VcpkgPlugin()
