#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -N init 
#$ -pe smp 8
#$ -q long

# Set up simulation environment
source env.sh

# Clean up from previous/ failed runs
rm -rf traj_segs seg_logs istates west.h5 
mkdir   seg_logs traj_segs istates

# Set pointer to bstate and tstate
BSTATE_ARGS="--bstate-file $WEST_SIM_ROOT/bstates/bstates.txt"
#TSTATE_ARGS="--tstate bound,1.35"

echo ${BSTATE_ARGS}

# Run w_init
w_init \
  $BSTATE_ARGS \
  $TSTATE_ARGS \
  --segs-per-state 8 \
  --work-manager threads "$@">& init.log
