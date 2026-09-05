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
# OUTSIDE the working tree, so only committed files can reach a distribution.
build:
	rm -rf dist
	@export_dir=$$(mktemp -d) && \
	git archive HEAD | tar -x -C "$$export_dir" && \
	.venv/bin/python -m build --outdir dist "$$export_dir" && \
	rm -rf "$$export_dir"
	@if tar -tzf dist/*.tar.gz | grep -qiE 'claude|gitignore'; then \
		echo "TAINTED SDIST"; exit 1; fi
	@if unzip -l dist/*.whl | grep -qiE 'claude|gitignore'; then \
		echo "TAINTED WHEEL"; exit 1; fi
	@echo "artifacts clean:" && ls dist
