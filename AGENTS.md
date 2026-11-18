# AGENTS.md

Rules for every agent working in this repo (Claude Code, Codex, or any other tool). Start with `README.md`.

## Fix what you find

On every feature or PR, fix what you find without asking, even when it is out of scope and your change did not cause it: an obvious bug, a gap, a leak (user data, secrets, money), or anything that could stop a user from paying. "Pre-existing", "not from this PR" or "out of scope" is never a reason to leave it (Ray, 2026-11-09 and 2026-11-12).

- Tiny and in code the change already touches: fix it in the same PR.
- Otherwise: open a small follow-up PR that goes through the same review, and name it in your report.
- Ask Ray first only for production database changes, spend, anything that cannot be undone, or a product decision.
- Reviewers list such findings as fixes to make, never as "out of scope".

## Who writes the code

omp (GLM 5.3 max; GLM 5.3 Flash for mechanical work) and Codex (`gpt-6.2-sol`, medium reasoning) write the code from
Claude's plan or brief; Claude plans, then reviews: `ponytail-review` on every PR, plus `impeccable` when the PR changes
UI, and an adversarial review in the environment with Codex CLI and GLM 5.3 max (Ray, 2026-11-18). If Codex cannot run,
GLM writes it alone; with neither, Claude writes it and says so in the PR. Always move GLM, Codex and kie.ai to the newest
model available to us.
