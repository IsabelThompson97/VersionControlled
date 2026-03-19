#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N fHRMmin1

module load amber/24.0

mpirun -np $NSLOTS $AMBERHOME/bin/sander.MPI -O -i min1.in -o min1.out -p 2KOCFolded_HRM.prmtop -c 2KOCFolded_HRM.rst7 -r min1.rst -inf min1.mdinfo -ref 2KOCFolded_HRM.rst7
