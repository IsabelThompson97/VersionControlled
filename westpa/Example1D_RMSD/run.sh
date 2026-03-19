#!/bin/bash 
#$ -pe smp 8 
#$ -m bea
#$ -M ithomps3@nd.edu
#$ -N RMSD_folding
#$ -q gpu
#$ -l gpu_card=1

#module load amber/22.0
#module load westpa/2022.07  
#module rm python/intel-3.6


module load mpich westpa/2022.10 cuda/10.2

export AMBERHOME=/opt/crc/a/amber/22.0/amber22
export PATH=$AMBERHOME/bin:$PATH
export LD_LIBRARY_PATH=$AMBERHOME/lib:$LD_LIBRARY_PATH

source env.sh

rm -f west.log

export WM_N_WORKERS=$NSLOTS
w_run --work-manager processes "$@" &> west.log
