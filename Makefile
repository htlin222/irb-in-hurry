.PHONY: help setup check generate pdf templates onboard validate all dashboard checklist review test lint format clean init \
        set-phase new amendment re_review continuing closure sae ib_update import suspension appeal

# Single source of truth: config.toml (+ the files it references, e.g. cv.toml, 中文計畫摘要.md)
CONFIG  := config.toml
OUTPUT  := output
RUN     := uv run
# Override the phase for one run without editing config.toml: make all PHASE=closure
PHASE   ?=
export PHASE

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
	@printf "  \033[36m%-12s\033[0m %s\n" "<phase>" "make closure|amendment|continuing|… = make all PHASE=<phase>"

setup: ## Install dependencies
	uv sync

init: ## Start from an example: make init EXAMPLE=tdxd-her2low (refuses to overwrite)
	@test -n "$(EXAMPLE)" || { echo "Usage: make init EXAMPLE=<name>"; ls examples; exit 1; }
	@for f in examples/$(EXAMPLE)/*; do \
		b=$$(basename "$$f"); \
		if [ -e "$$b" ] && [ -z "$(FORCE)" ]; then echo "✗ $$b exists (FORCE=1 to overwrite)"; exit 1; fi; \
	done
	cp examples/$(EXAMPLE)/* .
	@$(RUN) python scripts/config.py $(CONFIG)

check: ## Resolve @references in config.toml and validate required fields
	$(RUN) python scripts/config.py $(CONFIG)

generate: ## Generate DOCX forms from config.toml
	$(RUN) python scripts/generate_all.py $(CONFIG) --output $(OUTPUT)

pdf: ## Convert DOCX → PDF + PNG previews
	$(RUN) python scripts/convert.py $(OUTPUT)

templates: ## Cache the institution's official blank forms (for layout comparison)
	$(RUN) python scripts/fetch_templates.py

onboard: ## Draft a new institution from blanks in templates/$(INST)/  (make onboard INST=myhosp)
	@test -n "$(INST)" || (echo "usage: make onboard INST=<id>  (blanks in templates/<id>/)"; exit 2)
	$(RUN) python scripts/onboard.py $(INST)

validate: ## Layout/font safety gate vs the institution's blank forms (Win/Mac)
	$(RUN) python scripts/validate_layout.py $(OUTPUT)

all: generate pdf validate dashboard ## Generate + convert + validate + dashboard

dashboard: ## Show submission status
	./dashboard.sh $(CONFIG) $(OUTPUT)

checklist: ## View checklist
	@cat checklist.md

review: ## Run simulated IRB reviewer on generated forms
	$(RUN) python scripts/reviewer.py $(CONFIG) $(OUTPUT)

test: ## Run tests
	$(RUN) pytest -v

lint: ## Lint Python sources
	$(RUN) ruff check .

format: ## Auto-fix lint issues (imports, etc.)
	$(RUN) ruff check --fix .

clean: ## Remove generated files
	rm -rf $(OUTPUT) checklist.md

set-phase: ## Persist the phase in config.toml (keeps comments): make set-phase PHASE=closure
	@test -n "$(PHASE)" || { echo "Usage: make set-phase PHASE=<phase>"; exit 1; }
	$(RUN) python scripts/set_phase.py $(PHASE) $(CONFIG)

# Phase shortcuts: make closure == make all PHASE=closure (config.toml untouched)
new amendment re_review continuing closure sae ib_update import suspension appeal:
	@$(MAKE) --no-print-directory all PHASE=$@
