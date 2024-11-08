#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N min2_1hs3

module load amber/22.0

mpirun -np $NSLOTS $AMBERHOME/bin/sander.MPI -O -i min2.in -o min2.out -p 1hs3.prmtop -c min1.rst -r min2.rst -inf min2.mdinfo -ref min1.rst

