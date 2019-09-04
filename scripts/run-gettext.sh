#!/bin/bash

set -euo pipefail

# https://stackoverflow.com/a/246128
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

GETTEXT="$SCRIPTDIR/getsentences.py"

CONFIG="$SCRIPTDIR/../config/gettext.sh"

if [ ! -e "$CONFIG" ]; then
    echo "$0:ERROR:missing config file $CONFIG" >&2
    exit 1
fi

source "$CONFIG"

if [[ ! -n $(find "$GETTEXT_INDIR" -maxdepth 1 \
    \( -name '*.conllu' -or -name '*.conllu.gz' \)) ]]; then
    echo "$0:ERROR:no .conllu files found in $GETTEXT_INDIR" >&2
    exit 1
fi

mkdir -p "$GETTEXT_OUTDIR"

for f in $(find "$GETTEXT_INDIR" -maxdepth 1 \
    \( -name '*.conllu' -or -name '*.conllu.gz' \)); do
    b="$(basename "$f" .gz)"
    o="$GETTEXT_OUTDIR/${b%.conllu}"
    if [[ ! "$o" =~ \.txt$ ]]; then
	o="$o.txt"
    fi
    if [ -s "$o" ]; then
    	echo "$0:$o exists, skipping ..." >&2
    else
    	echo "$0:BATCH:$GETTEXT $f $GETTEXT_OPTIONS > $o" >&2
	sbatch "$SCRIPTDIR/runpy3out.sh" "$GETTEXT" "$o" "$f"
    	echo "$0:BATCHED:$GETTEXT $f $GETTEXT_OPTIONS > $o" >&2
    	sleep 10
    fi
done
