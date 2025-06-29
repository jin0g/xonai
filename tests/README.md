# xonai Test Documentation

## Overview

xonai test suite ensures reliability across different environments and usage scenarios. Tests are organized by type and dependency requirements to optimize development workflow and CI/CD pipeline performance.

## Test Structure

```
tests/
├── unit/              # Unit tests (no external dependencies)
├── integration/       # Integration tests (require Claude CLI)
├── interactive/       # Interactive tests (manual/automated user scenarios)
├── conftest.py        # Shared test configuration
└── README.md          # This file
```

## Test Categories

### Unit Tests (tests/unit/)

Fast, isolated tests with no external dependencies. All Claude CLI interactions are mocked.

**Scope:**
- Individual component functionality
- Error handling logic
- Response parsing and formatting
- Command filtering and routing
- Subprocess deadlock prevention

**Key Files:**
- `test_handler.py` - Command handling logic
- `test_xontrib.py` - Xontrib loading mechanism
- `test_display.py` - Response formatting
- `test_subprocess_handling.py` - Subprocess management
- `test_xonai_deadlock.py` - Deadlock prevention scenarios
- `test_check_claude.py` - Claude CLI availability checks

**Execution:**
```bash
python -m pytest tests/unit/ -v
python -m pytest tests/unit/ -v --cov=xonai --cov-report=term-missing
```

### Integration Tests (tests/integration/)

Tests that require Claude CLI installation and test actual AI interactions.

**Scope:**
- Real Claude CLI integration
- End-to-end command processing
- Error propagation from Claude CLI
- Complex query handling
- Multi-language support

**Key Files:**
- `test_integration.py` - Basic xonsh integration
- `test_ai_response.py` - AI response handling
- `test_complex_queries.py` - Complex scenarios with real Claude CLI
- `test_mock_claude_integration.py` - Mock Claude CLI integration

**Requirements:**
- Claude CLI installed and authenticated
- Network connectivity for Claude API calls

**Execution:**
```bash
python -m pytest tests/integration/ -v
python -m pytest -m claude_cli -v  # Only Claude CLI dependent tests
```

### Interactive Tests (tests/interactive/)

Manual and automated tests for user interaction scenarios.

**Scope:**
- Shell startup and shutdown
- User experience scenarios
- Signal handling (Ctrl-C, Ctrl-D)
- Real-time interaction patterns
- Cross-platform compatibility

**Key Files:**
- `test_xonai_manual.py` - Manual test procedures
- `test_xonai_real.py` - Automated interactive tests with pexpect
- `test_interactive_simulation.py` - Simulated user interactions
- `test_claude_cli_expect.exp` - Expect script for advanced scenarios

**Requirements:**
- pexpect library (for automated tests)
- expect utility (for .exp scripts)
- Terminal environment

**Execution:**
```bash
python -m pytest tests/interactive/ -v
python tests/interactive/test_xonai_manual.py  # Manual test suite
expect tests/interactive/test_claude_cli_expect.exp  # Expect script
```

## Test Markers

Tests use pytest markers for categorization and selective execution:

- `@pytest.mark.claude_cli` - Requires Claude CLI installation
- `@pytest.mark.integration` - Integration test (may be slow)
- `@pytest.mark.slow` - Long-running test

**Usage:**
```bash
python -m pytest -m "not claude_cli" -v     # Skip Claude CLI tests
python -m pytest -m "claude_cli" -v         # Only Claude CLI tests
python -m pytest -m "not slow" -v           # Skip slow tests
```

## Environment Configuration

### Test Environment Variables

- `XONAI_DUMMY=1` - Use DummyAI instead of Claude CLI for testing
- `PYTEST_CURRENT_TEST` - Set by pytest, used for test isolation

### Dummy AI Testing

Set `XONAI_DUMMY=1` to test with dummy AI implementation:

```bash
XONAI_DUMMY=1 python -m pytest tests/ -v
```

This enables testing without Claude CLI dependency and provides predictable responses for automation.

## Common Test Scenarios

### Testing Command Interception

```python
def test_command_interception():
    """Test that natural language commands are intercepted correctly."""
    # Test implementation checks:
    # 1. Normal commands pass through unchanged
    # 2. Unknown commands trigger AI processing
    # 3. No "command not found" errors displayed
```

### Testing Subprocess Deadlock Prevention

```python
def test_deadlock_prevention():
    """Test large stderr output doesn't cause deadlock."""
    # Test implementation verifies:
    # 1. Background thread handles stderr
    # 2. Large outputs process without hanging
    # 3. Process cleanup occurs properly
```

### Testing Signal Handling

```python
def test_ctrl_c_handling():
    """Test Ctrl-C interruption during AI processing."""
    # Test implementation ensures:
    # 1. Ctrl-C interrupts AI processing
    # 2. Shell remains responsive
    # 3. No process leaks occur
```

## Test Data and Fixtures

### Shared Fixtures (conftest.py)

- `xonsh_executable` - Path to xonsh binary for subprocess tests
- `tmp_path` - Temporary directory for test files
- `mock_claude_response` - Standardized mock responses

### Test Data Patterns

- **English queries:** "how to list files", "create a python script"
- **Japanese queries:** "ファイルを一覧表示する方法", "このプロジェクトの概要"
- **Complex scenarios:** Multi-line queries, large outputs, rapid succession
- **Error conditions:** Network failures, authentication errors, malformed responses

## Test Execution Strategies

### Development Workflow

1. **Pre-commit testing:**
   ```bash
   python -m pytest tests/unit/ -v --cov=xonai --cov-report=term-missing
   ```

2. **Feature development:**
   ```bash
   python -m pytest tests/unit/test_[component].py -v
   ```

3. **Integration verification:**
   ```bash
   XONAI_DUMMY=1 python -m pytest tests/integration/ -v
   ```

### CI/CD Pipeline

1. **Fast feedback (PR validation):**
   ```bash
   python -m pytest tests/unit/ -v --cov=xonai --cov-report=xml
   ```

2. **Full validation (merge to main):**
   ```bash
   python -m pytest tests/ -v -m "not claude_cli"
   ```

### Local Development

1. **Quick verification:**
   ```bash
   make test  # Runs unit tests only
   ```

2. **Full local testing:**
   ```bash
   make test-cc  # Includes Claude CLI tests if available
   ```

## Coverage Requirements

### Minimum Coverage Targets

- **Overall:** 85% line coverage
- **Core modules:** 90% line coverage
  - `xonai/handler.py`
  - `xonai/xontrib.py`
  - `xonai/ai/claude.py`

### Coverage Exclusions

- Platform-specific code branches
- Error handling for rare edge cases
- Debugging and development utilities

### Coverage Reporting

```bash
python -m pytest tests/unit/ --cov=xonai --cov-report=html
open htmlcov/index.html  # View detailed coverage report
```

## Test Performance

### Performance Targets

- **Unit tests:** < 30 seconds total execution
- **Integration tests:** < 2 minutes per test
- **Interactive tests:** < 5 minutes per test

### Performance Optimization

- Mock external dependencies in unit tests
- Use fixtures for common setup operations
- Parallelize independent test execution
- Skip slow tests in development workflow

## Debugging Tests

### Common Debug Scenarios

1. **Test isolation issues:**
   ```bash
   python -m pytest tests/unit/test_handler.py::TestHandler::test_specific -v -s
   ```

2. **Subprocess debugging:**
   ```bash
   python -m pytest tests/integration/test_integration.py -v -s --capture=no
   ```

3. **Mock verification:**
   ```bash
   python -m pytest tests/unit/ -v --pdb  # Drop into debugger on failure
   ```

### Test Output Analysis

- **stdout/stderr capture:** Use `-s` flag to see print statements
- **Detailed assertions:** Tests include contextual error messages
- **Log integration:** Tests respect logging configuration

## Test Maintenance

### Adding New Tests

1. **Identify test category:** Unit, integration, or interactive
2. **Choose appropriate fixtures:** Use shared fixtures when possible
3. **Follow naming conventions:** `test_[component]_[scenario].py`
4. **Add appropriate markers:** Mark dependencies clearly
5. **Update documentation:** Add to relevant test category documentation

### Updating Existing Tests

1. **Verify compatibility:** Ensure changes don't break existing functionality
2. **Update fixtures:** Modify shared fixtures if needed
3. **Check coverage impact:** Maintain or improve coverage levels
4. **Review performance:** Ensure tests remain fast and reliable

### Test Cleanup

- Remove obsolete tests when functionality is removed
- Consolidate duplicate test logic
- Update test data when APIs change
- Refresh mock data to match current behavior

## Troubleshooting

### Common Test Failures

1. **"Claude CLI not found":**
   - Install Claude CLI or use `XONAI_DUMMY=1`
   - Check PATH environment variable

2. **"xonsh not available":**
   - Install xonsh: `pip install xonsh`
   - Verify xonsh is in PATH

3. **Subprocess timeout:**
   - Increase timeout values in test configuration
   - Check for deadlock scenarios

4. **Import errors:**
   - Verify test environment has all dependencies
   - Check PYTHONPATH includes project root

### Platform-Specific Issues

1. **Windows:**
   - Path separator differences in test assertions
   - Signal handling variations

2. **macOS:**
   - Terminal permissions for interactive tests
   - Security restrictions on subprocess execution

3. **Linux:**
   - Distribution-specific package differences
   - Container environment limitations

### Test Environment Reset

```bash
# Clean test environment
rm -rf .pytest_cache/
rm -rf htmlcov/
rm -rf .coverage

# Reset virtual environment
deactivate
rm -rf venv/
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```