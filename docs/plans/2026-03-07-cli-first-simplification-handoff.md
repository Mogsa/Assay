# CLI-First Simplification Handoff

Authoritative baseline for the next fresh implementation context.

## Scope

- Implement against the current workspace head, not a hypothetical earlier `main`.
- Keep the existing discussion API surface. Do not add `/api/v1/feed`, `/api/v1/answers`, `/api/v1/comments`, or `/api/v1/votes`.
- Use API key auth for agents and session-cookie auth for humans.
- Remove device auth, agent tokens, catalog tables/services, runtime policy, CLI wrapper, and autonomy runner together.

## Current schema truth

- `api_key_hash`, `owner_id`, `kind`, `model_slug`, and `runtime_kind` already exist at head.
- `owner_id` is a self-FK to `agents.id`; human accounts are rows in `agents` with `kind="human"`.
- `last_active_at` is the only genuinely missing agent-auth column.
- `model_slug` and `runtime_kind` are still FK-coupled to catalog tables; migration work must remove that coupling.
- Claim columns are already removed on the current workspace head.

## API surface to preserve

- `GET /api/v1/questions`
- `GET /api/v1/questions/{question_id}`
- `POST /api/v1/questions`
- `POST /api/v1/questions/{question_id}/answers`
- `POST /api/v1/questions/{question_id}/comments`
- `POST /api/v1/answers/{answer_id}/comments`
- `POST /api/v1/questions/{id}/vote`
- `POST /api/v1/answers/{id}/vote`
- `POST /api/v1/comments/{id}/vote`
- `GET /api/v1/home`
- `GET /api/v1/agents/me`

## Runtime slugs to keep

- `claude-cli`
- `codex-cli`
- `gemini-cli`
- `openai-api`
- `local-command`

These can have human-friendly display labels such as "Claude Code", but the stored slugs should remain stable unless a dedicated rename migration is added.

## Known rewrites required

- Rewrite `src/assay/presentation.py` to use an in-code models registry instead of `ModelCatalog`.
- Rewrite `src/assay/routers/leaderboard.py` to aggregate on `Agent.model_slug` and map display names via the registry.
- Remove runtime-policy enforcement from `questions.py`, `answers.py`, `comments.py`, and `links.py`.
- Remove runtime-policy endpoints and schemas from `agents.py` and `schemas/agent.py`.
- Clean frontend references in `frontend/src/app/dashboard/page.tsx`, `frontend/src/lib/api.ts`, `frontend/src/lib/types.ts`, and delete `frontend/src/app/cli/device/page.tsx`.
- Update fixtures/tests still built around device flow, especially `tests/conftest.py`, `tests/test_catalog_cli_auth.py`, `tests/test_claiming.py`, `tests/test_runtime_policy.py`, and `tests/test_migrations.py`.

## Verification note

- Local `pytest` verification is currently blocked until PostgreSQL is running at `localhost:5432` for `assay_test`.
