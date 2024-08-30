#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -p smp 24
#$ -q long
#$ -N name_of_job

module load amber/22.0

cpptraj -i file.in