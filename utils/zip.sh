#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 4
#$ -q gpu
#$ -l gpu_card=1
#$ -N tarProduction400K

tar cfzv production.tar.gz ./production_400K
