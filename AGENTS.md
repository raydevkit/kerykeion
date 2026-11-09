# AGENTS.md

Rules for every agent working in this repo (Claude Code, Codex, or any other tool). Start with `README.md`.

## Bugs you find

Every obvious bug you find while touching code or reviewing it gets fixed, even when your change did not cause it. "Pre-existing" or "not from this PR" is never a reason to leave it (Ray, 2026-11-09).

- Tiny and in code the change already touches: fix it in the same PR.
- Otherwise: open a follow-up PR through the normal review flow, and name it in your report.
- Escalate to Ray instead only when it needs him: production database changes, spend, anything that cannot be undone, or a product decision.
- Reviewers list such bugs as findings to fix, never as "out of scope".
