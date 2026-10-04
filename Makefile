.PHONY: help setup generate pdf dashboard checklist review clean test lint format all templates validate \
        new closure amendment continuing

CONFIG := config.yml
OUTPUT := output
RUN := uv run

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## Install dependencies
	uv sync

generate: ## Generate DOCX forms from config.yml
	$(RUN) python scripts/generate_all.py $(CONFIG) --output $(OUTPUT)

pdf: ## Convert DOCX → PDF + PNG previews
	$(RUN) python scripts/convert.py $(OUTPUT)

templates: ## Download official blank forms (for layout comparison)
	$(RUN) python scripts/fetch_templates.py

validate: ## Layout/font safety gate vs official blank forms (Win/Mac)
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
	rm -rf $(OUTPUT)/*.docx $(OUTPUT)/*.pdf $(OUTPUT)/preview $(OUTPUT)/layout_report.md checklist.md

new: ## Set phase to new case + generate
	$(RUN) python scripts/set_phase.py new $(CONFIG)
	$(MAKE) all

closure: ## Set phase to closure + generate
	$(RUN) python scripts/set_phase.py closure $(CONFIG)
	$(MAKE) all

amendment: ## Set phase to amendment + generate
	$(RUN) python scripts/set_phase.py amendment $(CONFIG)
	$(MAKE) all

continuing: ## Set phase to continuing review + generate
	$(RUN) python scripts/set_phase.py continuing $(CONFIG)
	$(MAKE) all
