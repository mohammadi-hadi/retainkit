.PHONY: install lint test demo results locomo build

install:
	python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"

lint:
	.venv/bin/ruff check src tests examples
	.venv/bin/ruff format --check src tests examples
	.venv/bin/mypy src

test:
	.venv/bin/python -m pytest -q

demo:
	.venv/bin/retainkit demo --out results

results: demo

locomo:
	.venv/bin/python examples/locomo/fetch_data.py
	.venv/bin/python examples/locomo/run_locomo.py

# Build sdist + wheel from a clean `git archive` export in a temp directory
# OUTSIDE the working tree: hatchling walks upward looking for ignore files and
# would otherwise pick up local ones. Only committed files can reach a
# distribution, and the artifacts are then checked for stray hidden files.
build:
	rm -rf dist
	@export_dir=$$(mktemp -d) && \
	git archive HEAD | tar -x -C "$$export_dir" && \
	.venv/bin/python -m build --outdir dist "$$export_dir" && \
	rm -rf "$$export_dir"
	@if tar -tzf dist/*.tar.gz | grep -E '/\.' | grep -vE '/\.(github/|zenodo\.json$$)' ; then \
		echo "unexpected hidden files reached the sdist"; exit 1; fi
	@if unzip -Z1 dist/*.whl | grep -E '(^|/)\.' ; then \
		echo "unexpected hidden files reached the wheel"; exit 1; fi
	@echo "artifacts clean:" && ls dist
