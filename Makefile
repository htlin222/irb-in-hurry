.PHONY: help setup generate pdf preview dashboard checklist review clean test all templates validate

CONFIG := config.yml
OUTPUT := output
RUN := uv run

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## Install dependencies
	uv sync

generate: ## Generate DOCX forms from config.yml
	$(RUN) python scripts/generate_all.py $(CONFIG)

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
	rip $(OUTPUT)/*.docx $(OUTPUT)/*.pdf $(OUTPUT)/preview/*.png 2>/dev/null; true

new: ## Set phase to new case + generate
	$(RUN) python -c "import yaml; c=yaml.safe_load(open('$(CONFIG)')); c['phase']='new'; yaml.dump(c,open('$(CONFIG)','w'),allow_unicode=True,default_flow_style=False,sort_keys=False)"
	$(MAKE) all

closure: ## Set phase to closure + generate
	$(RUN) python -c "import yaml; c=yaml.safe_load(open('$(CONFIG)')); c['phase']='closure'; yaml.dump(c,open('$(CONFIG)','w'),allow_unicode=True,default_flow_style=False,sort_keys=False)"
	$(MAKE) all

amendment: ## Set phase to amendment + generate
	$(RUN) python -c "import yaml; c=yaml.safe_load(open('$(CONFIG)')); c['phase']='amendment'; yaml.dump(c,open('$(CONFIG)','w'),allow_unicode=True,default_flow_style=False,sort_keys=False)"
	$(MAKE) all

continuing: ## Set phase to continuing review + generate
	$(RUN) python -c "import yaml; c=yaml.safe_load(open('$(CONFIG)')); c['phase']='continuing'; yaml.dump(c,open('$(CONFIG)','w'),allow_unicode=True,default_flow_style=False,sort_keys=False)"
	$(MAKE) all
