#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N  pdbmodel_makepdb

module load amber/22.0

cpptraj -i pmakePDB.in