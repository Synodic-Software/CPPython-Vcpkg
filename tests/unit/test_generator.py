"""
TODO
"""

import pytest
from cppython.plugins.test.pytest import GeneratorUnitTests
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

        return VcpkgGenerator()

    def test_install(self, generator: VcpkgGenerator, mocker: MockerFixture):
        """
        TODO
        """
