# Configuration for classifier for machine translated/generated texts

MTGEN_DATA_ROOT="/wrk/pyysalos/puhti-DeepFin"

MTGEN_CONFIGDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

MTGEN_MODELDIR="$MTGEN_CONFIGDIR/../models"

MTGEN_MODEL="$MTGEN_MODELDIR/mtgen-220819"

MTGEN_BIAS="-0.5"

MTGEN_INDIR="$MTGEN_DATA_ROOT/source_data/parsed"

MTGEN_OUT_GENERATED="$MTGEN_DATA_ROOT/mtgen_out/generated"

MTGEN_OUT_NONGENERATED="$MTGEN_DATA_ROOT/mtgen_out/nongenerated"
