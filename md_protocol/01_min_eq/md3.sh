#!/bin/bash 
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 48 
#$ -q long
#$ -N fHRMmd3

module load amber/24.0

mpirun -np $NSLOTS $AMBERHOME/bin/sander.MPI -O -i md3.in -o md3.out -p 2KOCFolded_HRM.prmtop -c md2e.rst -r md3.rst -x md3.nc -ref md2e.rst
