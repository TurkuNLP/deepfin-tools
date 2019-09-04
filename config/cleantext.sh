# Configuration for text extraction from CoNLL-U

DATA_ROOT="/wrk/pyysalos/puhti-DeepFin"

CLEANTEXT_INDIR="$DATA_ROOT/extracted_texts"

CLEANTEXT_OUTDIR="$DATA_ROOT/extracted_texts_cleaned"

CLEANTEXT_OPTIONS='
--fix-text
--min-words 2
'
