#!/bin/bash 
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 48 
#$ -q long
#$ -N fHRMmd4

module load amber/24.0

mpirun -np $NSLOTS $AMBERHOME/bin/sander.MPI -O -i md4.in -o md4.out -p 2KOCFolded_HRM.prmtop -c md3_NewVolume.rst -r md4.rst -x md4.nc -ref md3.rst
