# AGENTS.md

Rules for every agent working in this repo (Claude Code, GLM through omp, or any other tool). Start with `README.md`.

## Fix what you find

On every feature or PR, fix what you find without asking, even when it is out of scope and your change did not cause it: an obvious bug, a gap, a leak (user data, secrets, money), or anything that could stop a user from paying. "Pre-existing", "not from this PR" or "out of scope" is never a reason to leave it (Ray, 2026-11-09 and 2026-11-12).

- Tiny and in code the change already touches: fix it in the same PR.
- Otherwise: open a small follow-up PR that goes through the same review, and name it in your report.
- Ask Ray first only for production database changes, spend, anything that cannot be undone, or a product decision.
- Reviewers list such findings as fixes to make, never as "out of scope".

## Who writes and reviews the code (Ray, 2026-11-26)

Claude leads every change. GLM 5.4 max (omp, `zai/glm-5.4`, `--thinking max`) writes the code from the Claude lead's brief; UI and UX work (screens, components, styles, on-screen copy, motion; in kabalah-motion-graphics the look of a template or video) Claude writes. Claude reviews it (`ponytail-review`, plus `impeccable` on UI), then GLM 5.4 max and a fresh Claude subagent review it adversarially, CodeRabbit reviews the PR, and Claude fixes the valid findings. The writer of a part never reviews it. If GLM cannot run (429, quota, omp down), a second fresh Claude subagent takes its review. The PR says who wrote what and which tool was missing. Codex never writes or reviews code: it is for generation only (JPG stills, animated GIFs and SVG objects, with kie.ai when Codex runs out). Always move GLM, Codex and kie.ai to the newest model available to us (`/mnt/project-files/setup/model-routing.md`).

Every PR: open the PR, then run `ponytail-review` (plus `impeccable` when the PR changes UI) and an adversarial review in the environment by GLM 5.4 max (`omp -p --no-session --model zai/glm-5.4 --thinking max "<prompt>" < /dev/null`) and a fresh Claude subagent; wait for CodeRabbit's automatic review (1 hour at most), fix its valid findings (answer the others on their threads), then the thread that owns the PR merges it, with no separate review thread (Ray, 2026-11-15). Never run `codex review` or send a review prompt to `codex exec` (Ray, 2026-11-26).
