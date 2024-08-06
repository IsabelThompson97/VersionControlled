#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N min1check

module load amber/22.0

mpirun -np $NSLOTS $AMBERHOME/bin/sander.MPI  -O -i min1.in -o min1.out -p ggc.prmtop -c ggc.rst7 -r min1.rst -inf min1.mdinfo -ref ggc.rst7
