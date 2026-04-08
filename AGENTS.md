# Agent Development Guide

Repository-wide guidance for coding agents. Explicit user instructions override this file.

---

## Highest-Priority Rules

- Read the relevant code before editing. Do not guess from names alone.
- Prefer the smallest correct change that fits the existing design.
- Treat the public API as product surface. Update tests and docs when it changes.
- Run relevant verification before finishing.
- Do not add dependencies or public exceptions without asking first.
- Leave unrelated user changes alone.
- Keep `AGENTS.md` and `README.md` current when package layout, commands, or public behavior changes.

---

## Project Snapshot

This repository contains a single Python package: `cloud_storage_api`.

It provides:

- `CloudStorageClient`: the provider-agnostic abstract interface.
- `ObjectInfo`: shared metadata returned by object operations.
- `DeleteResult`: typed delete response metadata.
- Typed domain exceptions:
  - `AuthenticationError`
  - `ContainerNotFoundError`
  - `InvalidContainerError`
  - `InvalidObjectNameError`
  - `InvalidFileObjectError`
  - `LocalFileAccessError`
  - `ObjectNotFoundError`
  - `StorageBackendError`

This repo does not contain concrete storage backends, service code, generated clients, or transport adapters.

The distribution name and the Python import path are both `cloud_storage_api`.

---

## Repository Layout

- `cloud_storage_api/__init__.py`: public exports.
- `cloud_storage_api/client.py`: `CloudStorageClient` abstract contract.
- `cloud_storage_api/models.py`: public result types.
- `cloud_storage_api/exceptions.py`: typed domain exceptions.
- `tests/`: pytest-based contract tests.
- `pyproject.toml`: package metadata and build configuration.
- `README.md`: user-facing package overview and usage.
- `CHANGELOG.md`: release history for the shared contract.

---

## Default Workflow

1. Read the relevant package modules and tests.
2. Make the smallest change that satisfies the request.
3. Add or update tests when the public contract or packaging changes.
4. Run the relevant verification commands.
5. Summarize what changed, how it was verified, and any remaining risk.

---

## Public API Rules

- Preserve the `CloudStorageClient` method contract unless the user explicitly asks to change it.
- Keep the public export surface in `cloud_storage_api/__init__.py` intentional and minimal.
- Do not add extra public exceptions without asking first.
- Keep provider-specific SDK types and implementation details out of this package.
- If a public signature, return type, or exported symbol changes, update tests and `README.md` in the same change.

---

## Testing Expectations

All lasting tests belong in `tests/` and should use `pytest`.

- Prefer contract tests that assert public imports, signatures, return annotations, public model fields, and documented behavioral guarantees like deterministic ordering.
- Prefer testing through the public API rather than private implementation details.
- Keep tests deterministic and fast.
- Do not add throwaway scripts for verification.
- No Pact-based consumer contract testing is set up in this repo today. The current contract coverage is ordinary pytest-based interface testing.
- Ask before adding Pact or any other new test dependency.

Recommended commands from the repository root:

```shell
uvx ruff format cloud_storage_api tests
uvx ruff check --fix cloud_storage_api tests
uv run --with pytest python -m pytest tests
uv run python -c "import cloud_storage_api"
uv build
```

---

## Code Standards

- Write simple, explicit, predictable Python.
- Use docstrings for public classes and methods.
- Prefer `dataclass` and `TypedDict` for public data models when appropriate.
- Keep comments rare and focused on why.
- Avoid broad exception handling and silent fallbacks.
- Use descriptive names and explicit types.

---

## Packaging Notes

- This package is intended to be consumable as a normal dependency or a `uv` git dependency.
- Keep `pyproject.toml`, `uv.lock`, and the import path aligned on `cloud_storage_api`.
- Verify that builds succeed after changing package metadata or layout.

---

## Git and Change Safety

- Never commit secrets, credentials, or local environment files.
- Never use destructive git commands unless the user explicitly asks.
- Do not amend commits unless the user explicitly asks.
- Use non-interactive git commands.
- Leave unrelated user changes intact.
