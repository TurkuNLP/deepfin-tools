# Configuration for heuristic CoNLL-U text filter

FILTER_DATA_ROOT="/wrk/pyysalos/puhti-DeepFin"

FILTER_INDIR="$FILTER_DATA_ROOT/mtgen_out/nongenerated"

FILTER_OUT_FILTERED="$FILTER_DATA_ROOT/filter_out/filtered"

FILTER_OUT_NONFILTERED="$FILTER_DATA_ROOT/filter_out/nonfiltered"

FILTER_OPTIONS='
--min-sents 3
--max-sents 1000
--avg-len 5
--upper-ratio 0.1
--no-word-ratio 0.2
--punct-ratio 0.05
--digit-ratio 0.05
--min-toks 20
--max-toks 10000
--min-words 30
--frequent-ratio 0.02
--foreign-ratio 0.01
--langdetect
'
