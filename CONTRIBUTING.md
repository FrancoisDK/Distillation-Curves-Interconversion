# Contributing to Distillation Curves Interconversion

Welcome! We're excited you want to contribute. Here's how to get involved.

## Getting Started

### 1. Fork & Clone
```bash
git clone https://github.com/YOUR_USERNAME/Distillation-Curves-Interconversion.git
cd Distillation-Curves-Interconversion
```

### 2. Set Up Development Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

pip install -e ".[dev]"
pip install pytest pytest-cov
```

### 3. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

## Development Guidelines

### Code Style
- **Python 3.12+** required
- Follow PEP 8
- Use type hints where practical
- Max line length: 100 characters

### Testing

**Run all tests:**
```bash
pytest tests/ -v
```

**Run with coverage:**
```bash
pytest tests/ --cov=. --cov-report=html
```

**Run specific test:**
```bash
pytest tests/test_bp_conversions.py::TestConversionPhysics::test_d86_less_than_d2887 -v
```

### Writing Tests
- Put new tests in `tests/test_*.py`
- Follow naming: `Test*` for classes, `test_*` for methods
- Include docstrings explaining what's tested
- Test both happy path and edge cases

**Example:**
```python
def test_my_feature(self):
    """Test that my feature does X correctly"""
    result = my_function(input_data)
    assert result == expected_value
```

## Areas for Contribution

### 🐛 Bug Fixes
- Check [Issues](https://github.com/FrancoisDK/Distillation-Curves-Interconversion/issues)
- Write test case first (reproduces bug)
- Fix the bug
- Verify test passes

### ✨ Features
- D86/D2887/TBP extensions
- Additional property calculations
- New conversion methods
- Performance improvements

### 📚 Documentation
- Improve README clarity
- Add more examples
- Technical deep-dives
- Troubleshooting guides

### 🧪 Testing
- Add edge case tests
- Performance benchmarks
- Validation against published data
- Cross-platform testing

## Pull Request Process

1. **Update tests**: Add or modify tests for your changes
2. **Run tests locally**: Ensure all pass (`pytest tests/ -v`)
3. **Update docs**: Document new features or API changes
4. **Keep commits clean**: Logical, descriptive commit messages
5. **Push to your fork**
6. **Create PR**: Link any related issues

### PR Description Template
```markdown
## Description
Brief explanation of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Performance improvement

## Testing
- [ ] Added/updated tests
- [ ] All tests pass locally
- [ ] Tested on Windows/Mac/Linux (if applicable)

## Related Issues
Fixes #123

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes
```

## Code Review Expectations

We may ask for changes:
- **Tests**: All changes need tests
- **Documentation**: Document public APIs
- **Performance**: No regressions
- **Compatibility**: Works on Python 3.12+

## Reporting Bugs

Create an [Issue](https://github.com/FrancoisDK/Distillation-Curves-Interconversion/issues/new) with:

```markdown
**Describe the bug:**
A clear description of what went wrong

**To reproduce:**
Steps to reproduce the issue

**Expected behavior:**
What should have happened

**Actual behavior:**
What actually happened

**Environment:**
- Python version
- OS (Windows/Mac/Linux)
- Installed via: pip/source

**Sample data:**
If applicable, minimal example that triggers the bug
```

## Questions?

- 📖 Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for API details
- 🏗️ Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- 💬 Open a [Discussion](https://github.com/FrancoisDK/Distillation-Curves-Interconversion/discussions)

## Development Roadmap

See [GitHub Projects](https://github.com/FrancoisDK/Distillation-Curves-Interconversion/projects) for planned features and priorities.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing! 🎉**
