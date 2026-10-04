.PHONY: help setup check generate pdf templates validate all dashboard checklist review test clean init \
        new amendment re_review continuing closure sae ib_update import suspension appeal

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

templates: ## Download official blank forms (for layout comparison)
	$(RUN) python scripts/fetch_templates.py

validate: ## Layout/font safety gate vs official blank forms (Win/Mac)
	$(RUN) python scripts/validate_layout.py $(OUTPUT)

all: generate pdf validate dashboard ## Generate + convert + validate + dashboard

dashboard: ## Show submission status
	./dashboard.sh $(CONFIG)

checklist: ## View checklist
	@cat checklist.md

review: ## Run simulated IRB reviewer on generated forms
	$(RUN) python scripts/reviewer.py $(CONFIG)

test: ## Run tests
	$(RUN) pytest tests/ -v

clean: ## Remove generated files
	rm -rf $(OUTPUT) checklist.md

# Phase shortcuts: make closure == make all PHASE=closure (config.toml untouched)
new amendment re_review continuing closure sae ib_update import suspension appeal:
	@$(MAKE) --no-print-directory all PHASE=$@
