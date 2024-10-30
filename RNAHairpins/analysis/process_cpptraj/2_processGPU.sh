#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 1
#$ -q gpu
#$ -l gpu_card=1
#$ -N UnfoldedRMSDFolded

module load amber/22.0

cpptraj -i process_rmsd.in
cp rmsd_toFolded.dat rmsd_toFolded.txt
