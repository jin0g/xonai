.PHONY: all test test-interactive lint install run clean

all: lint test install

test:
	@echo "Running all tests with dummy Claude CLI..."
	python3 -m pytest tests/ -v

test-interactive:
	@echo "Running interactive tests with expect..."
	@if command -v expect >/dev/null 2>&1; then \
		echo "Running basic interactive test..."; \
		./tests/test_interactive_expect.exp; \
		echo "Running advanced Claude CLI interactive test..."; \
		./tests/test_claude_cli_expect.exp; \
	else \
		echo "expect command not found. Install with: brew install expect (macOS) or apt-get install expect (Linux)"; \
		exit 1; \
	fi

lint:
	python3 -m ruff check xontrib/ xoncc/ tests/ --fix
	python3 -m ruff format xontrib/ xoncc/ tests/
	python3 -m mypy xontrib/ xoncc/ --ignore-missing-imports

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