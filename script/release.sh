#!/usr/bin/env bash
set -Eeuo pipefail

# Usage:
#   ./scripts/release.sh --test   # upload to TestPyPI
#   ./scripts/release.sh --prod   # upload to PyPI
# Env:
#   TEST_PYPI_TOKEN, PYPI_TOKEN

here="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$here"

mode="${1:-}"
if [[ "$mode" != "--test" && "$mode" != "--prod" ]]; then
  echo "Usage: $0 --test | --prod"
  exit 1
fi

# Ensure clean git
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "✗ Working tree not clean. Commit or stash changes."
  exit 1
fi

# Ensure required tools
python -m pip install --upgrade pip >/dev/null
python -m pip install --upgrade build twine >/dev/null

# Extract version from pyproject.toml
VERSION="$(python - <<'PY'
import tomllib, sys
with open("pyproject.toml","rb") as f:
    data = tomllib.load(f)
print(data["project"]["version"])
PY
)"
echo "• Releasing version: v${VERSION}"

# Sanity: version matches package __version__
if [[ -f src/yourpkg/__init__.py ]]; then
  PKG_VER="$(python - <<'PY'
import re, pathlib
p = pathlib.Path("src/yourpkg/__init__.py").read_text()
m = re.search(r'__version__\s*=\s*["\\\']([^"\\\']+)["\\\']', p)
print(m.group(1) if m else "")
PY
)"
  if [[ "$PKG_VER" != "$VERSION" ]]; then
    echo "✗ Version mismatch: pyproject=$VERSION, yourpkg.__version__=$PKG_VER"
    exit 1
  fi
fi

# Clean
rm -rf dist build ./*.egg-info

# Build
echo "• Building (sdist + wheel)…"
python -m build

# Check metadata
echo "• Checking archives with twine…"
python -m twine check dist/*

# Upload
if [[ "$mode" == "--test" ]]; then
  : "${TEST_PYPI_TOKEN:?TEST_PYPI_TOKEN not set}"
  echo "• Uploading to TestPyPI…"
  python -m twine upload \
    --repository-url https://test.pypi.org/legacy/ \
    -u __token__ -p "$TEST_PYPI_TOKEN" \
    dist/*
else
  : "${PYPI_TOKEN:?PYPI_TOKEN not set}"
  echo "• Uploading to PyPI…"
  python -m twine upload \
    -u __token__ -p "$PYPI_TOKEN" \
    dist/*
fi

# Tag after successful upload
git tag "v${VERSION}"
git push --tags
echo "✓ Done. Tagged v${VERSION}"
