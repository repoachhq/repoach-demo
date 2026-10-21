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

Opening the repository in Codespaces or Gitpod starts `make demo` in the first
terminal as soon as the container is up (the replay needs only `python3`), and
installs repoach at the pinned commit alongside it (about 2.5 minutes measured
with pipx from the git commit), then runs `repoach doctor`.

## The 90-second script

`make demo` replays the seven steps of the run recorded on 2026-10-21 (pull
request #9, opened and closed by `make demo DEMO_MODE=live`) in about 36 seconds.

| Step | Command | Recorded |
|---|---|---|
| 1 | `repoach init` | every file `unchanged`: the repository is already set up |
| 2 | `gh pr create` | the pull request adds `search`, `page_count` and `dueTotal`, with the three defects |
| 3 | `repoach ci review --dry-run` | `REQUEST_CHANGES`; the SQL injection (two findings) and the off-by-one verified by the refuter, one speculative finding refuted |
| 4 | `repoach review gate` | refused, exit 5: 3 open blocking findings, the spec's promised tests absent |
| 5 | fix commit | the prefix is bound, the count rounds up, `dueTotal` gets a test |
| 6 | review and gate again | all four reviewers `APPROVE`; the gate re-verifies the 3 findings of the planted head at the fix head, resolves all 3, and passes (exit 0) |
| 7 | `gh pr close` | the demo branch is gone |

The last line of `make demo` is `demo: 7/7 steps, rcs 0 0 0 5 0 0 0`, and it
exits 0 only when every step returned that code. Step 6 needs repoach with
SP-GATE-REVERIFIES-AT-HEAD (repoachhq/repoach#232): on `f8915fc`, the commit
`make install-repoach` pins, a finding verified at an earlier head is
re-verified only by repoach's own fix loop, so a fix pushed by a person leaves
it blocking and step 6 of a live run ends with exit 5.

## Layout

| Path | What it is |
|---|---|
| `src/tally/`, `tests/` | the service and its pytest suite |
| `frontend/src/` | `InvoiceTable.ts` and its vitest suite |
| `docs/specs/` | the governed spec, `SP-TALLY-INVOICES` |
| `demo/demo.py` | the walkthrough, live or replayed |
| `demo/defects/` | the planted defects and their fix, as patches |
| `demo/recorded/` | recorded runs (`*.jsonl`) and pull request #1's review and gate |
