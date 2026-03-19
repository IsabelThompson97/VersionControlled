#!/bin/bash 
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24 
#$ -q long
#$ -N md3_1hs3 

module load amber/22.0

mpirun -np $NSLOTS $AMBERHOME/bin/sander.MPI -O -i md3.in -o md3.out -p 1hs3.prmtop -c md2e.rst -r md3.rst -x md3.nc -ref md2e.rst
