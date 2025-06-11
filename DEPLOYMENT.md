# Deployment Guide for xoncc

## Prerequisites (Using PyPI Trusted Publisher - No API Token Needed!)

1. Create a PyPI account at https://pypi.org/account/register/

2. Configure Trusted Publisher on PyPI:
   - Go to https://pypi.org/manage/account/publishing/
   - Add a new pending publisher:
     - Project name: `xoncc`
     - Repository: `akira/xoncc` (or your GitHub username)
     - Workflow: `publish.yml`
     - Environment: (leave blank)

That's it! No API tokens needed.

## How Trusted Publisher Works

PyPI's Trusted Publisher uses OpenID Connect (OIDC) to authenticate GitHub Actions directly. This means:
- No API tokens to manage or rotate
- No secrets to store in GitHub
- More secure than traditional token-based authentication

## Deployment Process

1. Create and push to the `v0.0.1` branch:
   ```bash
   git checkout -b v0.0.1
   git push origin v0.0.1
   ```

2. GitHub Actions will automatically:
   - Run tests on multiple Python versions (3.8-3.12)
   - Run linting with ruff
   - Build the package
   - Publish to PyPI

## Manual Publishing (if needed)

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the package
twine check dist/*

# Upload to PyPI
twine upload dist/*
```

## Version Management

To release a new version:
1. Update version in `pyproject.toml`
2. Create a new branch (e.g., `v0.0.2`)
3. Update the workflow file to trigger on the new branch
4. Push to the new branch