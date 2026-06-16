# Datus Agent Guidelines

## Canonical Instructions

This file is the canonical guide for Codex and Claude when working under `datus-agent/`. Keep shared agent rules here. Keep `CLAUDE.md` as a short Claude entry point only.

## Project Structure

`datus/` contains the Python package. Major areas are `agent/` for workflows, `cli/` for command surfaces, `api/`, `gateway/`, `tools/`, `storage/`, `schemas/`, `prompts/`, and shared helpers in `utils/`. Configuration examples live in `conf/`. Tests are under `tests/`, split into `unit_tests/`, `integration/`, `regression/`, with shared fixtures in `tests/data/` and `tests/conf/`. Documentation is in `docs/`, benchmarks in `benchmark/`, packaging scripts in `build_scripts/`, and CI helpers in `ci/`.

## Build, Test, and Development Commands

Use Python 3.12 and `uv`.

```bash
uv sync --dev
uv run datus --version
uv run datus-agent --version
uv run pytest tests/unit_tests/ -q
uv run python ci/run-pr-tests.py upstream/main
uv run pytest -m nightly tests/
uv run pytest -m "nightly or regression" tests/
uv run ruff format datus/ tests/
uv run ruff check datus/ tests/
```

Build packages with `make build`, validate with `make check`, smoke-test with `make test`, and run all packaging steps with `make all`. Build docs with:

```bash
uv run --with mkdocs-material --with mike --with mkdocs-static-i18n mkdocs build --strict
```

## Coding Style & Guardrails

Ruff is the formatter, import sorter, and linter. Line length is 120 and target runtime is Python 3.12. Use typed, focused functions; keep first-party imports under `datus`; use `snake_case` files/functions, `PascalCase` classes, and `test_*.py` tests.

Use `from datus.utils.loggings import get_logger`; do not use `print()` in production code. Raise `DatusException(ErrorCode.XXX, ...)` from `datus.utils.exceptions`. Use English in code, comments, commit messages, and PR text; Chinese is only for docs explicitly targeting Chinese readers.

Do not import database connectors directly; use `ConnectorRegistry` or `db_manager_instance`. Do not hardcode LLM calls in nodes; go through `LLMBaseModel`. New tunable parameters belong in YAML config, not hardcoded constants. Secrets must come from environment variables or `${ENV_VAR}` substitution.

## CLI and TUI Rules

CLI colours, symbols, and helpers live in `datus/cli/cli_styles.py`. Use helpers such as `print_error`, `print_success`, `print_warning`, `print_info`, `print_status`, `print_usage`, and `print_empty_set` instead of inline Rich markup. Avoid emoji in new code; use Unicode `✓` and `✗` only. Use `TABLE_HEADER_STYLE`, `build_row_table()`, and `CODE_THEME = "monokai"` where applicable.

For full-screen TUI components, follow `ModelApp`: wrap `app.run()` in `tui_app.suspend_input()`, do not nest `asyncio.run()`, use `DynamicContainer` with `Condition` guards, and exit via `app.exit(result=Selection(...))`.

## Testing Guidelines

Use pytest. Add unit tests near the matching subsystem under `tests/unit_tests/`; use `tests/integration/` for multi-component or external-adapter behavior; use `tests/regression/` for broader product coverage. Mark tests with existing markers such as `acceptance`, `component`, `integration`, `nightly`, `benchmark`, or `regression`.

Routine CI tests must be deterministic and must mock external calls, including LLMs, remote databases, network, and optional packages. Nightly and regression tests may use real providers, but must skip cleanly when required keys are missing. Use `@pytest.mark.asyncio` and `pytest_asyncio.fixture` for async tests; shared event-loop helpers are in `datus/utils/async_utils.py`.

When modifying modules, mirror the source path in unit tests: `datus/utils/json_utils.py` maps to `tests/unit_tests/utils/test_json_utils.py`. For high-risk areas such as `datus/models/`, `datus/agent/node/`, `datus/tools/func_tool/`, `datus/tools/skill_tools/`, `datus/mcp_server.py`, or `datus/storage/document/`, also run the related integration or regression tests.

## Extension Points

- New node: add a file in `datus/agent/node/`, inherit `Node` or `AgenticNode`, register type in `datus/configuration/node_type.py`, and add factory mapping in `Node.new_instance()`.
- New provider using an existing interface: add entries to `conf/providers.yml` and `datus/conf/providers.yml`.
- New model SDK/auth: add a file in `datus/models/`, inherit `LLMBaseModel`, register in `MODEL_TYPE_MAP`, and update provider regression coverage.
- New MCP tool: add the function under `datus/tools/func_tool/` and register it in the MCP server tool list.

## Commit & Pull Request Guidelines

PR titles must start with `[BugFix]`, `[Enhancement]`, `[Feature]`, `[Refactor]`, `[UT]`, `[Doc]`, `[Tool]`, or `[Others]`. PR bodies must follow `.github/PULL_REQUEST_TEMPLATE.md` with `Why`, `Solution`, and `Test Cases` filled in. Before pushing, run Ruff, `uv run python ci/run-pr-tests.py upstream/main`, and `uv run python ci/audit_tests.py --repo-root . --diff-only upstream/main`; run merge-queue rehearsal when changing CI or acceptance harness behavior. Never use `--no-verify`.

## Local Git Layout

This repository is the fund-industry downstream version of upstream Datus. Use `/home/astenir/Code/oss/Datus-agent-fund` as the fund development worktree on `main`, and `/home/astenir/Code/oss/Datus-agent` as the clean upstream-reference worktree on `upstream-main`.

`origin/main` belongs to `astenir/Datus-agent-fund` and carries fund-specific changes. Do not treat it as a clean upstream mirror, and do not use GitHub's "Sync fork" button for routine updates. The fund branch should follow stable upstream release tags or release branches, not raw `upstream/main`.

Upgrade by testing the release first on a branch, then merge it into fund `main`:

```bash
cd /home/astenir/Code/oss/Datus-agent-fund
git fetch upstream
git switch -c upgrade/upstream-0.3.x
git merge v0.3.x
# run focused tests and resolve conflicts
git switch main
git merge --no-ff upgrade/upstream-0.3.x
git push origin main
```

Use `/home/astenir/Code/oss/Datus-agent` only to inspect or refresh the clean upstream baseline:

```bash
cd /home/astenir/Code/oss/Datus-agent
git fetch upstream
git merge --ff-only upstream/main
```

## Security & Configuration

Copy `conf/agent.yml.example` to `conf/agent.yml` for local work and reference credentials through environment variables such as `${OPENAI_API_KEY}`. Keep generated local state in `.datus/` or `~/.datus/` out of commits.
