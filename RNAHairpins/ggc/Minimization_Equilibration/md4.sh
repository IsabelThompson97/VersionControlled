#!/bin/bash 
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24 
#$ -q long
#$ -N md4_GGCcheck

module load amber/22.0

mpirun -np $NSLOTS $AMBERHOME/bin/sander.MPI -O -i md4.in -o md4.out -p ggc.prmtop -c md3_NewVolume.rst -r md4.rst -x md4.nc -ref md3.rst
