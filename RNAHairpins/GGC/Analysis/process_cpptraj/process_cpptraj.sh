#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N hbondsLifetime_ggcFolded


module load amber/22.0

cpptraj -i process_hbondsLifetime.in

# -----------------------------------------
# cpptraj -i process_rmsd.in
# cp rmsd.dat rmsd.txt

# ----------------------------------------
# cpptraj -i process_hbondFrames.in
# cp hbondFrames.dat hbondFrames.txt

#_____________________________________________
# cpptraj -i process_minDist.in
# cp minDist.dat minDist.txt

