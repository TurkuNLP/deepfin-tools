#!/bin/bash

mkdir -p filtered

FILTER="/homeappl/home/pyysalos/git_checkout/deepfin-tools/scripts/filteruddocs.py"

for f in source_data/parsed/*.conllu.gz; do
    o=filtered/$(basename $f .gz)
    python3 "$FILTER" \
	--min-sents 2 \
	--max-sents 1000 \
	--avg-len 5 \
	--upper-ratio 0.2 \
	--punct-ratio 0.1 \
	--digit-ratio 0.1 \
	--min-toks 15 \
	--max-toks 10000 \
	--min-words 20 \
	--frequent-ratio 0.01 \
	--foreign-ratio 0.025 \
	--langdetect \
	--invert \
	"$f" \
    > "$o"
    
done
