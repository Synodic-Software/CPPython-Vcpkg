"""
TODO
"""
import logging

import pytest
from cppython.data import default_pyproject
from cppython_core.schema import GeneratorConfiguration
from pytest_cppython.plugin import GeneratorIntegrationTests

from cppython_vcpkg.plugin import VcpkgGenerator


class TestCPPythonGenerator(GeneratorIntegrationTests):
    """
    The tests for the PDM generator
    """

    @pytest.fixture(name="generator")
    def fixture_generator(self) -> VcpkgGenerator:
        """
        Override of the plugin provided generator fixture.
        """
        configuration = GeneratorConfiguration(logging.getLogger(__name__))
        return VcpkgGenerator(configuration, default_pyproject)
