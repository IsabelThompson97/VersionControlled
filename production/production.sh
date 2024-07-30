#!/bin/bash 
#$ -pe smp 1
#$ -m bea
#$ -M nkarpins@nd.edu
#$ -N doublepcoord_check
#$ -q gpu
#$ -l gpu_card=1

module load amber/22.0

$AMBERHOME/bin/pmemd.cuda -O -i md_final.in -p final_double_bound.prmtop -c md.rst -ref md.rst -o md_final.out -r md_final.rst -x md_final.nc

$AMBERHOME/bin/pmemd.cuda -O -i md_final2.in -p final_double_bound.prmtop -c md_final.rst -ref md_final.rst -o md_final2.out -r md_final2.rst -x md_final2.nc

$AMBERHOME/bin/pmemd.cuda -O -i md_final3.in -p final_double_bound.prmtop -c md_final2.rst -ref md_final2.rst -o md_final3.out -r md_final3.rst -x md_final3.nc

$AMBERHOME/bin/pmemd.cuda -O -i md_final4.in -p final_double_bound.prmtop -c md_final3.rst -ref md_final3.rst -o md_final4.out -r md_final4.rst -x md_final4.nc

$AMBERHOME/bin/pmemd.cuda -O -i md_final5.in -p final_double_bound.prmtop -c md_final4.rst -ref md_final4.rst -o md_final5.out -r md_final5.rst -x md_final5.nc

$AMBERHOME/bin/pmemd.cuda -O -i md_final6.in -p final_double_bound.prmtop -c md_final5.rst -ref md_final5.rst -o md_final6.out -r md_final6.rst -x md_final6.nc

$AMBERHOME/bin/pmemd.cuda -O -i md_final7.in -p final_double_bound.prmtop -c md_final6.rst -ref md_final6.rst -o md_final7.out -r md_final7.rst -x md_final7.nc

$AMBERHOME/bin/pmemd.cuda -O -i md_final8.in -p final_double_bound.prmtop -c md_final7.rst -ref md_final7.rst -o md_final8.out -r md_final8.rst -x md_final8.nc

$AMBERHOME/bin/pmemd.cuda -O -i md_final9.in -p final_double_bound.prmtop -c md_final8.rst -ref md_final8.rst -o md_final9.out -r md_final9.rst -x md_final9.nc

$AMBERHOME/bin/pmemd.cuda -O -i md_final_10.in -p final_double_bound.prmtop -c md_final9.rst -ref md_final9.rst -o md_final_10.out -r md_final_10.rst -x md_final_10.nc
