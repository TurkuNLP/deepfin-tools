#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=8:00:00
#SBATCH --mem=8192
#SBATCH --partition=parallel
#SBATCH --output=/homeappl/home/pyysalos/sbatch-out/stdout/%j.txt
#SBATCH --error=/homeappl/home/pyysalos/sbatch-out/stderr/%j.txt

module load python-env/3.5.3

if [ "$#" -lt 4 ]; then
    echo "Usage: $0 SCRIPT MODEL IN OUT [PARAMS]"
    exit 1
fi

script="$1"
model="$2"
infile="$3"
outfile="$4"
shift 4

echo "RUN:$script $model $infile $@ > $outfile"
python3 "$script" "$model" "$infile" $@ > "$outfile"
echo "DONE:$script $model $infile $@ > $outfile"
