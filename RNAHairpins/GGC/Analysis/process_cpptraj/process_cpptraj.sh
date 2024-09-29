#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N radGyrHeavy_folded

module load amber/22.0

cpptraj -i process_radiusGyr.in
cp radGyrHeavyOnly.dat radGyrHeavyOnly.txt

# -----------------------------------------

#cpptraj -i process_hbondsLifetime.in

# -----------------------------------------
# cpptraj -i process_rmsd.in
# cp rmsd.dat rmsd.txt

# ----------------------------------------
# cpptraj -i process_hbondFrames.in
# cp hbondFrames.dat hbondFrames.txt

#_____________________________________________
# cpptraj -i process_minDist.in
# cp minDist.dat minDist.txt

