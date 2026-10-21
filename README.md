# repoach demo

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/repoachhq/repoach-demo?quickstart=1)
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/repoachhq/repoach-demo)

A small invoice service (Python, `src/tally/`) and its table component
(TypeScript, `frontend/`), set up with [repoach](https://github.com/repoachhq/repoach):
`repoach.toml` comes from `repoach init`, the review job from
`repoach init --ci github`, and `docs/specs/` holds the one spec the code is
reviewed against.

Pull request [#1](https://github.com/repoachhq/repoach-demo/pull/1) plants three
defects and stays open: a SQL injection, an off-by-one, and a function with no
test. Its review and the gate's refusal are committed under `demo/recorded/`.

## Run it

```bash
make demo                  # replay the recorded walkthrough: no key, no model, no forge
make demo DEMO_MODE=live   # the same seven steps for real (gh login + a model provider)
make demo-live PR=1        # review pull request #1 yourself, dry run, then gate it
```

`make demo` needs only `python3`. The live modes need `repoach`
(`make install-repoach`), `gh auth login`, and a model provider: a logged-in
Claude Code CLI (`REPOACH_PROVIDER=claude_code`, the default of `demo-live`)
or an API key (see `repoach doctor`).

Opening the repository in Codespaces or Gitpod installs repoach at the pinned
commit, runs `repoach doctor`, and starts `make demo` in the first terminal.

## The 90-second script

| Time | Step | What you see |
|---|---|---|
| 0:00 | 1. `repoach init` | every file reports `unchanged`: the repository is already set up |
| 0:10 | 2. `gh pr create` | a pull request adds `search`, `page_count` and `dueTotal`, with the three defects |
| 0:20 | 3. `repoach ci review --dry-run` | four reviewers; the team verdict and each finding with its refuter state |
| 0:45 | 4. `repoach review gate` | refused, exit 5, the open blocking findings named |
| 0:55 | 5. fix commit | the prefix is bound, the count rounds up, `dueTotal` gets a test |
| 1:05 | 6. review and gate again | the gate passes, exit 0 |
| 1:20 | 7. `gh pr close` | the demo branch is gone |

The last line of a run is `demo: 7/7 steps, rcs 0 0 0 5 0 0 0`; `make demo`
exits 0 only when every step returned the code shown there.

## Layout

| Path | What it is |
|---|---|
| `src/tally/`, `tests/` | the service and its pytest suite |
| `frontend/src/` | `InvoiceTable.ts` and its vitest suite |
| `docs/specs/` | the governed spec, `SP-TALLY-INVOICES` |
| `demo/demo.py` | the walkthrough, live or replayed |
| `demo/defects/` | the planted defects and their fix, as patches |
| `demo/recorded/` | recorded runs (`*.jsonl`) and pull request #1's review and gate |
