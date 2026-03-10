# Contributing to ContextFusion

Thank you for your interest in contributing to ContextFusion! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code:
- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Respect different viewpoints and experiences

## How to Contribute

### Reporting Bugs

Before creating a bug report:
1. Check if the issue already exists
2. Use the latest version to verify the bug

When reporting bugs, include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Relevant code snippets or logs

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Include:
- Clear description of the enhancement
- Rationale and use cases
- Possible implementation approaches

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure they pass
5. Update documentation as needed
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/context-fusion.git
cd context-fusion

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install with dev dependencies
make install-dev

# Run tests
make test

# Run linting
make lint

# Run type checking
make type-check
```

## Code Style

We use:
- **ruff** for linting and formatting
- **mypy** for type checking
- **pytest** for testing

All code must:
- Pass `make lint`
- Pass `make type-check`
- Have test coverage for new features
- Include docstrings for public APIs

### Pre-commit Hooks

Install pre-commit hooks to automatically check code:

```bash
pre-commit install
```

## Testing

Write tests for new features:
- Unit tests in `tests/`
- Integration tests in `tests/integration/`
- Use pytest fixtures for common setup

Run specific test categories:
```bash
# Unit tests only
pytest tests/ -m "not integration"

# Integration tests
pytest tests/integration/ -v

# With coverage
pytest --cov=context_portfolio_optimizer --cov-report=html
```

## Documentation

- Update README.md for user-facing changes
- Update docs/ for architectural changes
- Use Google-style docstrings
- Include type hints

## Commit Messages

Use clear, descriptive commit messages:
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Reference issues where applicable

Example:
```
Add PDF table extraction support

- Implement table detection in PDFLoader
- Add structured table output format
- Update tests for table extraction

Fixes #123
```

## Release Process

Maintainers will:
1. Update version in `version.py`
2. Update CHANGELOG.md
3. Create a GitHub release
4. Publish to PyPI

## Questions?

- Open a GitHub Discussion for questions
- Join our community chat (coming soon)

Thank you for contributing!
