# AGENTS.md — Roles & Guardrails

## Roles
- **Product**: enforces scope (PRD), resolves ambiguity minimally.
- **Architect**: module boundaries, public API, naming/typing consistency.
- **Implementer**: production code in `src/lagoon/`; tests-first.
- **Tester**: pytest + respx; realistic fixtures.
- **Docs**: README + docstrings + examples.
- **Release**: version bumps, changelog, tags.

## Guardrails
- Source of truth: `PRD.md`.
- Public API stability; full type hints (py310+); ruff + mypy clean.
- UC REST via `httpx`, tests via `respx`.
- Prefer Arrow/Polars for interchange; avoid Pandas in core.
- One shared S3 config helper; no duplicated env parsing.
- Precise exceptions; no bare `except`.
