"""The repoach walkthrough: seven steps, live against the forge or replayed.

Live mode opens a pull request carrying the planted defects, lets the
advisory job review it, shows the gate refusing it, pushes the fix, reviews
and gates again, then closes the pull request. Every command, its output and
its exit code are written to ``demo/recorded/<date>.jsonl``.

Replay mode prints a recording with no forge, no model and no key.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECORDED = ROOT / "demo" / "recorded"
DEFECTS = ROOT / "demo" / "defects"
EXPECTED_RCS = [0, 0, 0, 5, 0, 0, 0]
TITLES = {
    1: "repoach init on a clean clone",
    2: "open a pull request carrying the planted defects",
    3: "the advisory job reviews it",
    4: "the gate refuses the head: blocking findings are still open",
    5: "a second commit fixes the defects",
    6: "review and gate again",
    7: "close the pull request and delete the branch",
}
REVIEW_KEYS = {"pr_number", "final_verdict", "n_blockers", "n_majors", "reviews", "findings"}
CI_REVIEW_KEYS = {"outcome", "pr_number", "final_verdict", "review"}
GATE_KEYS = {"pr_number", "outcome", "head_sha", "merge", "reasons", "facts"}
GATE_FACT_KEYS = {"ci_green", "open_blocking_findings", "review_complete", "spec_coverage"}

BOLD, DIM, RED, GREEN, RESET = "\033[1m", "\033[2m", "\033[31m", "\033[32m", "\033[0m"


def _color(text: str, code: str) -> str:
    """Wrap ``text`` in an ANSI code when stdout is a terminal or FORCE_COLOR is set."""
    if os.environ.get("NO_COLOR") or not (sys.stdout.isatty() or os.environ.get("FORCE_COLOR")):
        return text
    return f"{code}{text}{RESET}"


def _json_or_none(text: str) -> dict | None:
    """Parse a command's stdout as one JSON object, else None."""
    try:
        value = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None
    return value if isinstance(value, dict) else None


def _review_lines(payload: dict) -> list[str]:
    """Summarise a ``review pr`` payload (or the one nested in ``ci review``)."""
    review = payload.get("review") if isinstance(payload.get("review"), dict) else payload
    lines = [f"team verdict: {review.get('final_verdict')}"]
    for entry in review.get("reviews") or []:
        lines.append(f"  {entry.get('role', '?'):<9} {entry.get('verdict')}")
    for f in review.get("findings") or []:
        state = (f.get("refutation") or {}).get("state", "?")
        where = f.get("file") or f.get("path") or "?"
        line = f.get("line")
        loc = f"{where}:{line}" if line else where
        title = f.get("title") or f.get("claim") or f.get("message") or ""
        lines.append(f"  [{f.get('severity', '?')}] {loc} {title[:90]} ({state})")
    usage = review.get("usage") or {}
    total = usage.get("total") if isinstance(usage, dict) else None
    if isinstance(total, dict) and total.get("duration_s") is not None:
        lines.append(f"  model time: {total['duration_s']} s")
    return lines


def _gate_lines(payload: dict) -> list[str]:
    """Summarise a ``review gate`` payload."""
    facts = payload.get("facts") or {}
    verdict = "MERGE" if payload.get("merge") else "REFUSED"
    lines = [
        f"gate: {verdict}  (ci_green={facts.get('ci_green')}, "
        f"open_blocking_findings={facts.get('open_blocking_findings')}, "
        f"review_complete={facts.get('review_complete')})"
    ]
    lines += [f"  reason: {r}" for r in payload.get("reasons") or []]
    return lines


def _render(record: dict) -> list[str]:
    """Turn one recorded command into the lines a viewer reads."""
    payload = _json_or_none(record.get("stdout", ""))
    argv = record.get("argv") or []
    if payload is not None and "gate" in argv:
        return _gate_lines(payload)
    if payload is not None and ("final_verdict" in payload or "review" in payload):
        return _review_lines(payload)
    text = (record.get("stdout") or "") + (record.get("stderr") or "")
    return [ln for ln in text.splitlines() if ln.strip()][:12]


def _missing_keys(record: dict) -> list[str]:
    """Name the keys the installed repoach's JSON contract requires and the record lacks."""
    payload = _json_or_none(record.get("stdout", ""))
    argv = record.get("argv") or []
    if payload is None:
        return []
    if "gate" in argv:
        missing = sorted(GATE_KEYS - payload.keys())
        missing += [f"facts.{k}" for k in sorted(GATE_FACT_KEYS - (payload.get("facts") or {}).keys())]
        return missing
    if argv[:3] == ["repoach", "ci", "review"]:
        missing = sorted(CI_REVIEW_KEYS - payload.keys())
        nested = payload.get("review")
        if isinstance(nested, dict):
            missing += [f"review.{k}" for k in sorted(REVIEW_KEYS - nested.keys())]
        return missing
    if argv[:3] == ["repoach", "review", "pr"]:
        return sorted(REVIEW_KEYS - payload.keys())
    return []


def _latest_recording() -> Path:
    """The recording replay plays: DEMO_RECORDING, else the newest one."""
    chosen = os.environ.get("DEMO_RECORDING")
    if chosen:
        return Path(chosen)
    runs = sorted(RECORDED.glob("*.jsonl"))
    if not runs:
        sys.exit("demo: no recording under demo/recorded/ (run make demo DEMO_MODE=live once)")
    return runs[-1]


def replay(fast: bool, verify: bool) -> int:
    """Print a recording step by step and check its exit codes."""
    path = _latest_recording()
    records = [json.loads(ln) for ln in path.read_text().splitlines() if ln.strip()]
    print(_color(f"repoach demo: replaying {path.relative_to(ROOT)} (no forge, no model)", DIM))
    started = time.monotonic()
    rcs: dict[int, int] = {}
    for record in records:
        step = int(record["step"])
        if step not in rcs:
            print()
            print(_color(f"[{step}/7] {TITLES.get(step, '')}", BOLD))
        print(_color("$ " + shlex.join(record["argv"]), DIM))
        if not fast:
            time.sleep(min(float(record.get("elapsed_s", 0)) / 20.0, 4.0) + 0.6)
        for line in _render(record):
            refused = line.startswith("gate: REFUSED") or "REQUEST_CHANGES" in line
            print(_color(line, RED) if refused else line)
        rc = int(record["rc"])
        print(_color(f"exit {rc}", GREEN if rc == 0 else RED))
        rcs[step] = rc
        if verify:
            missing = _missing_keys(record)
            if missing:
                print(f"demo: step {step}: recorded JSON lacks {', '.join(missing)}; re-record it")
                return 1
    return _summary(rcs, started)


def _summary(rcs: dict[int, int], started: float) -> int:
    """Print the closing line and return 0 when the exit codes are the expected ones."""
    got = [rcs.get(n) for n in range(1, 8)]
    print()
    print(f"elapsed: {time.monotonic() - started:.1f} s")
    print(f"demo: {sum(1 for r in got if r is not None)}/7 steps, rcs " + " ".join(str(r) for r in got))
    return 0 if got == EXPECTED_RCS else 1


class Live:
    """Run the seven steps against the forge and the model, recording each command."""

    def __init__(self, record: bool) -> None:
        self.records: list[dict] = []
        self.record = record
        self.branch = "demo/planted-defect-" + dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.work = ROOT / "tmp" / "demo-work"

    def run(self, step: int, argv: list[str], *, cwd: Path = ROOT, show: bool = True) -> dict:
        """Run one command, echo it and its output, and keep the record."""
        if show:
            print(_color("$ " + shlex.join(argv), DIM), flush=True)
        t0 = time.monotonic()
        proc = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, check=False)
        rec = {
            "step": step,
            "argv": argv,
            "rc": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "elapsed_s": round(time.monotonic() - t0, 1),
        }
        if show:
            for line in _render(rec):
                print(line)
            print(_color(f"exit {proc.returncode}", GREEN if proc.returncode == 0 else RED), flush=True)
            self.records.append(rec)
        elif proc.returncode != 0:
            sys.stderr.write(proc.stdout + proc.stderr)
            raise SystemExit(f"demo: {shlex.join(argv)} failed with {proc.returncode}")
        return rec

    def _commit_patch(self, patch: str, message: str) -> None:
        """Apply one patch on the demo branch in a scratch worktree and push it."""
        quiet = {"show": False}
        self.run(0, ["git", "-C", str(self.work), "apply", str(DEFECTS / patch)], **quiet)
        self.run(0, ["git", "-C", str(self.work), "add", "-A"], **quiet)
        self.run(0, ["git", "-C", str(self.work), "commit", "-q", "-m", message], **quiet)
        self.run(0, ["git", "-C", str(self.work), "push", "-q", "-u", "origin", self.branch], **quiet)

    def _close_leftovers(self) -> None:
        """Close any demo pull request a previous run left open."""
        out = self.run(0, ["gh", "pr", "list", "--state", "open", "--json", "number,headRefName"], show=False)
        for pr in json.loads(out["stdout"] or "[]"):
            if pr["headRefName"].startswith("demo/planted-defect-"):
                print(f"demo: closing leftover #{pr['number']} ({pr['headRefName']})")
                self.run(0, ["gh", "pr", "close", str(pr["number"]), "--delete-branch"], show=False)

    def walk(self) -> int:
        """Walk the seven steps and write the recording."""
        for need in ("gh", "repoach"):
            if subprocess.run(["which", need], capture_output=True, check=False).returncode:
                print(f"demo: {need} is not installed; try make demo (replay)")
                return 2
        if subprocess.run(["gh", "auth", "status"], capture_output=True, check=False).returncode:
            print("demo: no GitHub login (gh auth login, or GH_TOKEN); try make demo (replay)")
            return 2
        started = time.monotonic()
        install_t0 = os.environ.get("DEMO_INSTALL_T0")
        self._close_leftovers()

        print(_color(f"\n[1/7] {TITLES[1]}", BOLD))
        self.run(1, ["repoach", "init"])

        print(_color(f"\n[2/7] {TITLES[2]}", BOLD))
        self.run(0, ["git", "fetch", "-q", "origin", "main"], show=False)
        self.run(0, ["git", "worktree", "add", "-q", "-b", self.branch, str(self.work), "origin/main"], show=False)
        try:
            self._commit_patch("planted.patch", "feat(store): search invoices, count pages, total what is due")
            body = "Spec: SP-TALLY-INVOICES\n\nAdds customer search, a page count and the due total."
            pr = self.run(
                2,
                ["gh", "pr", "create", "--base", "main", "--head", self.branch,
                 "--title", "feat(store): search invoices, count pages, total what is due", "--body", body],
            )
            number = pr["stdout"].strip().rsplit("/", 1)[-1]

            print(_color(f"\n[3/7] {TITLES[3]}", BOLD))
            self.run(3, ["repoach", "ci", "review", "--pr", number, "--forge", "github", "--dry-run"])
            if install_t0:
                print(f"install-to-first-review: {time.time() - float(install_t0):.0f} s")

            print(_color(f"\n[4/7] {TITLES[4]}", BOLD))
            gate = self.run(4, ["repoach", "review", "gate", number, "--forge", "github"])
            if gate["rc"] != 5:
                print("demo: the gate did not refuse; no reviewer found the defects in demo/defects/planted.patch")

            print(_color(f"\n[5/7] {TITLES[5]}", BOLD))
            self._commit_patch("fix.patch", "fix(store): bind the search prefix, round the page count up, test the due total")
            self.run(5, ["git", "-C", str(self.work), "log", "--oneline", "-2"])

            print(_color(f"\n[6/7] {TITLES[6]}", BOLD))
            self.run(6, ["repoach", "ci", "review", "--pr", number, "--forge", "github", "--dry-run"])
            self.run(6, ["repoach", "review", "gate", number, "--forge", "github"])

            print(_color(f"\n[7/7] {TITLES[7]}", BOLD))
            self.run(7, ["gh", "pr", "close", number, "--delete-branch"])
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(self.work)], cwd=ROOT, check=False)
            subprocess.run(["git", "branch", "-D", self.branch], cwd=ROOT, capture_output=True, check=False)
        if self.record:
            RECORDED.mkdir(parents=True, exist_ok=True)
            out = RECORDED / (dt.date.today().isoformat() + ".jsonl")
            out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in self.records))
            print(f"demo: recorded {out.relative_to(ROOT)}")
        rcs: dict[int, int] = {}
        for r in self.records:
            rcs[r["step"]] = r["rc"]
        return _summary(rcs, started)


def main() -> int:
    """Parse the mode and run it."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["replay", "live"], default=os.environ.get("DEMO_MODE") or "replay")
    args = parser.parse_args()
    if args.mode == "live":
        return Live(record=os.environ.get("DEMO_RECORD", "1") == "1").walk()
    return replay(fast=os.environ.get("DEMO_FAST") == "1", verify=os.environ.get("DEMO_VERIFY") == "1")


if __name__ == "__main__":
    sys.exit(main())
