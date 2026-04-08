"""Tests for the public cloud storage client contract."""

from __future__ import annotations

from datetime import UTC
from datetime import datetime
from dataclasses import fields
from dataclasses import FrozenInstanceError
import importlib
from importlib import resources
import inspect
from typing import BinaryIO
from typing import get_type_hints

import cloud_storage_api
import pytest
from cloud_storage_api import AuthenticationError
from cloud_storage_api import CloudStorageClient
from cloud_storage_api import ContainerNotFoundError
from cloud_storage_api import DeleteResult
from cloud_storage_api import InvalidContainerError
from cloud_storage_api import InvalidFileObjectError
from cloud_storage_api import InvalidObjectNameError
from cloud_storage_api import LocalFileAccessError
from cloud_storage_api import ObjectInfo
from cloud_storage_api import ObjectNotFoundError
from cloud_storage_api import StorageBackendError


class StubClient(CloudStorageClient):
    """Minimal concrete client used to exercise the abstract contract."""

    def upload_file(
        self,
        container: str,
        local_path: str,
        remote_path: str,
    ) -> ObjectInfo:
        return ObjectInfo(object_name=remote_path, data_type="application/octet-stream")

    def upload_obj(
        self,
        container: str,
        file_obj: BinaryIO,
        remote_path: str,
    ) -> ObjectInfo:
        return ObjectInfo(object_name=remote_path, data_type="application/octet-stream")

    def download_file(
        self,
        container: str,
        object_name: str,
        file_name: str,
    ) -> ObjectInfo:
        return ObjectInfo(object_name=object_name, integrity="etag-123")

    def list_files(self, container: str, prefix: str) -> list[ObjectInfo]:
        return [ObjectInfo(object_name=f"{prefix}report.csv", storage_tier="standard")]

    def delete_file(self, container: str, object_name: str) -> DeleteResult:
        return {
            "deleted": True,
            "version_id": "v1",
            "request_charged": False,
        }

    def get_file_info(self, container: str, object_name: str) -> ObjectInfo:
        return ObjectInfo(
            object_name=object_name,
            version_id="v1",
            encryption="AES256",
            size_bytes=128,
            updated_at=datetime(2026, 4, 8, tzinfo=UTC),
            metadata={"source": "stub"},
        )


def test_public_types_are_importable() -> None:
    """The package should export the public contract and result models."""

    object_info = ObjectInfo(object_name="reports/daily.csv")

    assert issubclass(StubClient, CloudStorageClient)
    assert object_info.object_name == "reports/daily.csv"
    assert object_info.version_id is None
    assert cloud_storage_api.__all__ == [
        "AuthenticationError",
        "CloudStorageClient",
        "ContainerNotFoundError",
        "DeleteResult",
        "InvalidContainerError",
        "InvalidFileObjectError",
        "InvalidObjectNameError",
        "LocalFileAccessError",
        "ObjectInfo",
        "ObjectNotFoundError",
        "StorageBackendError",
    ]


def test_package_has_no_factory_module() -> None:
    """The shared package should not expose dependency-injection helpers."""

    try:
        importlib.import_module("cloud_storage_api.factory")
    except ModuleNotFoundError:
        pass
    else:  # pragma: no cover
        msg = "cloud_storage_api.factory should not exist"
        raise AssertionError(msg)


def test_public_exception_exports_match_expected_contract() -> None:
    """The package should export only the requested typed domain exceptions."""

    expected_exception_names = {
        "AuthenticationError",
        "ContainerNotFoundError",
        "InvalidContainerError",
        "InvalidObjectNameError",
        "InvalidFileObjectError",
        "LocalFileAccessError",
        "ObjectNotFoundError",
        "StorageBackendError",
    }

    exported_exception_names = {
        name for name in cloud_storage_api.__all__ if name.endswith("Error")
    }

    assert exported_exception_names == expected_exception_names
    assert issubclass(AuthenticationError, PermissionError)
    assert issubclass(ContainerNotFoundError, FileNotFoundError)
    assert issubclass(InvalidContainerError, ValueError)
    assert issubclass(InvalidObjectNameError, ValueError)
    assert issubclass(InvalidFileObjectError, ValueError)
    assert issubclass(LocalFileAccessError, OSError)
    assert issubclass(ObjectNotFoundError, FileNotFoundError)
    assert issubclass(StorageBackendError, Exception)


def test_object_info_contract_is_frozen_and_explicit() -> None:
    """ObjectInfo should be a small immutable public metadata model."""

    object_info = ObjectInfo(
        object_name="reports/report.csv",
        version_id="v1",
        data_type="text/csv",
        integrity="etag-123",
        encryption="AES256",
        storage_tier="standard",
        size_bytes=512,
        updated_at=datetime(2026, 4, 8, tzinfo=UTC),
        metadata={"source": "reports"},
    )

    assert [field.name for field in fields(ObjectInfo)] == [
        "object_name",
        "version_id",
        "data_type",
        "integrity",
        "encryption",
        "storage_tier",
        "size_bytes",
        "updated_at",
        "metadata",
    ]
    assert object_info.version_id == "v1"
    assert object_info.size_bytes == 512
    assert object_info.updated_at == datetime(2026, 4, 8, tzinfo=UTC)
    assert object_info.metadata == {"source": "reports"}

    with pytest.raises(FrozenInstanceError):
        setattr(object_info, "object_name", "reports/other.csv")


def test_delete_result_contract_includes_normalized_keys() -> None:
    """DeleteResult should provide a provider-neutral contract surface."""

    assert DeleteResult.__required_keys__ == {
        "deleted",
        "version_id",
        "request_charged",
    }
    assert DeleteResult.__optional_keys__ == frozenset()

    delete_result: DeleteResult = {
        "deleted": True,
        "version_id": "v1",
        "request_charged": False,
    }

    assert delete_result["deleted"] is True
    assert delete_result["version_id"] == "v1"
    assert delete_result["request_charged"] is False


def test_typed_package_marker_is_present() -> None:
    """The package should advertise that it ships inline type information."""

    assert resources.files("cloud_storage_api").joinpath("py.typed").is_file()


def test_method_signatures_match_the_public_contract() -> None:
    """The abstract interface should expose the agreed method shapes."""

    expected_parameters_by_method = {
        "upload_file": ("self", "container", "local_path", "remote_path"),
        "upload_obj": ("self", "container", "file_obj", "remote_path"),
        "download_file": ("self", "container", "object_name", "file_name"),
        "list_files": ("self", "container", "prefix"),
        "delete_file": ("self", "container", "object_name"),
        "get_file_info": ("self", "container", "object_name"),
    }

    for method_name, expected_parameters in expected_parameters_by_method.items():
        method = getattr(CloudStorageClient, method_name)
        signature = inspect.signature(method)

        assert tuple(signature.parameters) == expected_parameters
        assert all(
            parameter.default is inspect.Signature.empty
            for parameter in signature.parameters.values()
            if parameter.name != "self"
        )

    assert get_type_hints(CloudStorageClient.upload_file)["return"] is ObjectInfo
    assert get_type_hints(CloudStorageClient.upload_obj)["return"] is ObjectInfo
    assert get_type_hints(CloudStorageClient.download_file)["return"] is ObjectInfo
    assert get_type_hints(CloudStorageClient.list_files)["return"] == list[ObjectInfo]
    assert get_type_hints(CloudStorageClient.delete_file)["return"] is DeleteResult
    assert get_type_hints(CloudStorageClient.get_file_info)["return"] is ObjectInfo


def test_method_docstrings_include_container_and_auth_failures() -> None:
    """Operations should document distinct auth and container errors."""

    for method_name in (
        "upload_file",
        "upload_obj",
        "download_file",
        "list_files",
        "delete_file",
        "get_file_info",
    ):
        docstring = inspect.getdoc(getattr(CloudStorageClient, method_name))

        assert docstring is not None
        assert "AuthenticationError" in docstring
        assert "ContainerNotFoundError" in docstring


def test_list_files_contract_documents_deterministic_ordering() -> None:
    """The interface should commit to deterministic list ordering."""

    docstring = inspect.getdoc(CloudStorageClient.list_files)

    assert docstring is not None
    assert "sorted in ascending" in docstring
    assert "lexicographic order by ``object_name``" in docstring


def test_interface_does_not_expose_old_alias_methods() -> None:
    """The shared interface should only expose the agreed method names."""

    assert not hasattr(CloudStorageClient, "list")
    assert not hasattr(CloudStorageClient, "delete")
    assert not hasattr(CloudStorageClient, "head")
