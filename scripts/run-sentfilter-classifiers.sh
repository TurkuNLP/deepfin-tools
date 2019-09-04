#!/bin/bash

set -euo pipefail

# https://stackoverflow.com/a/246128
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

SFILTER="$SCRIPTDIR/filterudsents.py"

CONFIG="$SCRIPTDIR/../config/sentfilter.sh"

if [ ! -e "$CONFIG" ]; then
    echo "$0:ERROR:missing config file $CONFIG" >&2
    exit 1
fi

source "$CONFIG"

if [[ ! -n $(find "$SFILTER_INDIR" -maxdepth 1 \
    \( -name '*.conllu' -or -name '*.conllu.gz' \)) ]]; then
    echo "$0:ERROR:no .conllu files found in $SFILTER_INDIR" >&2
    exit 1
fi

mkdir -p "$SFILTER_OUT_FILTERED"
mkdir -p "$SFILTER_OUT_NONFILTERED"

for f in $(find "$SFILTER_INDIR" -maxdepth 1 \
    \( -name '*.conllu' -or -name '*.conllu.gz' \)); do
    # Filtered
    o="$SFILTER_OUT_FILTERED/$(basename "$f" .gz)"
    if [ -s "$o" ]; then
    	echo "$0:$o exists, skipping ..." >&2
    else
    	echo "$0:BATCH:$SFILTER $f --invert $SFILTER_OPTIONS > $o" >&2
    	sbatch "$SCRIPTDIR/runfilter.sh" \
    	    "$SFILTER" "$f" "$o" \
	    --invert \
	    $SFILTER_OPTIONS
    	echo "$0:BATCHED:$SFILTER $f --invert $SFILTER_OPTIONS > $o" >&2
    	sleep 60
    fi
    # # Nonfiltered
    o="$SFILTER_OUT_NONFILTERED/$(basename "$f" .gz)"
    if [ -s "$o" ]; then
    	echo "$0:$o exists, skipping ..." >&2
    else
    	echo "$0:BATCH:$SFILTER $f $SFILTER_OPTIONS > $o" >&2
    	sbatch "$SCRIPTDIR/runfilter.sh" \
    	    "$SFILTER" "$f" "$o" \
	    $SFILTER_OPTIONS
    	echo "$0:BATCHED:$SFILTER $f $SFILTER_OPTIONS > $o" >&2
    	sleep 60
    fi
done
