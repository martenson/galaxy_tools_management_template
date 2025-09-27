ifndef INSTANCE
$(error INSTANCE is required but not set)
endif

NPROC := $(shell nproc 2>/dev/null || sysctl -n hw.logicalcpu) ## Workaround since MacOS does not have nproc

help:
	@egrep '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

lint: ## Lint all yaml files for the given INSTANCE
	# Check the yml files have valid syntax and are loadable
	find ./$(INSTANCE)/sections/ -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P $(NPROC) python3 scripts/yaml_check.py
	# Validate the yml files against the schema
	find ./$(INSTANCE)/sections/ -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P $(NPROC) -I {} pykwalify -d '{}' -s ./$(INSTANCE)/schema/.schema.yml
	# Verify that all repositories have at least one revision
	find ./$(INSTANCE)/sections/ -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P $(NPROC) python3 scripts/identify_unpinned.py

fix: ## For the given INSTANCE fix all lockfiles and add the latest revision to every repo that has no revision.
	# Generate the lockfile or update it if it is missing tools. Also add flags for dependency handling.
	find ./$(INSTANCE)/sections/ -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P $(NPROC) python3 scripts/fix_lockfile.py
	# Add the latest revision to every repository that has no revision
	find ./$(INSTANCE)/sections/ -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P $(NPROC) python3 scripts/update_tool.py --without --log debug

update-owner:  ## For the given INSTANCE update all tools that are owned by the OWNER
	find ./$(INSTANCE)/sections/ -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P $(NPROC) python3 scripts/update_tool.py --owner $(OWNER)

update-all: ## For the given INSTANCE update all tools
	find ./$(INSTANCE)/sections/ -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P $(NPROC) python3 scripts/update_tool.py

install: ## For the given INSTANCE install all revisions that are missing
	find ./$(INSTANCE)/sections/ -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P 1 -I {} shed-tools install --toolsfile {} --galaxy $(INSTANCE) --api_key $(GALAXY_API_KEY) --skip_install_resolver_dependencies

.PHONY: fix lint help update-owner update-all install
