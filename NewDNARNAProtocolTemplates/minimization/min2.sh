#!/bin/bash
#$ -M nkarpins@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N min2check

module load amber/22.0

mpirun -np $NSLOTS $AMBERHOME/bin/sander.MPI -O -i min2.in -o min2.out -p final_double_bound.prmtop -c min1.rst -r min2.rst -inf min2.mdinfo -ref min1.rst

