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

`make demo` replays steps 1-4 of the run recorded on 2026-10-21 (pull request
#6, opened and closed by `make demo DEMO_MODE=live`) in about 17 seconds.

| Step | Command | Recorded |
|---|---|---|
| 1 | `repoach init` | every file `unchanged`: the repository is already set up |
| 2 | `gh pr create` | the pull request adds `search`, `page_count` and `dueTotal`, with the three defects |
| 3 | `repoach ci review --dry-run` | 85 s live: `REQUEST_CHANGES`; the SQL injection and the off-by-one verified by the refuter, two speculative findings refuted; the tester names `dueTotal` as untested |
| 4 | `repoach review gate` | refused, exit 5: 5 open blocking findings, the spec's promised tests absent |
| 5 | fix commit | the prefix is bound, the count rounds up, `dueTotal` gets a test |
| 6 | review and gate again | all four reviewers `APPROVE`, the promised tests present, but the gate still refuses (exit 5) |
| 7 | `gh pr close` | the demo branch is gone |

The last line of `make demo` is `demo: 4/4 steps, rcs 0 0 0 5`, and it exits 0
only when every step returned that code. Steps 5-7 are in the recording
(`DEMO_UPTO=7 make demo` replays them): on repoach `f8915fc` a finding the
refuter verified at an earlier head is re-verified only by repoach's own fix
loop, so a fix pushed by a person leaves it blocking and step 6 ends with exit
5 where the walkthrough expects 0. The replay stops at the gate until repoach
re-judges those findings at the new head.

## Layout

| Path | What it is |
|---|---|
| `src/tally/`, `tests/` | the service and its pytest suite |
| `frontend/src/` | `InvoiceTable.ts` and its vitest suite |
| `docs/specs/` | the governed spec, `SP-TALLY-INVOICES` |
| `demo/demo.py` | the walkthrough, live or replayed |
| `demo/defects/` | the planted defects and their fix, as patches |
| `demo/recorded/` | recorded runs (`*.jsonl`) and pull request #1's review and gate |
