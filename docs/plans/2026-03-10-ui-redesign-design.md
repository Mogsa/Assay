# UI Redesign Design

## Summary

Simplify the layout, fix voting bugs, and add a full-width question overlay for browsing.

## Decisions

1. **Drop right sidebar** — search/leaderboard already accessible via nav
2. **Slim left sidebar** (~200px) — more room for the feed
3. **Main feed takes majority of screen** — wider cards, more readable
4. **Richer feed cards** — title, author, excerpt + verdict/answer summary indicators
5. **Question overlay** — clicking expand opens full-width takeover (Problem | Solutions, two-column, independently scrollable)
6. **Close overlay** — X button + Escape + click backdrop
7. **Fix vote buttons** — loading state, error feedback, keep vertical arrows simple
8. **Fix API error handling** — FastAPI validation errors are arrays, not strings; normalize them
