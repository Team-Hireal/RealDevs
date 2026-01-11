# Contributing to RealDevs

Thank you for your interest in contributing to RealDevs! This document provides guidelines for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/RealDevs.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit: `git commit -m "Add feature: description"`
7. Push: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

See [README.md](../README.md) for setup instructions.

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints where possible
- Maximum line length: 120 characters
- Use meaningful variable names
- Add docstrings to functions and classes

### TypeScript (Frontend)
- Use TypeScript strict mode
- Follow Prettier formatting
- Use meaningful component and variable names
- Add JSDoc comments for complex functions

## Testing

### Backend Tests
```bash
cd apps/api
pytest
```

### Frontend Tests
```bash
cd apps/web
npm test
```

## Pull Request Guidelines

1. **Description**: Clearly describe what your PR does
2. **Issue Reference**: Link to related issues
3. **Tests**: Add tests for new features
4. **Documentation**: Update docs if needed
5. **Small PRs**: Keep changes focused and atomic

## Reporting Bugs

Open an issue with:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, versions)
- Screenshots if applicable

## Feature Requests

We welcome feature requests! Please:
- Search existing issues first
- Clearly describe the feature and use case
- Explain why it would be valuable

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the project's values of transparency and privacy

## Questions?

Open a GitHub Discussion or reach out to maintainers.

Thank you for contributing! 🎉

