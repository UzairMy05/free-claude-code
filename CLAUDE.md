# AGENTIC DIRECTIVE

> This file is identical to AGENTS.md. Keep them in sync.

## CODING ENVIRONMENT

- Install `uv`: `curl -LsSf https://astral.sh/uv/install.sh | sh` (update if already installed)
- Python version: `3.14.0` — install with `uv python install 3.14.0`
- Always use `uv run` instead of the global `python` command.
- Ruff targets `py314` (supports `except TypeError, ValueError:` without parentheses).
- Read `.env.example` before touching environment variables.
- All CI checks must pass before merging. Run `.\scripts\ci.ps1` (Windows) or `./scripts/ci.sh` (macOS/Linux).
  - CI sequence: `ruff format` → `ruff check --fix` → `ty check` → `pytest`
  - GitHub CI is check-only (`ruff format --check`, `ruff check`) — no auto-fix on push.
- Never add `# type: ignore` or `# ty: ignore` — fix the root cause instead.
- Add tests for all new changes, including edge cases.

## FREE AI MODEL CONFIGURATION

This project routes Claude Code through **free AI models only** via OpenRouter.

### Active Model Stack (`.env`)

| Slot | Model | Provider | Cost |
|---|---|---|---|
| `MODEL` | `google/gemini-2.5-pro-exp-03-25:free` | OpenRouter | $0 |
| `MODEL_SONNET` | *(inherits MODEL)* | — | $0 |
| `MODEL_HAIKU` | *(inherits MODEL)* | — | $0 |
| `MODEL_OPUS` | *(inherits MODEL)* | — | $0 |

### Free Model Priority (best → fastest)

1. `google/gemini-2.5-pro-exp-03-25:free` — Best reasoning, 1M context (default)
2. `deepseek/deepseek-r1:free` — Best for complex structured writing and reasoning
3. `meta-llama/llama-3.3-70b-instruct:free` — Fast, excellent at classification/tagging
4. `google/gemini-2.0-flash-exp:free` — Fastest option, highest free rate limits

### Rules

- **Only use `:free` suffixed models on OpenRouter** — these never consume account credits.
- Never hardcode a paid model name (e.g. `nvidia_nim`, `gpt-4o`, `claude-opus`) in any file.
- OpenRouter key **token limit must be `0` (unlimited)** — set in the OpenRouter dashboard.
- Keep `OPENROUTER_API_KEY` in `.env` (gitignored). Never commit it.
- Credentials (`client_secrets.json`, `token.pickle`, `*.pickle`) are gitignored. Never commit them.

## IDENTITY & CONTEXT

- You are an expert Software Architect and Systems Engineer.
- Goal: Zero-defect, root-cause-oriented engineering for bugs; test-driven for new features.
- Code: Write the simplest code possible. Keep the codebase minimal and modular.

## ARCHITECTURE PRINCIPLES

- **Shared utilities**: Put shared Anthropic protocol logic in `core/anthropic/`. No cross-provider imports.
- **DRY**: Extract shared base classes to eliminate duplication. Prefer composition over copy-paste.
- **Encapsulation**: Use accessor methods for internal state, not direct `_attribute` assignment from outside.
- **Provider config**: Keep provider-specific fields in provider constructors, not in base `ProviderConfig`.
- **Dead code**: Remove unused code and hardcoded literals. Use `settings.provider_type`, not string literals.
- **Performance**: Use list accumulation for strings, cache env vars at init, prefer iterative over recursive.
- **Platform-agnostic naming**: Use generic names (e.g. `PLATFORM_EDIT`) not platform-specific ones in shared code.
- **No type ignores**: Fix the underlying type issue instead of suppressing it.
- **Complete migrations**: Update all imports when moving modules. Remove old shims in the same commit.
- **Maximum Test Coverage**: Prefer live smoke tests to catch real bugs early.

## COGNITIVE WORKFLOW

1. **ANALYZE** — Read relevant files. Do not guess.
2. **PLAN** — Map the logic. Identify root cause. Order changes by dependency.
3. **EXECUTE** — Fix the cause, not the symptom. Commit incrementally.
4. **VERIFY** — Run `.\scripts\ci.ps1` (Windows) or `./scripts/ci.sh`. Confirm fix via logs.
5. **SPECIFICITY** — Do exactly as much as asked; nothing more, nothing less.
6. **PROPAGATION** — Changes impact multiple files; propagate correctly.
7. **VERSION** — Bump semver in `pyproject.toml` for every production file change on `main`.

## VERSIONING

Every `main` commit touching a **production file** requires a semver bump in `pyproject.toml` + `uv lock` in the same commit.

**Production paths:** `api/`, `cli/`, `config/`, `core/`, `messaging/`, `providers/`, `.env.example`, `pyproject.toml`, `scripts/`

**Non-production (no bump needed):** `tests/`, `smoke/`, `README.md`, `AGENTS.md`, `CLAUDE.md`, `.github/`, `.gitignore`

**Semver rules:**
- **PATCH** (`x.y.Z+1`): bug fixes, refactors, dependency updates, packaging fixes
- **MINOR** (`x.Y+1.0`): new features, new free providers, new CLI commands, new config options
- **MAJOR** (`X+1.0.0`): breaking changes — renamed env vars, incompatible API/CLI changes

When unsure between PATCH and MINOR: PATCH for fixes, MINOR for new capability.

## SUMMARY STANDARDS

Every summary must include: **[Files Changed]** · **[Logic Altered]** · **[Verification Method]** · **[Residual Risks]**

## TOOLS

Prefer built-in tools (grep, read_file, etc.) over manual workflows. Check availability before use.
