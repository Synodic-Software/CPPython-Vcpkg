"""Builder to help build vcpkg state"""

from typing import Any

from cppython_core.schema import CorePluginData

from cppython_vcpkg.schema import (
    Manifest,
    VcpkgConfiguration,
    VcpkgData,
    VcpkgDependency,
)


def generate_manifest(core_data: CorePluginData) -> Manifest:
    """From the input configuration data, construct a Vcpkg specific Manifest type

    Args:
        core_data: The core data to help with the resolve

    Returns:
        The manifest
    """
    base_dependencies = core_data.cppython_data.dependencies

    vcpkg_dependencies: list[VcpkgDependency] = []
    for dependency in base_dependencies:
        vcpkg_dependency = VcpkgDependency(name=dependency.name)
        vcpkg_dependencies.append(vcpkg_dependency)

    return Manifest(
        name=core_data.pep621_data.name,
        version=core_data.pep621_data.version,
        dependencies=vcpkg_dependencies,
    )


def resolve_vcpkg_data(data: dict[str, Any], core_data: CorePluginData) -> VcpkgData:
    """Resolves the input data table from defaults to requirements

    Args:
        data: The input table
        core_data: The core data to help with the resolve

    Returns:
        The resolved data
    """

    parsed_data = VcpkgConfiguration(**data)

    root_directory = core_data.project_data.pyproject_file.parent.absolute()

    modified_install_path = parsed_data.install_path
    modified_manifest_path = parsed_data.manifest_path

    # Add the project location to all relative paths
    if not modified_install_path.is_absolute():
        modified_install_path = root_directory / modified_install_path

    if not modified_manifest_path.is_absolute():
        modified_manifest_path = root_directory / modified_manifest_path

    # Create directories
    modified_install_path.mkdir(parents=True, exist_ok=True)
    modified_manifest_path.mkdir(parents=True, exist_ok=True)

    return VcpkgData(install_path=modified_install_path, manifest_path=modified_manifest_path)
