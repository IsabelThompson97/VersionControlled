#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 1
#$ -q gpu
#$ -l gpu_card=1
#$ -N cpptraj_unfolded1hs3

module load amber/22.0

cpptraj -i 1_radiusGyr.in
cp radGyr.dat radGyr.txt

# -----------------------------------------

cpptraj -i 1_hbondsLifetime.in

# -----------------------------------------
cpptraj -i 1_rmsdtoCrystal.in
cp rmsd_toCrystal.dat rmsd_toCrystal.txt

# # -----------------------------------------
cpptraj -i 1_rmsd.in
cp rmsd.dat rmsd.txt

# # ----------------------------------------
cpptraj -i 1_hbondFrames.in
cp hbondFrames.dat hbondFrames.txt

# #_____________________________________________
cpptraj -i 1_minDist.in
cp minDist.dat minDist.txt

#_____________________________________________
cpptraj -i 1_minDistRibose.in
cp minDistRiboseO.dat minDistRiboseO.txt

#_____________________________________________
cpptraj -i 1_minDistNucleotide.in
cp minDistNucleotideO.dat minDistNucleotideO.txt

