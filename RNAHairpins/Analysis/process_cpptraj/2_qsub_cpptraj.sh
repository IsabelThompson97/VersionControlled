#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N UnfoldedRMSDFolded2

module load amber/22.0

# cpptraj -i 1_radiusGyr.in
# cp radGyr.dat radGyr.txt

# -----------------------------------------

# cpptraj -i 1_hbondsLifetime.in

# -----------------------------------------
cpptraj -i 1_rmsdtoFolded.in
cp rmsd_toFolded.dat rmsd_toFolded.txt

# -----------------------------------------
# cpptraj -i 1_rmsd.in
# cp rmsd.dat rmsd.txt

# ----------------------------------------
# cpptraj -i 1_hbondFrames.in
# cp hbondFrames.dat hbondFrames.txt

#_____________________________________________
# cpptraj -i 1_minDist.in
# cp minDistRiboseO.dat minDistRiboseO.txt

