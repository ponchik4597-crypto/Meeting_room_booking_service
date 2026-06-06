.PHONY: format lint lint-fix check

format:
	poetry run ruff format .
	poetry run ruff check . --fix

lint:
	poetry run ruff check .

lint-fix:
	poetry run ruff check . --fix

check:
	poetry run ruff format --check .
	poetry run ruff check .
