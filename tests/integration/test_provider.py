"""Integration tests for the provider
"""

import pytest
from cppython_core.schema import PEP621, CPPythonData, PyProject, TargetEnum, ToolData
from pytest_cppython.plugin import ProviderIntegrationTests

from cppython_vcpkg.plugin import VcpkgData, VcpkgProvider

default_pep621 = PEP621(name="test_name", version="1.0")
default_cppython_data = CPPythonData(target=TargetEnum.EXE)
default_tool_data = ToolData(cppython=default_cppython_data)
default_pyproject = PyProject(project=default_pep621, tool=default_tool_data)
default_vcpkg_data = VcpkgData()


class TestCPPythonProvider(ProviderIntegrationTests[VcpkgProvider, VcpkgData]):
    """The tests for the vcpkg provider"""

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
