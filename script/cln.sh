#!/usr/bin/env bash
set -euo pipefail

# Root to prune (top-level entries only)
SVCROOT="${SVCROOT:-src/piopiy/transports/services}"

# Services to keep (comma-separated, names or single-file services like "telecmi,foo.py")
KEEP_SERVICES="${KEEP_SERVICES:-telecmi}"
# Top-level files to keep (comma-separated)
KEEP_FILES="${KEEP_FILES:-__init__.py}"

# Preserve rules:
#  - Any dir/file that contains a file with one of these extensions will be skipped
PRESERVE_EXTS="${PRESERVE_EXTS:-onnx,onx}"
#  - Extra path globs (relative, shell-style) to search inside a candidate.
#    Example: "vad/data/**,models/**/*.bin"
PRESERVE_GLOBS="${PRESERVE_GLOBS:-}"

# Dry-run (1 = show what would be deleted/skipped; 0 = actually delete)
DRY_RUN="${DRY_RUN:-0}"

[ -d "$SVCROOT" ] || { echo "ERROR: not found: $SVCROOT" >&2; exit 1; }

echo "Pruning in: $SVCROOT"
echo "Keep services: $KEEP_SERVICES"
echo "Keep files   : $KEEP_FILES"
echo "Preserve exts: $PRESERVE_EXTS"
[ -n "$PRESERVE_GLOBS" ] && echo "Preserve globs: $PRESERVE_GLOBS"
[ "$DRY_RUN" = "1" ] && echo "(dry-run mode)"

# Make a regex like "telecmi|janus"
make_regex() {
  # shellcheck disable=SC2001
  echo "$1" | sed -e 's/[[:space:]]//g' -e 's/,/|/g' -e 's/[.[\*^$\\]/\\&/g'
}
KEEP_SV_RE="$(make_regex "$KEEP_SERVICES")"
KEEP_FILES_RE="$(make_regex "$KEEP_FILES")"

contains_preserved_in_dir() {
  # $1 = dir
  d="$1"
  # Check extensions
  oldIFS="$IFS"; IFS=','; for ext in $PRESERVE_EXTS; do IFS="$oldIFS"
    ext="$(printf '%s' "$ext" | tr -d '[:space:]')"
    [ -n "$ext" ] || continue
    if find "$d" -type f -iname "*.$ext" -print -quit 2>/dev/null | grep -q .; then
      return 0
    fi
    IFS=','  # restore for loop
  done
  IFS="$oldIFS"
  # Check extra globs
  if [ -n "$PRESERVE_GLOBS" ]; then
    oldIFS="$IFS"; IFS=','; for g in $PRESERVE_GLOBS; do IFS="$oldIFS"
      g="$(printf '%s' "$g" | tr -d '[:space:]')"
      [ -n "$g" ] || continue
      if find "$d" -type f -path "*/$g" -print -quit 2>/dev/null | grep -q .; then
        return 0
      fi
      IFS=','  # restore for loop
    done
    IFS="$oldIFS"
  fi
  return 1
}

file_is_preserved() {
  # $1 = file path
  p="$1"
  # ext check
  ext="${p##*.}"
  if [ "$ext" != "$p" ]; then
    oldIFS="$IFS"; IFS=','; for e in $PRESERVE_EXTS; do IFS="$oldIFS"
      e="$(printf '%s' "$e" | tr -d '[:space:]')"
      [ -n "$e" ] || continue
      if [ "$ext" = "$e" ]; then return 0; fi
      IFS=','  # restore for loop
    done
    IFS="$oldIFS"
  fi
  # glob check
  if [ -n "$PRESERVE_GLOBS" ]; then
    oldIFS="$IFS"; IFS=','; for g in $PRESERVE_GLOBS; do IFS="$oldIFS"
      g="$(printf '%s' "$g" | tr -d '[:space:]')"
      [ -n "$g" ] || continue
      case "$p" in
        */$g) return 0 ;;
      esac
      IFS=','  # restore for loop
    done
    IFS="$oldIFS"
  fi
  return 1
}

echo "Will delete:"
# Iterate top-level entries (no mapfile, no arrays)
# Use -print0 for safety with spaces; read -d '' works on old bash
find "$SVCROOT" -mindepth 1 -maxdepth 1 -print0 | \
while IFS= read -r -d '' entry; do
  base="$(basename "$entry")"

  # Keep service names (and their ".py" single-file variants)
  if [ -n "$KEEP_SV_RE" ] && echo "$base" | grep -Eq "^($KEEP_SV_RE)(\.py)?$"; then
    continue
  fi
  # Keep explicit top-level files
  if [ -n "$KEEP_FILES_RE" ] && echo "$base" | grep -Eq "^($KEEP_FILES_RE)$"; then
    continue
  fi

  # Preservation checks
  if [ -d "$entry" ]; then
    if contains_preserved_in_dir "$entry"; then
      echo "  SKIP  $entry   (contains preserved files)"
      continue
    fi
  elif [ -f "$entry" ]; then
    if file_is_preserved "$entry"; then
      echo "  SKIP  $entry   (preserved file)"
      continue
    fi
  fi

  echo "  DELETE $entry"
  if [ "$DRY_RUN" != "1" ]; then
    rm -rf -- "$entry"
  fi
done

[ "$DRY_RUN" = "1" ] && echo "Dry-run complete. No changes made." || echo "Done."
