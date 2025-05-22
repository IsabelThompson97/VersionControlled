#!/bin/bash

# Set up environment for westpa
# Actviate a conda environment containing westpa, openmm and mdtraj;
# you may need to create this first (see install instructions)


# module load mpich/3.3/gcc/8.5.0 cuda/10.2 westpa/2022.07
# For ./init.sh USE westpa/2022.10
module load westpa/2022.07 mpich cuda/10.2

export AMBERHOME=/opt/crc/a/amber/22.0/amber22
export PATH=$AMBERHOME/bin:$PATH
export LD_LIBRARY_PATH=$AMBERHOME/lib:$LD_LIBRARY_PATH

export WEST_SIM_ROOT="$PWD"
export SIM_NAME=$(basename $WEST_SIM_ROOT)

export AMBER_EXEC=$AMBERHOME/bin/pmemd.cuda
export CPPTRAJ=$AMBERHOME/bin/cpptraj
