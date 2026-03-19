#!/bin/bash 
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 1
#$ -q gpu
#$ -l gpu_card=1
#$ -N fHRMmd4

module load amber/24.0

$AMBERHOME/bin/pmemd.cuda -O -i md4.in -o md4.out -p 2KOCFolded_HRM.prmtop -c md3_NewVolume.rst -r md4.rst -x md4.nc -ref md3.rst
