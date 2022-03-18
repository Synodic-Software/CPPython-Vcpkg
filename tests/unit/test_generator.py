"""
TODO
"""

import pytest
from cppython.data import default_pyproject
from pytest_cppython.plugin import GeneratorUnitTests
from pytest_mock import MockerFixture

from cppython_vcpkg.plugin import VcpkgData, VcpkgGenerator


class TestCPPythonGenerator(GeneratorUnitTests):
    """
    The tests for the PDM interface
    """

    @pytest.fixture(name="generator")
    def fixture_generator(self) -> VcpkgGenerator:
        """
        Override of the plugin provided generator fixture.
        """

        vcpkg_data = VcpkgData()
        return VcpkgGenerator(default_pyproject, vcpkg_data)

    def test_install(self, generator: VcpkgGenerator, mocker: MockerFixture):
        """
        TODO
        """
