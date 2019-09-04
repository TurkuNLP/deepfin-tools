#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=6:00:00
#SBATCH --mem=8192
#SBATCH --partition=parallel
#SBATCH --output=/homeappl/home/pyysalos/sbatch-out/stdout/%j.txt
#SBATCH --error=/homeappl/home/pyysalos/sbatch-out/stderr/%j.txt

module load python-env/3.5.3

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 SCRIPT OUT [PARAMS]"
    exit 1
fi

script="$1"
outfile="$2"
shift 2

python3 "$script" $@ > "$outfile"
