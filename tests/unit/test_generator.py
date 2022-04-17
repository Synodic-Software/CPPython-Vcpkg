"""
TODO
"""
import logging

import pytest
from cppython.data import default_pyproject
from cppython_core.schema import GeneratorConfiguration
from pytest_cppython.plugin import GeneratorUnitTests
from pytest_mock import MockerFixture

from cppython_vcpkg.plugin import VcpkgGenerator


class TestCPPythonGenerator(GeneratorUnitTests):
    """
    The tests for the PDM interface
    """

    @pytest.fixture(name="generator")
    def fixture_generator(self) -> VcpkgGenerator:
        """
        Override of the plugin provided generator fixture.
        """
        configuration = GeneratorConfiguration(logging.getLogger(__name__))
        return VcpkgGenerator(configuration, default_pyproject)

    def test_install(self, generator: VcpkgGenerator, mocker: MockerFixture):
        """
        TODO
        """
