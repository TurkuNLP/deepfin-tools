# Configuration for heuristic CoNLL-U text filter

SFILTER_DATA_ROOT="/wrk/pyysalos/puhti-DeepFin"

SFILTER_INDIR="$SFILTER_DATA_ROOT/filter_out/nonfiltered"

SFILTER_OUT_FILTERED="$SFILTER_DATA_ROOT/sentfilter_out/filtered"

SFILTER_OUT_NONFILTERED="$SFILTER_DATA_ROOT/sentfilter_out/nonfiltered"

SFILTER_OPTIONS='
--min-nouns 1
--min-verbs 1
--reject-ratio 0.25
--max-reject 10
--upper-ratio 0.2
--punct-ratio 0.1
--digit-ratio 0.1
--foreign-ratio 0.05
--min-words 2
--max-words 100
--min-toks 3
--max-toks 100
'
