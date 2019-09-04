#!/bin/bash

set -euo pipefail

# https://stackoverflow.com/a/246128
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

PREDICT="$SCRIPTDIR/predictud.py"

CONFIG="$SCRIPTDIR/../config/delex.sh"

if [ ! -e "$CONFIG" ]; then
    echo "$0:ERROR:missing config file $CONFIG" >&2
    exit 1
fi

source "$CONFIG"

for f in "$DELEX_MODEL".{clf,vecf}; do
    if [ ! -e "$f" ]; then
	echo "$0:ERROR:missing model file $f (not trained?)" >&2
	exit 1
    fi
done

if [[ ! -n $(find "$DELEX_INDIR" -maxdepth 1 \
    \( -name '*.conllu' -or -name '*.conllu.gz' \)) ]]; then
    echo "$0:ERROR:no .conllu files found in $DELEX_INDIR" >&2
    exit 1
fi

mkdir -p "$DELEX_OUT_FILTERED"
mkdir -p "$DELEX_OUT_NONFILTERED"

for f in $(find "$DELEX_INDIR" -maxdepth 1 \
    \( -name '*.conllu' -or -name '*.conllu.gz' \)); do
    # Filtered
    o="$DELEX_OUT_FILTERED/$(basename "$f" .gz)"
    if [ -s "$o" ]; then
    	echo "$0:$o exists, skipping ..." >&2
    else
    	echo "$0:BATCH:$PREDICT --filter pos $f > $o" >&2
    	sbatch "$SCRIPTDIR/rundelex.sh" \
    	    "$PREDICT" "$DELEX_MODEL" "$f" "$o" \
    	    --filter pos \
	    $DELEX_OPTIONS
    	echo "$0:BATCHED:$PREDICT --filter pos $f > $o" >&2
    	sleep 60
    fi
    # Nonfiltered
    o="$DELEX_OUT_NONFILTERED/$(basename "$f" .gz)"
    if [ -s "$o" ]; then
    	echo "$0:$o exists, skipping ..." >&2
    else
    	echo "$0:BATCH:$PREDICT --filter neg $f > $o" >&2
    	sbatch "$SCRIPTDIR/rundelex.sh" \
    	    "$PREDICT" "$DELEX_MODEL" "$f" "$o" \
    	    --filter neg \
	    $DELEX_OPTIONS
    	echo "$0:BATCHED:$PREDICT --filter neg $f > $o" >&2
    	sleep 60
    fi
done
