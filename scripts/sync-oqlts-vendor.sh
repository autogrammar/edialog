#!/usr/bin/env bash
# Sync @semcod/oqlts vendor copy from c2004 monorepo (for oqlos/cql standalone checkout).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${OQLTS_SRC:-$ROOT/../../maskservice/c2004/packages/oqlts}"
DEST="$ROOT/vendor/oqlts"
if [[ ! -d "$SRC" ]]; then
  echo "oqlts source not found: $SRC (set OQLTS_SRC)" >&2
  exit 1
fi
rsync -a --delete \
  --exclude node_modules \
  --exclude dist \
  "$SRC/" "$DEST/"
(cd "$DEST" && npm ci && npm run build)
echo "Synced oqlts → $DEST"
