#!/bin/bash 
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24 
#$ -q long
#$ -N GGC-rna-md2check 

module load amber/22.0

mpirun -np $NSLOTS $AMBERHOME/bin/sander.MPI -O -i md2a.in -o md2a.out -p final_double_bound.prmtop -c md1.rst -r md2a.rst -x md2a.nc -ref md1.rst

mpirun -np $NSLOTS $AMBERHOME/bin/sander.MPI -O -i md2b.in -o md2b.out -p final_double_bound.prmtop -c md2a.rst -r md2b.rst -x md2b.nc -ref md2a.rst

mpirun -np $NSLOTS $AMBERHOME/bin/sander.MPI -O -i md2c.in -o md2c.out -p final_double_bound.prmtop -c md2b.rst -r md2c.rst -x md2c.nc -ref md2b.rst

mpirun -np $NSLOTS $AMBERHOME/bin/sander.MPI -O -i md2d.in -o md2d.out -p final_double_bound.prmtop -c md2c.rst -r md2d.rst -x md2d.nc -ref md2c.rst

mpirun -np $NSLOTS $AMBERHOME/bin/sander.MPI -O -i md2e.in -o md2e.out -p final_double_bound.prmtop -c md2d.rst -r md2e.rst -x md2e.nc -ref md2d.rst
