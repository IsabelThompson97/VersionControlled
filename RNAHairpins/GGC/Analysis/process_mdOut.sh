#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N process_mdout_prod

module load amber

# process_mdout.perl ../../min_eq/*.out ../../production/*.out

process_mdout.perl ../md_final01.out ../md_final2.out ../md_final3.out ../md_final4.out ../md_final5.out ../md_final6.out ../md_final7.out ../md_final8.out ../md_final9.out ../md_final_10.out


# If in directory ggc/folded/analysis/process_mdOut and trajectories in /ggc/folded/production
#process_mdout.perl ../../../production/md_final01.out ../../../production/md_final2.out ../../../production/md_final3.out ../../../production/md_final4.out ../../../production/md_final5.out ../../../production/md_final6.out ../../../production/md_final7.out ../../../production/md_final8.out ../../../production/md_final9.out ../../../production/md_final_10.out
