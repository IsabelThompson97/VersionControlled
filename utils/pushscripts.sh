#!/bin/bash

# -------------------
# README
# Script to copy **scripts only** to GitHub controlled folder
# DO NOT cp data files
# RUN ME FROM THE PROJECT DIRECTORY SCRIPTS FOLDER
# /afs/crc.nd.edu/user/i/ithomps3/VersionControlled/utils/pushscripts.sh $OutputName #$CommitMessage
# With alias in .bashrc command is **** pushscripts $OutputName *******
# Example: pushscripts RNAHairpins/GGC/Analysis/process_cpptraj
# -------------------

ISABEL_GIT_DIR="/afs/crc.nd.edu/user/i/ithomps3/VersionControlled/"
ARG_1=$1
#COMMIT_MESSAGE=$2

STORE_AT=$ISABEL_GIT_DIR$ARG_1

#echo $ISABEL_GIT_DIR
#echo "Arg1 = $ARG_1"

mkdir -p $STORE_AT

cp *.in $STORE_AT
cp *.sh $STORE_AT
cp *.ipynb $STORE_AT
cp *.py $STORE_AT

# ------------

# Figure out how to automatically fetch GitHub 

#echo "git add $ISABEL_GIT_DIR"
#echo 'git commit -c '$ISABEL_GIT_DIR' -m "'"$COMMIT_MESSAGE"'"'