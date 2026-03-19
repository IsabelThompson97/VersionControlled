#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N process_mdout_prod

module load amber

process_mdout.perl ../md_final01.out ../md_final2.out ../md_final3.out ../md_final4.out ../md_final5.out ../md_final6.out ../md_final7.out ../md_final8.out ../md_final9.out ../md_final_10.out

# Examples
# process_mdout.perl ../md1.out ../md2a.out ../md2b.out ../md2c.out ../md2d.out ### whatever output files you want to analyze ###
# process_mdout.perl ../../md1.out ../../md2a.out ../../md2b.out ../../md2c.out ../../md2d.out ../../md2e.out ../../md3.out ../../md4.out
# process_mdout.perl ../../min_eq/*.out ../../production/*.out
# process_mdout.perl ../../production/*.out