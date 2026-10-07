#!/usr/bin/env python3
"""Stop hook: the turn ended. Record WHICH prompt it answered, then signal.

Most chapters are questions with no artefact, so "the turn that received this
exact prompt has ended" is the honest completion signal for them. Chapters that
produce something also check the artefact (see ./check).
"""
import json, os, pathlib, subprocess, sys, time

state = pathlib.Path(os.environ["STAGECAST_STATE"])
prompts = pathlib.Path(os.environ["STAGECAST_PROMPTS"])
ev = json.load(sys.stdin)

def texts(entry):
    c = entry.get("message", {}).get("content")
    if isinstance(c, str):
        yield c
    elif isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and b.get("type") == "text":
                yield b.get("text", "")

wanted = {p.stem: p.read_text().strip() for p in prompts.glob("*.md")}
# A slash command reaches the transcript as its arguments, not its name.
keys = {k: [v.split(" ", 1)[1] if v.startswith("/") else v] for k, v in wanted.items()}
hit = None
for line in reversed(pathlib.Path(ev["transcript_path"]).read_text().splitlines()):
    try:
        e = json.loads(line)
    except ValueError:
        continue
    if e.get("type") != "user":
        continue
    for t in texts(e):
        hit = next((k for k, vs in keys.items() if any(v in t for v in vs)), None)
        if hit:
            break
    if hit:
        break

(state / "answered").mkdir(parents=True, exist_ok=True)
if hit:
    fp = subprocess.run([str(state.parent / "check"), "fp"], cwd=ev.get("cwd", "."),
                        capture_output=True, text=True).stdout.strip()
    (state / f"fp-{hit}").write_text(fp)
    (state / "answered" / hit).write_text(str(int(time.time())))
(state / "turn-ended").write_text(str(int(time.time())))
