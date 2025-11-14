<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

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

---

## 🔐 Git & Version Control Discipline

To keep the repository clean, traceable, and compatible with automated agents:

### 1. **Atomic Commits**
- Every commit should include **only logically related changes**.
- Always commit **only modified files** — *no bulk commits of unrelated files*.
- Example:
  ```bash
  git add src/lagoon/client.py tests/test_client.py
  git commit -m "feat(client): implement UCClient.get_table and tests"
  ```
- One feature or bugfix = one commit.  
  Documentation updates should be separate commits.

### 2. **Never Use Destructive Operations**
- 🚫 No `git push --force`, `git reset --hard`, or `rebase -i` on shared branches.
- Use `git revert` instead of rewriting history.
- Maintain linear, additive history unless working in an isolated feature branch.

### 3. **Commit Message Style**
Follow [Conventional Commits](https://www.conventionalcommits.org):
```
feat(core): add BaseTable write() support
fix(dispatch): correct format routing for parquet
docs(prd): update phase 2 objectives
test(client): add 4xx handling tests
```

### 4. **Review Workflow**
- All commits should run linting and tests locally (`ruff check . && mypy . && pytest`).
- PR titles mirror commit message of the main change.
- Merge via **squash or rebase merge**, never force push to `main`.

---

## Decision Log
Record notable design decisions here:
- YYYY-MM-DD: Initial scaffolding for data-lagoon (import: lagoon).
- YYYY-MM-DD: Enforced atomic commits & non-destructive Git operations.
