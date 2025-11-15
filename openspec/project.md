# Project Context

## Purpose
`data-lagoon` is a Python library intended as a small, typed core for data-related utilities.  
Owner: please refine this to describe the concrete domain and primary use cases for this project (e.g., data ingestion, transformation, validation, orchestration).

## Tech Stack
- Python 3.13+ (`requires-python = ">=3.13"` in `pyproject.toml`)
- Single package library: `src/data_lagoon`
- Build backend: `uv_build` (PEP 517-compatible backend used by the `uv` toolchain)
- Packaging metadata: PEP 621 `pyproject.toml`
- Type-hinted code with `py.typed` published for type checkers

## Project Conventions

### Code Style
- Prefer explicit, modern type hints everywhere (library is typed and ships `py.typed`).
- Use standard Python naming conventions:
  - Modules and packages: `snake_case`
  - Classes: `PascalCase`
  - Functions, methods, variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
- Keep public API small and intentional; re-export only well-supported symbols from `data_lagoon.__init__`.
- Aim for side-effect-free imports (importing `data_lagoon` should not perform I/O or network calls).
- When a formatter/linter is configured, follow its output (e.g., `black`-style formatting and `ruff`-style linting are good defaults even if not yet enforced by tooling).

### Architecture Patterns
- Library-first design: this repo is a reusable Python package, not an application.
- Keep modules small and focused; prefer composition over inheritance.
- Isolate external I/O, networking, or environment access into dedicated modules so core logic can stay pure and testable.
- Separate:
  - Core domain logic (pure functions/classes)
  - Integration/adapters (working with files, CLIs, services)
- Favor clear, explicit data structures over "magical" helpers; make behavior obvious from function signatures.

### Testing Strategy
- Tests live under `tests/` and use `pytest` by default.
- Name test files `test_*.py` and test functions `test_*` for auto-discovery.
- Prefer fast, deterministic unit tests over slow integration tests.
- For new features or bug fixes, add or update tests that describe the intended behavior.
- Use type checkers (e.g., `mypy` or `pyright`) on the public API surface where possible; treat type errors as issues to fix, not ignore.

### Git Workflow
- Default branch is `main` (assume this unless the repo indicates otherwise).
- Use short-lived feature branches for work:
  - `feature/<short-description>` for new capabilities
  - `fix/<short-description>` for bug fixes
- Keep commits small and focused; write imperative, descriptive messages (e.g., `Add basic dataset loader`).
- Open pull requests even for solo work to document intent and enable review.

## Domain Context
Owner: please describe the domain focus of `data-lagoon` so assistants understand what "data" means here.  
Examples of helpful details:
- Types of data you expect to handle (e.g., tabular, time-series, logs, events).
- Typical data sources/targets (files, warehouses, APIs, streams).
- Any important domain terms or concepts that appear in code and specs.

## Important Constraints
- Runtime must support Python 3.13+.
- Keep the library dependency-light; prefer the standard library when reasonable.
- Public APIs should be stable once released; breaking changes should go through an OpenSpec change proposal.
- Avoid hidden global state; functions and classes should be safe to use in multi-threaded and async-aware contexts where possible.
- Owner: add any business, performance, or regulatory constraints that matter (e.g., privacy requirements, latency budgets, data residency).

## External Dependencies
- Runtime Python dependencies: currently none (empty `dependencies` list in `pyproject.toml`).
- Build-time tooling: `uv_build` via `pyproject.toml`.
- Owner: list any external services, APIs, data stores, or infrastructure this library is expected to integrate with, even if not yet implemented (e.g., S3, Postgres, Snowflake, Kafka).
