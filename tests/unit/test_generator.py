"""
TODO
"""
from typing import Type

import pytest
from pytest_cppython.plugin import ProviderUnitTests

from cppython_vcpkg.plugin import VcpkgData, VcpkgProvider


class TestCPPythonProvider(ProviderUnitTests[VcpkgProvider, VcpkgData]):
    """
    The tests for the PDM interface
    """

    @pytest.fixture(name="provider_data", scope="session")
    def fixture_provider_data(self) -> VcpkgData:
        """
        A required testing hook that allows ProviderData generation
        """
        return VcpkgData()

    @pytest.fixture(name="provider_type", scope="session")
    def fixture_provider_type(self) -> Type[VcpkgProvider]:
        """
        A required testing hook that allows type generation
        """
        return VcpkgProvider
