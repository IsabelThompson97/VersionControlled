#!/bin/bash 
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 1
#$ -q gpu
#$ -l gpu_card=1
#$ -N mdoutHRM

module load amber

process_mdout.perl ../../../production/md_final1.out ../../../production/md_final2.out ../../../production/md_final3.out ../../../production/md_final4.out ../../../production/md_final5.out ../../../production/md_final6.out ../../../production/md_final7.out ../../../production/md_final8.out ../../../production/md_final9.out ../../../production/md_final_10.out  
