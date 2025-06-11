.PHONY: all test test-cc test-all lint install run clean

all: lint test install

test:
	python3 -m pytest tests/ -v

test-cc:
	python3 -m pytest tests/ -v -m claude_cli

test-all:
	python3 -m pytest tests/ -v -m ""

lint:
	python3 -m ruff check xontrib/ xoncc/ tests/ --fix
	python3 -m ruff format xontrib/ xoncc/ tests/

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