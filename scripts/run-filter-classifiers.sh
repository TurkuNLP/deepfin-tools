#!/bin/bash

set -euo pipefail

# https://stackoverflow.com/a/246128
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

FILTER="$SCRIPTDIR/filteruddocs.py"

CONFIG="$SCRIPTDIR/../config/filter.sh"

if [ ! -e "$CONFIG" ]; then
    echo "$0:ERROR:missing config file $CONFIG" >&2
    exit 1
fi

source "$CONFIG"

if [[ ! -n $(find "$FILTER_INDIR" -maxdepth 1 \
    \( -name '*.conllu' -or -name '*.conllu.gz' \)) ]]; then
    echo "$0:ERROR:no .conllu files found in $FILTER_INDIR" >&2
    exit 1
fi

mkdir -p "$FILTER_OUT_FILTERED"
mkdir -p "$FILTER_OUT_NONFILTERED"

for f in $(find "$FILTER_INDIR" -maxdepth 1 \
    \( -name '*.conllu' -or -name '*.conllu.gz' \)); do
    # Filtered
    o="$FILTER_OUT_FILTERED/$(basename "$f" .gz)"
    if [ -s "$o" ]; then
    	echo "$0:$o exists, skipping ..." >&2
    else
    	echo "$0:BATCH:$FILTER $f --invert $FILTER_OPTIONS > $o" >&2
    	sbatch "$SCRIPTDIR/runfilter.sh" \
    	    "$FILTER" "$f" "$o" \
	    --invert \
	    $FILTER_OPTIONS
    	echo "$0:BATCHED:$FILTER $f --invert $FILTER_OPTIONS > $o" >&2
    	sleep 60
    fi
    # # Nonfiltered
    o="$FILTER_OUT_NONFILTERED/$(basename "$f" .gz)"
    if [ -s "$o" ]; then
    	echo "$0:$o exists, skipping ..." >&2
    else
    	echo "$0:BATCH:$FILTER $f $FILTER_OPTIONS > $o" >&2
    	sbatch "$SCRIPTDIR/runfilter.sh" \
    	    "$FILTER" "$f" "$o" \
	    $FILTER_OPTIONS
    	echo "$0:BATCHED:$FILTER $f $FILTER_OPTIONS > $o" >&2
    	sleep 60
    fi
done
