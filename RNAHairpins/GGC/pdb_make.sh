#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N  md9_makepdb

module load amber/22.0

cpptraj -i pdb_make.in
