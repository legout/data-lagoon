# CONTRIBUTING.md — data-lagoon

Welcome to **data-lagoon** — the unified Python SDK for lakehouse data via Unity Catalog.

We follow a clear set of collaboration and automation principles to keep the codebase maintainable and reproducible.

---

## 🧭 Getting Started

1. Clone and install in editable mode:
   ```bash
   git clone https://github.com/your-org/data-lagoon.git
   cd data-lagoon
   pip install -e .[dev]
   ```
2. Run sanity checks:
   ```bash
   ruff check . && mypy . && pytest
   ```

---

## 🧠 Working With Live Documentation Contexts

To stay synchronized with evolving dependencies (PyIceberg, Delta-RS, DuckDB, etc.), we use **Context7** and **DeepWiki MCP**.

### Context7
Fetch live documentation contexts before modifying adapters or core APIs:
```bash
context7.fetch("pyiceberg API reference")
context7.fetch("delta-rs python bindings")
context7.fetch("duckdb SQL functions")
```
Use this only as *context*, not as code source.

### DeepWiki MCP
When Context7 is unavailable, use DeepWiki MCP for similar lookups:
```bash
deepwiki.search("pyarrow dataset API latest")
deepwiki.search("ibis expression API reference")
```
Copy only relevant API summaries into your local reasoning context — never commit raw documentation or scraped text.

### Rules
- Always cite doc versions in comments when you rely on external APIs.
- Refresh fetched contexts before major releases.
- Do not embed large documentation files in this repository.

---

## 🧩 Code Style & Linting

- Type hints required (`mypy --strict` clean).
- Lint clean (`ruff check .`).
- Docstrings in Google style.
- Prefer Arrow/Polars over Pandas.
- Keep adapters self-contained and protocol-compliant.

---

## 🧱 Git Discipline

- Atomic commits only (see `AGENTS.md` for full policy).
- Never use destructive Git operations on shared branches.
- Use conventional commits for messages.
- PRs must pass tests, ruff, and mypy before merge.

---

## 🧩 Reporting Issues or Proposing Features

Open a GitHub Issue or Discussion tagged as one of:
- `bug`: for reproducible issues.
- `enhancement`: for new capabilities.
- `adapter`: for format/engine integration requests.

When proposing, reference relevant **PRD.md** sections if possible.

---

Happy contributing, and thank you for helping grow `data-lagoon`!
