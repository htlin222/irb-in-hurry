#!/usr/bin/env bash
# Plays the doctor at the agent's multiple-choice questions (AskUserQuestion).
# Picks the option whose text matches a known true answer for this study;
# if none matches it does nothing, and the stage stalls visibly.
S="${1:-stagecast-irb}"
ANSWERS='全數納入|普查|全部納入'
while sleep 3; do
  pane="$(tmux -L "$S" capture-pane -p -t "$S" 2>/dev/null)" || continue
  grep -q 'Enter to select' <<<"$pane" || continue
  # Numbered options: "❯ 1. …" or "  2. …"
  opts="$(grep -E '^\s*(❯\s*)?[0-9]+\.' <<<"$pane")"
  n="$(grep -nE "$ANSWERS" <<<"$opts" | head -1 | cut -d: -f1)"
  [ -n "$n" ] || continue
  sleep 4   # let the viewer read the question
  for _ in $(seq 2 "$n"); do tmux -L "$S" send-keys -t "$S" Down; sleep 0.4; done
  tmux -L "$S" send-keys -t "$S" Enter
  sleep 8
done
