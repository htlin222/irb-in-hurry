.PHONY: help setup check generate pdf templates onboard validate all dashboard checklist review test lint format clean init \
        doctor build \
        set-phase new amendment re_review continuing closure sae ib_update import suspension appeal

# Thin wrapper over the `irbh` CLI (irb_in_hurry/cli.py) for working in this checkout.
# Outside the repo, install the package and call `irbh` directly (see README).
# Single source of truth: config.toml (+ the files it references, e.g. cv.toml, 中文計畫摘要.md)
CONFIG  := config.toml
OUTPUT  := output
RUN     := uv run
IRBH    := $(RUN) irbh
# Override the phase for one run without editing config.toml: make all PHASE=closure
PHASE   ?=
export PHASE

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
	@printf "  \033[36m%-12s\033[0m %s\n" "<phase>" "make closure|amendment|continuing|… = make all PHASE=<phase>"

setup: ## Install dependencies
	uv sync

init: ## Start from an example: make init EXAMPLE=tdxd-her2low (refuses to overwrite)
	$(IRBH) init $(EXAMPLE) $(if $(FORCE),--force)

check: ## Resolve @references in config.toml and validate required fields
	$(IRBH) check $(CONFIG)

generate: ## Generate DOCX forms from config.toml
	$(IRBH) generate $(CONFIG) --output $(OUTPUT)

pdf: ## Convert DOCX → PDF + PNG previews
	$(IRBH) pdf --output $(OUTPUT)

templates: ## Cache the institution's official blank forms (for layout comparison)
	$(IRBH) templates $(CONFIG)

onboard: ## Draft a new institution from blanks in templates/$(INST)/  (make onboard INST=myhosp)
	@test -n "$(INST)" || (echo "usage: make onboard INST=<id>  (blanks in templates/<id>/)"; exit 2)
	$(IRBH) onboard $(INST)

validate: ## Layout/font safety gate vs the institution's blank forms (Win/Mac)
	$(IRBH) validate $(CONFIG) --output $(OUTPUT)

all: generate pdf validate dashboard ## Generate + convert + validate + dashboard

dashboard: ## Show submission status
	$(IRBH) dashboard $(CONFIG) --output $(OUTPUT)

checklist: ## View checklist
	@cat checklist.md

review: ## Run simulated IRB reviewer on generated forms
	$(IRBH) review $(CONFIG) --output $(OUTPUT)

test: ## Run tests
	$(RUN) pytest -v

doctor: ## Check LibreOffice, poppler, form font, config and cached blanks
	$(IRBH) doctor $(CONFIG)

build: ## Build the sdist + wheel into dist/
	uv build

lint: ## Lint Python sources
	$(RUN) ruff check .

format: ## Auto-fix lint issues (imports, etc.)
	$(RUN) ruff check --fix .

clean: ## Remove generated files
	rm -rf $(OUTPUT) checklist.md

set-phase: ## Persist the phase in config.toml (keeps comments): make set-phase PHASE=closure
	@test -n "$(PHASE)" || { echo "Usage: make set-phase PHASE=<phase>"; exit 1; }
	$(IRBH) set-phase $(PHASE) $(CONFIG)

# Phase shortcuts: make closure == make all PHASE=closure (config.toml untouched)
new amendment re_review continuing closure sae ib_update import suspension appeal:
	@$(MAKE) --no-print-directory all PHASE=$@
