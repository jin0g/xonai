# xonai Test Structure

## Directory Structure

```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests  
├── interactive/       # Interactive tests
└── conftest.py        # Common test configuration
```

## Test Types

### 🧪 Unit Tests (`tests/unit/`)
Test individual component functionality.

### 🔗 Integration Tests (`tests/integration/`)
Test integrated behavior in xonsh environment.

### 🎯 Interactive Tests (`tests/interactive/`)
Test manual and automated user interaction experiences.

### 🤖 Dummy AI Tests
Set XONAI_DUMMY=1 environment variable to test with dummy implementation without actual AI API.

## Running Tests

```bash
# Run all tests
make test

# Run by category
python3 -m pytest tests/unit/ -v           # Unit tests
python3 -m pytest tests/integration/ -v    # Integration tests
python3 -m pytest tests/interactive/ -v    # Interactive tests
XONAI_DUMMY=1 python3 -m pytest tests/ -v  # Test with dummy AI

# Run manual test
python3 tests/interactive/test_xonai_manual.py
```