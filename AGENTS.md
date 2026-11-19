# AGENTS.md

Rules for every agent working in this repo (Claude Code, Codex, or any other tool). Start with `README.md`.

## Fix what you find

On every feature or PR, fix what you find without asking, even when it is out of scope and your change did not cause it: an obvious bug, a gap, a leak (user data, secrets, money), or anything that could stop a user from paying. "Pre-existing", "not from this PR" or "out of scope" is never a reason to leave it (Ray, 2026-11-09 and 2026-11-12).

- Tiny and in code the change already touches: fix it in the same PR.
- Otherwise: open a small follow-up PR that goes through the same review, and name it in your report.
- Ask Ray first only for production database changes, spend, anything that cannot be undone, or a product decision.
- Reviewers list such findings as fixes to make, never as "out of scope".

## Who writes the code

Claude (Opus 5.5, extra high effort) leads every change. Backend work (server code, APIs, the money path, database, jobs, scripts, tests): Claude plans and briefs, Codex (`gpt-6.2-sol`, medium reasoning) and omp (GLM 5.3 max; GLM 5.3 Flash for mechanical work) write it, Claude reviews it, CodeRabbit reviews the PR, and Claude fixes CodeRabbit's valid findings. UI and UX work (screens, components, styles, on-screen copy, motion; in kabalah-motion-graphics the look of a template or video): Claude writes it, Codex and GLM review it adversarially, and the PR waits for CodeRabbit too. A PR with both follows each flow for its own part. If Codex or GLM cannot run (a failed Codex login counts), the other takes its part and a fresh Claude subagent does the adversarial review in place of the missing one; with neither, Claude writes it and a separate fresh Claude subagent does the adversarial review. The PR says who wrote what and which tool was missing. Always move GLM, Codex and kie.ai to the newest model available to us. Every PR also gets `ponytail-review`, plus `impeccable` when it changes UI, and an adversarial review in the environment with Codex CLI and GLM 5.3 max, where on backend the model that did not write a part reviews it, or the fresh Claude subagent in its place (Ray, 2026-11-19).
