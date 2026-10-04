#!/usr/bin/env bash
# IRB Submission Dashboard
# Usage: ./dashboard.sh [config.toml]

set -euo pipefail

CONFIG="${1:-config.toml}"
CHECKLIST="checklist.md"
OUTPUT_DIR="output"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Resolve config.toml (+ @references) via the project loader; honours $PHASE
if command -v uv &>/dev/null && [ -f "pyproject.toml" ]; then
    PY="uv run python"
else
    PY="python3"
fi

VARS="$($PY scripts/config.py "$CONFIG" --shell)" || exit 1
eval "$VARS"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║     ${CYAN}KFSYSCC IRB Submission Dashboard${NC}${BOLD}          ║${NC}"
echo -e "${BOLD}╠══════════════════════════════════════════════╣${NC}"
echo -e "${BOLD}║${NC} IRB No:     ${GREEN}${IRB_NO:-（待核發）}${NC}"
echo -e "${BOLD}║${NC} Phase:      ${CYAN}${PHASE_ZH}${NC} (${PHASE})"
echo -e "${BOLD}║${NC} PI:         ${PI}"
echo -e "${BOLD}║${NC} Study Type: ${STUDY_TYPE} / ${REVIEW_TYPE}"
echo -e "${BOLD}║${NC} Title:      ${TITLE}..."
echo -e "${BOLD}╠══════════════════════════════════════════════╣${NC}"

# Count files
DOCX_COUNT=$(find "$OUTPUT_DIR" -maxdepth 1 -name "*.docx" 2>/dev/null | wc -l | tr -d ' ')
PDF_COUNT=$(find "$OUTPUT_DIR" -maxdepth 1 -name "*.pdf" 2>/dev/null | wc -l | tr -d ' ')
PNG_COUNT=$(find "$OUTPUT_DIR/preview" -name "*.png" 2>/dev/null | wc -l | tr -d ' ')

echo -e "${BOLD}║${NC} ${GREEN}■${NC} DOCX files: ${DOCX_COUNT}"
echo -e "${BOLD}║${NC} ${GREEN}■${NC} PDF files:  ${PDF_COUNT}"
echo -e "${BOLD}║${NC} ${GREEN}■${NC} Previews:   ${PNG_COUNT}"
echo -e "${BOLD}╠══════════════════════════════════════════════╣${NC}"

# Checklist status
if [ -f "$CHECKLIST" ]; then
    DONE=$(grep -c '^■' "$CHECKLIST" 2>/dev/null || echo 0)
    TODO=$(grep -c '^□' "$CHECKLIST" 2>/dev/null || echo 0)
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
