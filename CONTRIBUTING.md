# Contributing to Open Pandas-AI

Thank you for your interest in contributing to Open Pandas-AI! 🎉

## 🤝 How to Contribute

### Reporting Bugs

- Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md)
- Include steps to reproduce the issue
- Provide environment details (OS, Python version, etc.)
- Add screenshots if applicable

### Suggesting Features

- Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md)
- Describe the use case and motivation
- Propose a solution if you have one

### Submitting Pull Requests

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Follow the code style** (see below)
5. **Add tests** for new features
6. **Update documentation** if needed
7. **Commit your changes**:
   ```bash
   git commit -m 'Add some amazing feature'
   ```
8. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```
9. **Open a Pull Request**

## 📝 Code Style

- Follow **PEP 8** style guide
- Use **type hints** where possible
- Add **docstrings** to functions and classes
- Keep functions focused and small
- Use meaningful variable names

### Formatting

We use `black` for code formatting:

```bash
pip install black
black .
```

### Linting

We use `flake8` for linting:

```bash
pip install flake8
flake8 .
```

## 🧪 Testing

- Write tests for new features
- Ensure all tests pass:
  ```bash
  pytest
  ```
- Aim for good test coverage

## 📚 Documentation

- Update README.md if adding new features
- Add docstrings to new functions/classes
- Update TECHNICAL_REPORT.md for architectural changes

## 🔍 Code Review Process

1. All PRs require at least one review
2. Address review comments promptly
3. Keep PRs focused and small when possible
4. Update your PR if requested

## ❓ Questions?

- Open an issue for discussion
- Check existing issues and PRs
- Review the documentation

## 🙏 Thank You!

Your contributions make Open Pandas-AI better for everyone!
