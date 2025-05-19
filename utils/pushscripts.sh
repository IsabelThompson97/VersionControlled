#!/bin/bash

# -------------------
# README
# Script to copy **scripts only** to GitHub controlled folder
# DO NOT cp data files
# RUN ME FROM THE PROJECT DIRECTORY SCRIPTS FOLDER
# /users/ithomps3/VersionControlled/utils/pushscripts.sh $OutputName 
# With alias in .bashrc command is **** pushscripts $OutputName *******
# Example: pushscripts RNAHairpins/GGC/Analysis/process_cpptraj
# -------------------

ISABEL_GIT_DIR="/users/ithomps3/VersionControlled/"
ARG_1=$1


STORE_AT=$ISABEL_GIT_DIR$ARG_1

#echo $ISABEL_GIT_DIR
#echo "Arg1 = $ARG_1"

mkdir -p $STORE_AT

cp *.in $STORE_AT
cp *.sh $STORE_AT
cp *.ipynb $STORE_AT
cp *.py $STORE_AT

# ------------
