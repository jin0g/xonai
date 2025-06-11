.PHONY: all test lint install run clean

all: lint test install

test:
	@echo "Running all tests..."
	python3 -m pytest tests/ -v
	@echo ""
	@echo "Running interactive tests with expect..."
	@if command -v expect >/dev/null 2>&1; then \
		echo "Running basic interactive test..."; \
		./tests/interactive/test_interactive_expect.exp; \
		echo "Running advanced Claude CLI interactive test..."; \
		./tests/interactive/test_claude_cli_expect.exp; \
	else \
		echo "expect command not found. Skipping interactive tests."; \
		echo "To run interactive tests, install expect with: brew install expect (macOS) or apt-get install expect (Linux)"; \
	fi

lint:
	python3 -m ruff check xoncc/ tests/ --fix
	python3 -m ruff format xoncc/ tests/
	python3 -m mypy xoncc/ --ignore-missing-imports

install:
	pip3 install --user .

run: install
	xoncc

hello:
	echo "Hello World!"

clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete