#!/bin/bash 
#$ -M nkarpins@nd.edu
#$ -m abe
#$ -pe smp 24 
#$ -q long
#$ -N admy-dna1check 

module load amber/22.0

mpirun -np $NSLOTS $AMBERHOME/bin/sander.MPI -O -i md1.in -o md1.out -p final_double_bound.prmtop -c min2.rst -r md1.rst -x md1.nc -ref min2.rst

