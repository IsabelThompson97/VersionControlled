#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N min1_1hs3

module load amber/22.0

mpirun -np $NSLOTS $AMBERHOME/bin/sander.MPI  -O -i min1.in -o min1.out -p 1hs3.prmtop -c 1hs3.rst7 -r min1.rst -inf min1.mdinfo -ref 1hs3.rst7
