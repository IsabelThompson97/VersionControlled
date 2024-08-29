#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N rmsd_ggcfolded

module load amber/22.0

cpptraj -i process_rmsd.in
