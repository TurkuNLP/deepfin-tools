#!/bin/bash

set -euo pipefail

# https://stackoverflow.com/a/246128
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

PREDICT="$SCRIPTDIR/predictud.py"

CONFIG="$SCRIPTDIR/../config/mtgen.sh"

if [ ! -e "$CONFIG" ]; then
    echo "$0:ERROR:missing config file $CONFIG" >&2
    exit 1
fi

source "$CONFIG"

for f in "$MTGEN_MODEL".{clf,vecf}; do
    if [ ! -e "$f" ]; then
	echo "$0:ERROR:missing model file $f (not trained?)" >&2
	exit 1
    fi
done

if [[ ! -n $(find "$MTGEN_INDIR" -maxdepth 1 \
    \( -name '*.conllu' -or -name '*.conllu.gz' \)) ]]; then
    echo "$0:ERROR:no .conllu files found in $MTGEN_INDIR" >&2
    exit 1
fi

mkdir -p "$MTGEN_OUT_GENERATED"
mkdir -p "$MTGEN_OUT_NONGENERATED"

for f in $(find "$MTGEN_INDIR" -maxdepth 1 \
    \( -name '*.conllu' -or -name '*.conllu.gz' \)); do
    # Generated
    o="$MTGEN_OUT_GENERATED/$(basename "$f" .gz)"
    if [ -s "$o" ]; then
    	echo "$0:$o exists, skipping ..." >&2
    else
    	echo "$0:BATCH:$PREDICT -f Nongenerated $f > $o" >&2
    	sbatch "$SCRIPTDIR/runmtgen.sh" \
    	    "$PREDICT" "$MTGEN_MODEL" "$f" "$o" \
    	    -f Nongenerated \
    	    -t -b "$MTGEN_BIAS"
    	echo "$0:BATCHED:$PREDICT -f Nongenerated $f > $o" >&2
    	sleep 60
    fi
    # Nongenerated
    o="$MTGEN_OUT_NONGENERATED/$(basename "$f" .gz)"
    if [ -s "$o" ]; then
    	echo "$0:$o exists, skipping ..." >&2
    else
    	echo "$0:BATCH:$PREDICT -f Generated $f > $o" >&2
    	sbatch "$SCRIPTDIR/runmtgen.sh" \
    	    "$PREDICT" "$MTGEN_MODEL" "$f" "$o" \
    	    -f Generated \
    	    -t -b "$MTGEN_BIAS"
    	echo "$0:BATCHED:$PREDICT -f Generated $f > $o" >&2
    	sleep 60
    fi
done
