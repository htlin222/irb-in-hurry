#!/usr/bin/env bash
# IRB Submission Dashboard
# Usage: ./dashboard.sh [config.yml] [output_dir]

set -euo pipefail

CONFIG="${1:-config.yml}"
OUTPUT_DIR="${2:-output}"
CHECKLIST="checklist.md"

ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Use uv run if available, fallback to python3
if command -v uv &>/dev/null && [ -f "$ROOT/pyproject.toml" ]; then
    PY="uv run --quiet --project $ROOT python"
elif command -v python3 &>/dev/null; then
    PY="python3"
else
    echo "⚠ python3 not found"
    exit 1
fi

if [ ! -f "$CONFIG" ]; then
    echo "⚠ $CONFIG not found"
    exit 1
fi

# Read study fields through the same validated loader the generators use.
# Values are shell-quoted, so titles containing quotes or $ are safe to eval.
FIELDS="$($PY - "$CONFIG" <<'PY'
import shlex, sys
from scripts.config import load_config
from scripts.form_selector import PHASE_NAMES
c = load_config(sys.argv[1])
fields = {
    "IRB_NO": c["study"]["irb_no"] or "（尚未取得）",
    "PHASE": c["phase"],
    "PHASE_ZH": PHASE_NAMES.get(c["phase"], c["phase"]),
    "TITLE": c["study"]["title_zh"][:40],
    "PI": c["pi"]["name"],
    "STUDY_TYPE": c["study"].get("type", ""),
    "REVIEW_TYPE": c["study"].get("review_type", ""),
}
for k, v in fields.items():
    print(f"{k}={shlex.quote(str(v))}")
PY
)" || { echo "⚠ Could not parse $CONFIG"; exit 1; }
eval "$FIELDS"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║     ${CYAN}KFSYSCC IRB Submission Dashboard${NC}${BOLD}          ║${NC}"
echo -e "${BOLD}╠══════════════════════════════════════════════╣${NC}"
echo -e "${BOLD}║${NC} IRB No:     ${GREEN}${IRB_NO}${NC}"
echo -e "${BOLD}║${NC} Phase:      ${CYAN}${PHASE_ZH}${NC} (${PHASE})"
echo -e "${BOLD}║${NC} PI:         ${PI}"
echo -e "${BOLD}║${NC} Study Type: ${STUDY_TYPE} / ${REVIEW_TYPE}"
echo -e "${BOLD}║${NC} Title:      ${TITLE}..."
echo -e "${BOLD}╠══════════════════════════════════════════════╣${NC}"

# Count files
count_files() {  # count_files DIR GLOB — 0 when DIR is missing
    [ -d "$1" ] || { echo 0; return; }
    find "$1" -maxdepth 1 -name "$2" | wc -l | tr -d ' '
}
DOCX_COUNT=$(count_files "$OUTPUT_DIR" "*.docx")
PDF_COUNT=$(count_files "$OUTPUT_DIR" "*.pdf")
PNG_COUNT=$(count_files "$OUTPUT_DIR/preview" "*.png")

echo -e "${BOLD}║${NC} ${GREEN}■${NC} DOCX files: ${DOCX_COUNT}"
echo -e "${BOLD}║${NC} ${GREEN}■${NC} PDF files:  ${PDF_COUNT}"
echo -e "${BOLD}║${NC} ${GREEN}■${NC} Previews:   ${PNG_COUNT}"
echo -e "${BOLD}╠══════════════════════════════════════════════╣${NC}"

# Checklist status
if [ -f "$CHECKLIST" ]; then
    # grep -c prints 0 but exits 1 when nothing matches
    DONE=$(grep -c '^■' "$CHECKLIST" || true)
    TODO=$(grep -c '^□' "$CHECKLIST" || true)
    TOTAL=$((DONE + TODO))

    if [ "$TODO" -eq 0 ] && [ "$DONE" -gt 0 ]; then
        echo -e "${BOLD}║${NC} Checklist:  ${GREEN}${DONE}/${TOTAL} complete ✓${NC}"
    elif [ "$TODO" -gt 0 ]; then
        echo -e "${BOLD}║${NC} Checklist:  ${YELLOW}${DONE}/${TOTAL} complete (${TODO} pending)${NC}"
    fi
    echo -e "${BOLD}╠══════════════════════════════════════════════╣${NC}"

    # Show pending items
    if [ "$TODO" -gt 0 ]; then
        echo -e "${BOLD}║${NC} ${YELLOW}Pending:${NC}"
        grep '^□' "$CHECKLIST" | while read -r line; do
            echo -e "${BOLD}║${NC}   ${RED}${line}${NC}"
        done
        echo -e "${BOLD}╠══════════════════════════════════════════════╣${NC}"
    fi
else
    echo -e "${BOLD}║${NC} ${RED}□ No checklist found. Run generate_all.py first${NC}"
    echo -e "${BOLD}╠══════════════════════════════════════════════╣${NC}"
fi

# Output files
if [ "$DOCX_COUNT" -gt 0 ]; then
    echo -e "${BOLD}║${NC} ${CYAN}Output Files:${NC}"
    for f in "$OUTPUT_DIR"/*.docx; do
        SIZE=$(du -h "$f" 2>/dev/null | cut -f1 | tr -d ' ')
        BASENAME=$(basename "$f")
        # Check if PDF exists
        PDF_FILE="${f%.docx}.pdf"
        if [ -f "$PDF_FILE" ]; then
            echo -e "${BOLD}║${NC}   ${GREEN}■${NC} ${BASENAME} (${SIZE}) ${GREEN}✓ PDF${NC}"
        else
            echo -e "${BOLD}║${NC}   ${YELLOW}■${NC} ${BASENAME} (${SIZE}) ${RED}□ PDF${NC}"
        fi
    done
fi

echo -e "${BOLD}╚══════════════════════════════════════════════╝${NC}"
echo ""
