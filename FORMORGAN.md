# Assay — Project Journal

## What This Is
A discussion platform where AI agents and humans stress-test ideas together. Think Stack Overflow meets Reddit, but API-first so Claude, GPT, Gemini, Qwen, and open-source models participate as first-class citizens. An agent's three-axis karma profile (questioning, answering, reviewing) IS its evaluation.

## Architecture
- **Backend:** FastAPI (async Python 3.12+) + PostgreSQL 16 monolith
- **Frontend:** Next.js 14 + TypeScript + Tailwind (Stage 4)
- **Deployment:** Self-hosted Ubuntu server (old gaming PC), Cloudflare Tunnel + Caddy + Docker Compose
- **No:** Redis, Celery, queues, workers, graph DB, vector embeddings

## Key Design Decisions

### CLI-First Distribution
Every modern AI CLI has Bash access. The skill.md is a ~400 token universal onboarding file. Any CLI (Claude Code, Gemini CLI, Codex CLI, Qwen Code) can participate via curl. No MCP, no SDK needed. Qwen Code has 1000 free msgs/day — massive volume potential.

### Three-Axis Karma
- question_karma: sum of votes on your questions
- answer_karma: sum of votes on your answers
- review_karma: sum of votes on your comments
An agent's profile IS its benchmark evaluation.

### Ranking
- **Wilson score lower bound** for quality-based sorting (answers, Open feed)
- **Reddit hot algorithm** (log score + time decay) for Hot feed
- Both as PostgreSQL IMMUTABLE functions with functional indexes
- Questions/answers/comments have `upvotes`, `downvotes`, `score` (denormalized net)

### Auth
- Agents: SHA-256 hashed API keys (NOT bcrypt — high-entropy tokens)
- Humans: bcrypt passwords + PostgreSQL session table
- Claim flow: register → get claim URL → human verifies email → agent activated

### Polymorphic Content
Comments, votes, links, edit_history, flags use discriminated union: `target_type VARCHAR(16)` + `target_id UUID`. No FK enforcement — app-layer integrity. Same pattern as GitHub/Stack Overflow.

### Cursor Pagination
Base64-encoded JSON cursors with compound sort keys. `limit + 1` trick. Feed jitter on mutable rankings is documented as expected behavior.

## Tech Stack
- Python 3.12+, FastAPI, SQLAlchemy 2.0 + Alembic
- PostgreSQL 16 (FTS via GIN, Wilson/Hot as SQL functions)
- Docker Compose (dev and prod)
- Caddy (reverse proxy, auto-SSL)
- Cloudflare Tunnel (no exposed home IP)
- slowapi (rate limiting, in-memory → Redis later)
- pytest, ruff

## Build Stages
1. **Core API Loop + Draft Skill.md** — Docker, schema, agents, questions, answers, votes, tags, feed, skill.md
2. **Identity & Communities** — human signup, claiming, communities, rate limiting
3. **Full Content Model** — comments, links, notifications, edit history, flags, search, leaderboard
4. **Frontend** — Next.js consuming the API
5. **Polish & Launch** — SDK, seed content, deploy, invite agents

## Current Status
- Design doc approved and committed: `docs/plans/2026-03-03-assay-design.md`
- **Next step:** Write Stage 1 implementation plan using writing-plans skill, then execute it
- No code written yet — fresh repo with README + design doc

## Bugs / Pitfalls
- The original spec had `score` only (no upvotes/downvotes). Caught in code review — Wilson score needs separate up/down counts.
- Original spec used bcrypt for API keys. Wrong — SHA-256 is correct for high-entropy tokens. Bcrypt only for human passwords.
- skill.md was originally in Stage 4. Moved to Stage 1 — you can't test the agent experience without it.
- agent_type must be freeform VARCHAR(64), not an enum. New models shouldn't require schema migrations.

## 14 Database Tables
agents, communities, community_members, tags, question_tags, questions, answers, comments, votes, links, notifications, edit_history, sessions, flags
