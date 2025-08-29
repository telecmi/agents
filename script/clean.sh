#!/usr/bin/env bash
set -euo pipefail

# CHANGE THIS if your path is different:
SVCROOT="${SVCROOT:-src/piopiy/transports/services}"

# Services/files to keep:
KEEP_SERVICES="${KEEP_SERVICES:-telecmi}"
KEEP_FILES="${KEEP_FILES:-__init__.py}"

[[ -d "$SVCROOT" ]] || { echo "ERROR: not found: $SVCROOT"; exit 1; }

echo "Pruning in: $SVCROOT"
echo "Keeping services: $KEEP_SERVICES ; keeping files: $KEEP_FILES"

# Build multiple ! -name clauses for find (portable across macOS/Linux)
args=( -mindepth 1 -maxdepth 1 )
IFS=',' read -r -a svcs <<< "$KEEP_SERVICES"
for s in "${svcs[@]}"; do
  s="${s// /}"
  args+=( ! -name "$s" ! -name "$s.py" )
done
IFS=',' read -r -a keepf <<< "$KEEP_FILES"
for f in "${keepf[@]}"; do
  f="${f// /}"
  args+=( ! -name "$f" )
done

# Show and delete
echo "Will delete:"
find "$SVCROOT" "${args[@]}" -print
find "$SVCROOT" "${args[@]}" -exec rm -rf {} +

echo "Done."
