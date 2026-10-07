#!/usr/bin/env bash
# The worker. stagecast opens one session per chapter; every chapter after the
# first resumes the same conversation, so prompt 12 ("compared with the first
# submission…") is answered by the agent that made that submission.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export STAGECAST_STATE="$HERE/.stagecast" STAGECAST_PROMPTS="$HERE/prompts" STAGECAST_HOME="$HERE"
export IS_SANDBOX=1
unset CLAUDECODE
mkdir -p "$STAGECAST_STATE"
cont=(); [ -f "$STAGECAST_STATE/started" ] && cont=(--continue)
touch "$STAGECAST_STATE/started"
exec claude --dangerously-skip-permissions --settings "$HERE/hook-settings.json" "${cont[@]}"
