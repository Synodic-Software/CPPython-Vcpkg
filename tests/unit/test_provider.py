"""Unit test the provider plugin
"""

from typing import Any

import pytest
from pytest_cppython.plugin import ProviderUnitTests

from cppython_vcpkg.plugin import VcpkgProvider


class TestCPPythonProvider(ProviderUnitTests[VcpkgProvider]):
    """The tests for the vcpkg Provider"""

    @pytest.fixture(name="plugin_data", scope="session")
    def fixture_plugin_data(self) -> dict[str, Any]:
        """A required testing hook that allows data generation

        Returns:
            The constructed plugin data
        """
        return {}

    @pytest.fixture(name="plugin_type", scope="session")
    def fixture_plugin_type(self) -> type[VcpkgProvider]:
        """A required testing hook that allows type generation

        Returns:
            The type of the Provider
        """
        return VcpkgProvider
