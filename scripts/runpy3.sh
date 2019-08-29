#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --mem=8192
#SBATCH --partition=parallel
#SBATCH --output=/homeappl/home/pyysalos/sbatch-out/stdout/%j.txt
#SBATCH --error=/homeappl/home/pyysalos/sbatch-out/stderr/%j.txt

module load python-env/3.5.3

python3 $@
