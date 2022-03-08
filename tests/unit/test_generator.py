"""
TODO
"""

import pytest
from cppython.plugins.test.pytest import GeneratorUnitTests
from pytest_mock import MockerFixture

from cppython_vcpkg.plugin import VcpkgPlugin


class TestCPPythonGenerator(GeneratorUnitTests):
    """
    The tests for the PDM interface
    """

    @pytest.fixture(name="generator")
    def fixture_generator(self) -> VcpkgPlugin:
        """
        Override of the plugin provided generator fixture.
        """

        return VcpkgPlugin()

    def test_install(self, generator: VcpkgPlugin, mocker: MockerFixture):
        """
        TODO
        """
