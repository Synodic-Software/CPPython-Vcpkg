"""Unit test the provider plugin
"""

import pytest
from pytest_cppython.plugin import ProviderUnitTests

from cppython_vcpkg.plugin import VcpkgData, VcpkgProvider


class TestCPPythonProvider(ProviderUnitTests[VcpkgProvider, VcpkgData]):
    """The tests for the vcpkg Provider"""

    @pytest.fixture(name="provider_data", scope="session")
    def fixture_provider_data(self) -> VcpkgData:
        """A required testing hook that allows ProviderData generation

        Returns:
            The constructed provider data
        """
        return VcpkgData()

    @pytest.fixture(name="provider_type", scope="session")
    def fixture_provider_type(self) -> type[VcpkgProvider]:
        """A required testing hook that allows type generation

        Returns:
            The type of the Provider
        """
        return VcpkgProvider
