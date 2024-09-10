#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N cpptrajProcess_ggcFolded


module load amber/22.0

cd ..

cpptraj -i ./process_cpptraj/process_rmsd.in

cd process_cpptraj
cp rmsd.dat rmsd.txt

# ----------------------------------------
# cpptraj -i ./process_cpptraj/process_hbondframes.in
# cd process_cpptraj
# cp hbonds.dat hbonds.txt

#_____________________________________________
# cpptraj -i ./process_cpptraj/process_minDist.in
# cd process_cpptraj
# cp minDist.dat minDist.txt

