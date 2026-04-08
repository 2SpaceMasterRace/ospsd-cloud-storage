# cloud_storage_api

Provider-agnostic abstract contract, shared metadata types, and typed domain
exceptions for cloud storage.

## Role

This package defines the shared interface that implementations must honor.
It contains no provider SDKs, dependency-injection registry, service code, or
transport-specific types.

The distribution name and Python import path are both `cloud_storage_api`.

## API

```python
class CloudStorageClient(ABC):
    def upload_file(self, container: str, local_path: str, remote_path: str) -> ObjectInfo: ...
    def upload_obj(self, container: str, file_obj: BinaryIO, remote_path: str) -> ObjectInfo: ...
    def download_file(self, container: str, object_name: str, file_name: str) -> ObjectInfo: ...
    def list_files(self, container: str, prefix: str) -> list[ObjectInfo]: ...
    def delete_file(self, container: str, object_name: str) -> DeleteResult: ...
    def get_file_info(self, container: str, object_name: str) -> ObjectInfo: ...
```

| Method | Returns | Contract |
| --- | --- | --- |
| `upload_file(container, local_path, remote_path)` | `ObjectInfo` | Uploads a local file from disk. Raises `LocalFileAccessError` if the source path cannot be read. |
| `upload_obj(container, file_obj, remote_path)` | `ObjectInfo` | Uploads a binary file-like object. Raises `InvalidFileObjectError` for invalid file objects. |
| `download_file(container, object_name, file_name)` | `ObjectInfo` | Downloads an object to a local path. Raises `LocalFileAccessError` if the destination path cannot be written. |
| `list_files(container, prefix)` | `list[ObjectInfo]` | Lists objects for the prefix. Results must be sorted in ascending lexicographic order by `object_name`. Use `prefix=""` to list the whole container. |
| `delete_file(container, object_name)` | `DeleteResult` | Returns normalized provider-neutral delete metadata. |
| `get_file_info(container, object_name)` | `ObjectInfo` | Returns metadata for a single stored object without downloading its contents. |

**ObjectInfo**

| Field | Type | Meaning |
| --- | --- | --- |
| `object_name` | `str` | Provider object key or path. |
| `version_id` | `str \| None` | Provider object version identifier, when available. |
| `data_type` | `str \| None` | MIME type or provider-reported content type. |
| `integrity` | `str \| None` | Checksum, ETag, or similar integrity marker. |
| `encryption` | `str \| None` | Encryption mode or algorithm applied to the object. |
| `storage_tier` | `str \| None` | Storage class or access tier. |
| `size_bytes` | `int \| None` | Object size in bytes. |
| `updated_at` | `datetime \| None` | Last-modified timestamp. |
| `metadata` | `Mapping[str, str] \| None` | Provider object metadata normalized to string pairs. |

**DeleteResult**

| Field | Type | Meaning |
| --- | --- | --- |
| `deleted` | `bool` | Canonical provider-neutral delete outcome. |
| `version_id` | `str \| None` | Deleted object version identifier, when available. |
| `request_charged` | `bool \| None` | Whether a requester-pays charge was applied. |

**Exceptions**

| Exception | Meaning |
| --- | --- |
| `AuthenticationError` | The provider rejected credentials or denied storage access. |
| `ContainerNotFoundError` | The referenced container or bucket does not exist. |
| `InvalidContainerError` | The container or bucket name is invalid. |
| `InvalidObjectNameError` | The object key or path is invalid. |
| `InvalidFileObjectError` | A provided file object is not a valid binary readable object. |
| `LocalFileAccessError` | A local filesystem path cannot be read from or written to. |
| `ObjectNotFoundError` | The requested remote object does not exist. |
| `StorageBackendError` | The backing provider failed unexpectedly. |

## Dependencies

None. This package is intentionally framework-free and implementation-free.
It also ships `py.typed` so downstream type checkers can consume the package as
a typed dependency.

## Install

```shell
uv add "cloud_storage_api @ git+https://github.com/2SpaceMasterRace/ospsd-cloud-storage.git@v1.0.0"
```

This pins consumers to the stable `1.0.0` shared contract release.

## Usage

```python
from typing import BinaryIO

from cloud_storage_api import CloudStorageClient
from cloud_storage_api import DeleteResult
from cloud_storage_api import ObjectInfo


class ExampleStorageClient(CloudStorageClient):
    def upload_file(self, container: str, local_path: str, remote_path: str) -> ObjectInfo:
        raise NotImplementedError

    def upload_obj(self, container: str, file_obj: BinaryIO, remote_path: str) -> ObjectInfo:
        raise NotImplementedError

    def download_file(self, container: str, object_name: str, file_name: str) -> ObjectInfo:
        raise NotImplementedError

    def list_files(self, container: str, prefix: str) -> list[ObjectInfo]:
        raise NotImplementedError

    def delete_file(self, container: str, object_name: str) -> DeleteResult:
        raise NotImplementedError

    def get_file_info(self, container: str, object_name: str) -> ObjectInfo:
        raise NotImplementedError
```

Callers and implementations should depend on this package as the shared
contract.
