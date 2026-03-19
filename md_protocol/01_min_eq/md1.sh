#!/bin/bash 
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 48 
#$ -q long
#$ -N fHRMmd1

module load amber/24.0

mpirun -np $NSLOTS $AMBERHOME/bin/sander.MPI -O -i md1.in -o md1.out -p 2KOCFolded_HRM.prmtop -c min2.rst -r md1.rst -x md1.nc -ref min2.rst

