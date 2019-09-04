#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=72:00:00
#SBATCH --mem=8192
#SBATCH --partition=parallel
#SBATCH --output=/homeappl/home/pyysalos/sbatch-out/stdout/%j.txt
#SBATCH --error=/homeappl/home/pyysalos/sbatch-out/stderr/%j.txt

module load python-env/3.5.3

if [ "$#" -lt 3 ]; then
    echo "Usage: $0 SCRIPT IN OUT [PARAMS]"
    exit 1
fi

script="$1"
infile="$2"
outfile="$3"
shift 3

echo "RUN:$script $infile $@ > $outfile"
python3 "$script" "$infile" $@ > "$outfile"
echo "DONE:$script $infile $@ > $outfile"
