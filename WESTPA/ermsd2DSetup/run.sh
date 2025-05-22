#!/bin/bash 
#$ -M ithomps3@nd.edu
#$ -N folding2D
#$ -m bea
#$ -pe smp 8 
#$ -q gpu
#$ -l gpu_card=1

#module load amber/22.0
#module load westpa/2022.07  
#module rm python/intel-3.6


module load mpich/4.1.2/intel/24.2 westpa/2022.07 cuda/10.2

export AMBERHOME=/opt/crc/a/amber/22.0/amber22
export PATH=$AMBERHOME/bin:$PATH
export LD_LIBRARY_PATH=$AMBERHOME/lib:$LD_LIBRARY_PATH

source env.sh

rm -f west.log

export WM_N_WORKERS=$NSLOTS
w_run --work-manager processes "$@" &> west.log
