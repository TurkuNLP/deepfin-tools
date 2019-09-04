# Configuration for delexicalized classifier

DATA_ROOT="/wrk/pyysalos/puhti-DeepFin"

DELEX_CONFIGDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

DELEX_MODELDIR="$DELEX_CONFIGDIR/../models"

DELEX_MODEL="$DELEX_MODELDIR/delex-020919"

DELEX_INDIR="$DATA_ROOT/sentfilter_out/nonfiltered"

DELEX_OUT_FILTERED="$DATA_ROOT/delex_out/filtered"

DELEX_OUT_NONFILTERED="$DATA_ROOT/delex_out/nonfiltered"

DELEX_OPTIONS='
--prefix delex_
--delex
--bias 0.5
'
