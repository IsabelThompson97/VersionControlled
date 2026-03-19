#!/bin/bash 
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 1
#$ -q gpu
#$ -l gpu_card=1
#$ -N fHRMmd3

module load amber/24.0

$AMBERHOME/bin/pmemd.cuda -O -i md3.in -o md3.out -p 2KOCFolded_HRM.prmtop -c md2e.rst -r md3.rst -x md3.nc -ref md2e.rst
