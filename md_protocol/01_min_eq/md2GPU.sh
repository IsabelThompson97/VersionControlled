#!/bin/bash 
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 1
#$ -q gpu
#$ -l gpu_card=1
#$ -N fHRMmd2

module load amber/24.0

$AMBERHOME/bin/pmemd.cuda -O -i md2a.in -o md2a.out -p 2KOCFolded_HRM.prmtop -c md1.rst -r md2a.rst -x md2a.nc -ref md1.rst

$AMBERHOME/bin/pmemd.cuda -O -i md2b.in -o md2b.out -p 2KOCFolded_HRM.prmtop -c md2a.rst -r md2b.rst -x md2b.nc -ref md2a.rst

$AMBERHOME/bin/pmemd.cuda -O -i md2c.in -o md2c.out -p 2KOCFolded_HRM.prmtop -c md2b.rst -r md2c.rst -x md2c.nc -ref md2b.rst

$AMBERHOME/bin/pmemd.cuda -O -i md2d.in -o md2d.out -p 2KOCFolded_HRM.prmtop -c md2c.rst -r md2d.rst -x md2d.nc -ref md2c.rst

$AMBERHOME/bin/pmemd.cuda -O -i md2e.in -o md2e.out -p 2KOCFolded_HRM.prmtop -c md2d.rst -r md2e.rst -x md2e.nc -ref md2d.rst
