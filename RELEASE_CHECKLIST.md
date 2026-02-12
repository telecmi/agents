# Release Checklist for v0.0.6

## Pre-Release Verification

### ✅ Code Quality
- [x] Version updated to 0.0.6 in `pyproject.toml`
- [x] CHANGELOG.md created with all changes documented
- [x] All examples tested and working
- [x] No syntax errors in any files
- [x] Import statements verified

### ✅ Documentation
- [x] README.md enhanced with provider showcase
- [x] PARAMETERS.md created with complete reference
- [x] GETTING_STARTED.md available
- [x] API_REFERENCE.md available
- [x] DEVELOPER_GUIDE.md available
- [x] All provider READMEs created (STT, LLM, TTS)

### ✅ Examples
- [x] 8 STT provider examples
- [x] 13 LLM provider examples
- [x] 17 TTS provider examples
- [x] 2 combined stack examples
- [x] Basic example with full parameter documentation
- [x] MCP sales example
- [x] Murf.ai example

### ✅ Package Metadata
- [x] PyPI classifiers added
- [x] Keywords expanded for better discoverability
- [x] License file included
- [x] README.md set as long description

## Build & Test

### Local Testing
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build

# Test installation locally
pip install dist/piopiy_ai-0.0.6-py3-none-any.whl

# Verify imports
python -c "from piopiy.agent import Agent; print('✅ Import successful')"

# Run basic example
python example/basic/basic.py
```

### Test PyPI (Optional)
```bash
# Upload to Test PyPI first
python -m twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ piopiy-ai==0.0.6
```

## Release to PyPI

### Build Package
```bash
# Ensure build tools are installed
pip install --upgrade build twine

# Build distribution packages
python -m build
```

### Upload to PyPI
```bash
# Upload to PyPI
python -m twine upload dist/*

# You'll be prompted for:
# - Username: __token__
# - Password: <your-pypi-token>
```

### Verify Release
```bash
# Wait a few minutes, then install from PyPI
pip install piopiy-ai==0.0.6

# Verify installation
python -c "from piopiy.agent import Agent; print('✅ PyPI release successful')"
```

## Post-Release

### Git Tagging
```bash
# Create and push git tag
git tag -a v0.0.6 -m "Release v0.0.6 - 40+ provider examples"
git push origin v0.0.6
```

### GitHub Release
1. Go to https://github.com/telecmi/agents/releases
2. Click "Draft a new release"
3. Select tag: v0.0.6
4. Title: "v0.0.6 - Comprehensive Provider Examples"
5. Copy content from CHANGELOG.md
6. Publish release

### Announce
- [ ] Update documentation website (if applicable)
- [ ] Post on social media/blog
- [ ] Notify users of new features

## Rollback Plan

If issues are discovered:
```bash
# Yank the release from PyPI (doesn't delete, just hides)
pip install --upgrade twine
twine upload --repository pypi --skip-existing dist/*
# Then use PyPI web interface to yank the version
```

## Notes

- **Version**: 0.0.6
- **Release Date**: 2026-02-12
- **Major Changes**: 40+ provider examples, comprehensive documentation
- **Breaking Changes**: None
- **Migration Guide**: Not needed
