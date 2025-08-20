#!/usr/bin/env bash
# vendorize_pipecat.sh
# Clone repo@ref, copy src/pipecat → src/piopiy (EXCLUDING transport/transports),
# and rewrite code tokens 'pipecat' → 'piopiy' (imports & dotted uses only).

set -euo pipefail

### --- CONFIGURE (or pass as env) ---
REPO_URL="${REPO_URL:-https://github.com/pipecat-ai/pipecat.git}"
REPO_REF="${REPO_REF:-v0.0.80}"                      # tag/branch/SHA
TARGET_PROJECT_DIR="${TARGET_PROJECT_DIR:-$PWD}"     # your project root
SRC_SUBPATH="${SRC_SUBPATH:-src/pipecat}"
DEST_SUBPATH="${DEST_SUBPATH:-src/piopiy}"
# Exclude ALL transport/transports trees anywhere
EXCLUDES="${EXCLUDES:-transport/**,transports/**,**/transport/**,**/transports/**}"
RSYNC_DELETE="${RSYNC_DELETE:-0}"                    # set 1 to mirror
### ----------------------------------

need(){ command -v "$1" >/dev/null 2>&1 || { echo "Missing: $1" >&2; exit 1; }; }
need git; need rsync; need python3

echo "→ Clone $REPO_URL @ $REPO_REF"
TMPDIR="$(mktemp -d)"; trap 'rm -rf "$TMPDIR"' EXIT
if ! git clone --depth 1 --branch "$REPO_REF" "$REPO_URL" "$TMPDIR/repo" 2>/dev/null; then
  git clone "$REPO_URL" "$TMPDIR/repo"
  ( cd "$TMPDIR/repo" && git checkout "$REPO_REF" )
fi
[ -d "$TMPDIR/repo/$SRC_SUBPATH" ] || { echo "Missing $SRC_SUBPATH at $REPO_REF" >&2; exit 1; }

DEST_PATH="$TARGET_PROJECT_DIR/$DEST_SUBPATH"
mkdir -p "$DEST_PATH"

echo "→ Copy $SRC_SUBPATH → $DEST_SUBPATH (excluding transport/transports)"
IFS=',' read -r -a _EX <<< "$EXCLUDES"
RSYNC_ARGS=(-a)
[ "$RSYNC_DELETE" = "1" ] && RSYNC_ARGS+=(--delete)
for pat in "${_EX[@]}"; do RSYNC_ARGS+=(--exclude "$pat"); done
rsync "${RSYNC_ARGS[@]}" "$TMPDIR/repo/$SRC_SUBPATH/" "$DEST_PATH/"

echo "→ Rewrite Python code tokens: pipecat → piopiy (imports & dotted uses only)"
python3 - <<'PY' "$DEST_PATH"
import io, os, sys, tokenize
root = sys.argv[1]

def rewrite(path: str):
    with open(path, 'rb') as f:
        src = f.read()
    try:
        toks = list(tokenize.tokenize(io.BytesIO(src).readline))
    except tokenize.TokenError:
        return False

    out, changed = [], False
    in_import, paren = False, 0

    def end_stmt(tok):
        return tok.type == tokenize.NEWLINE and paren == 0

    i = 0
    while i < len(toks):
        tok = toks[i]
        ttype, tstr = tok.type, tok.string

        if ttype == tokenize.OP:
            if tstr in '([{': paren += 1
            elif tstr in ')]}': paren = max(0, paren - 1)

        if ttype == tokenize.NAME and tstr in ('import','from'):
            in_import = True
        elif end_stmt(tok):
            in_import = False

        if ttype == tokenize.NAME and tstr == 'pipecat':
            # consider dotted use: pipecat.<x>
            j = i + 1
            while j < len(toks) and toks[j].type in (tokenize.NL, tokenize.INDENT, tokenize.DEDENT):
                j += 1
            dotted = j < len(toks) and toks[j].type == tokenize.OP and toks[j].string == '.'
            if in_import or dotted:
                tok = tokenize.TokenInfo(ttype, 'piopiy', tok.start, tok.end, tok.line)
                changed = True

        out.append(tok); i += 1

    if changed:
        new = tokenize.untokenize(out)
        if new != src:
            with open(path, 'wb') as f: f.write(new)
    return changed

count = 0
for dp, _, fns in os.walk(root):
    for fn in fns:
        if fn.endswith(('.py','.pyi')):
            if rewrite(os.path.join(dp, fn)): count += 1
print(f"   …updated {count} file(s)")
PY

echo "✓ Done. Vendored to: $DEST_PATH"
