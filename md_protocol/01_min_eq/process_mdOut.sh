#!/bin/bash 
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 1
#$ -q gpu
#$ -l gpu_card=1
#$ -N mdOut2KOC_HRM

module load amber

process_mdout.perl ../../../min_eq/min*.out ../../../min_eq/md*.out 
