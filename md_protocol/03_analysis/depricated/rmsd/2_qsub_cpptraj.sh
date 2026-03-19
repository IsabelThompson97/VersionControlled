#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 1
#$ -q gpu
#$ -l gpu_card=1
#$ -N fDES_RMSDNew

module load amber/22.0

# cpptraj -i 1_rmsdtoNMR1-12.in
# cp rmsd_toNMR1-12.dat rmsd_toNMR1-12.txt

# # # -----------------------------------------
# cpptraj -i 1_rmsd.in
# cp rmsd1-12.dat rmsd1-12.txt

# # # -----------------------------------------
# cpptraj -i 1_rmsdtoNMRBackbone.in
# cp rmsd_toNMRBackbone.dat rmsd_toNMRBackbone.txt

# # # -----------------------------------------
# cpptraj -i 1_rmsdtoNMRStem.in
# cp rmsd_toNMRStem.dat rmsd_toNMRStem.txt

# # # -----------------------------------------
# cpptraj -i 1_rmsdtoNMRLoop.in
# cp rmsd_toNMRLoop.dat rmsd_toNMRLoop.txt

# # -----------------------------------------
cpptraj -i 1_rmsdtoNMR1-12Bases.in
cp rmsd_toNMR1-12Bases.dat rmsd_toNMR1-12Bases.txt
