# Changelog

All notable changes to `cloud_storage_api` are documented in this file.

## [1.0.0] - 2026-04-08

### Added
- `AuthenticationError` for provider credential and access failures.
- `ContainerNotFoundError` for a well-formed but nonexistent container.
- `LocalFileAccessError` for local read/write failures.
- `py.typed` marker for downstream type checkers.
- Stronger pytest contract coverage for public exports, model fields, typed
  package metadata, and documented guarantees.

### Changed
- Finalized the stable provider-agnostic `CloudStorageClient` contract.
- Simplified `DeleteResult` to only use provider-neutral keys:
  - `deleted`
  - `version_id`
  - `request_charged`
- Expanded `ObjectInfo` with practical metadata fields:
  - `size_bytes`
  - `updated_at`
  - `metadata`
- Documented deterministic ordering for `list_files()`.
- Documented auth and missing-container behavior across all interface methods.
- Improved `README.md` API docs and install instructions.

## [0.1.0] - 2026-04-08

### Added
- Initial shared cloud storage ABC package.
- Public `CloudStorageClient`, `ObjectInfo`, `DeleteResult`, and typed domain
  exceptions.
