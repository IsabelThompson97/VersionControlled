#!/bin/bash
#$ -M nkarpins@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N check

module load amber/22.0

mpirun -np $NSLOTS $AMBERHOME/bin/sander.MPI  -O -i min1.in -o min1.out -p final_double_bound.prmtop -c final_double_bound.rst7 -r min1.rst -inf min1.mdinfo -ref final_double_bound.rst7
