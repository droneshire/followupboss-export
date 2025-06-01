PYTHON ?= python
PIP ?= pip
MAYBE_UV = uv
PIP_COMPILE = $(if $(MAYBE_UV),pip compile,uv pip-compile)

# Core paths
CSV_DIR=$(PWD)/csv
SOURCE_PATH=$(PWD)/src
PACKAGES_PATH=$(PWD)/packages
PY_VENV=$(PWD)/venv
PYTHON_VERSION=$(shell $(PYTHON) -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}');")
PY_SITE_PACKAGES=$(PY_VENV)/lib/python$(PYTHON_VERSION)/site-packages
PY_PATH=$(SOURCE_PATH)

RUN_PY_DIRECT = PYTHONPATH=$(PY_PATH) $(PYTHON) -m
RUN_PY= $(RUN_PY_DIRECT)

# NOTE: exclude any virtual environment subdirectories here
PY_VENV_REL_PATH=$(subst $(PWD)/,,$(PY_VENV))
PY_FIND_COMMAND = find . -name '*.py' | grep -vE "($(PY_VENV_REL_PATH))"

BLACK_CMD = $(RUN_PY_DIRECT) black --line-length 100 $(shell $(PY_FIND_COMMAND))

create_dirs:
	mkdir -p $(CSV_DIR)

init: create_dirs
	@if [ -d "$(PY_VENV_REL_PATH)" ]; then \
		echo "\033[33mVirtual environment already exists\033[0m"; \
	else \
		$(PYTHON) -m venv $(PY_VENV_REL_PATH); \
	fi
	@echo "\033[0;32mRun 'source $(PY_VENV_REL_PATH)/bin/activate' to activate the virtual environment\033[0m"

install:
	$(PIP) install --upgrade pip
	$(PIP) install pip-tools uv
	$(MAYBE_UV) $(PIP_COMPILE) --strip-extras --output-file=$(PACKAGES_PATH)/requirements.txt $(PACKAGES_PATH)/requirements.in
	$(MAYBE_UV) $(PIP) install $(INSTALL_SYSTEM_ARGS) -r $(PACKAGES_PATH)/requirements.txt


format: isort
	$(RUN_PY_DIRECT) ruff check --fix $(shell $(PY_FIND_COMMAND))

check_format:
	$(RUN_PY_DIRECT) ruff check --diff $(shell $(PY_FIND_COMMAND))

mypy:
	$(RUN_PY_DIRECT) mypy $(shell $(PY_FIND_COMMAND))

pylint:
	$(RUN_PY_DIRECT) pylint $(shell $(PY_FIND_COMMAND))

autopep8:
	autopep8 --in-place --aggressive --aggressive $(shell $(PY_FIND_COMMAND))

isort:
	isort $(shell $(PY_FIND_COMMAND))

lint: check_format mypy

lint_full: check_format mypy pylint

upgrade: install
	pip install --upgrade $$(pip freeze | awk '{split($$0, a, "=="); print a[1]}')
	pip freeze > $(PACKAGES_PATH)/requirements.txt

clean:
	rm -rf $(PY_VENV)
	rm -rf .ruff_cache
	rm -rf .mypy_cache

### Scripts
export_people:
	$(RUN_PY_DIRECT) src.executables.export_people $(ARGS)

.PHONY: create_dirs init install install_requirements format check_format mypy pylint autopep8 isort lint lint_full upgrade clean
.PHONY: export_people
# End Makefile