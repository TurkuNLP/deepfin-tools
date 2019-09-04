#!/bin/bash

set -euo pipefail

# https://stackoverflow.com/a/246128
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

CLEANTEXT="$SCRIPTDIR/cleantext.py"

CONFIG="$SCRIPTDIR/../config/cleantext.sh"

if [ ! -e "$CONFIG" ]; then
    echo "$0:ERROR:missing config file $CONFIG" >&2
    exit 1
fi

source "$CONFIG"

if [[ ! -n $(find "$CLEANTEXT_INDIR" -maxdepth 1 \
    \( -name '*.txt' -or -name '*.txt.gz' \)) ]]; then
    echo "$0:ERROR:no .txt files found in $CLEANTEXT_INDIR" >&2
    exit 1
fi

mkdir -p "$CLEANTEXT_OUTDIR"

for f in $(find "$CLEANTEXT_INDIR" -maxdepth 1 \
    \( -name '*.txt' -or -name '*.txt.gz' \)); do
    b="$(basename "$f" .gz)"
    o="$CLEANTEXT_OUTDIR/$b"
    if [ -s "$o" ]; then
    	echo "$0:$o exists, skipping ..." >&2
    else
    	echo "$0:BATCH:$CLEANTEXT $f $CLEANTEXT_OPTIONS > $o" >&2
	sbatch "$SCRIPTDIR/runpy3out.sh" "$CLEANTEXT" "$o" "$f"
    	echo "$0:BATCHED:$CLEANTEXT $f $CLEANTEXT_OPTIONS > $o" >&2
    	sleep 30
    fi
done
