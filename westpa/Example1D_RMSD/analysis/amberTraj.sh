#!/bin/bash


# --------------------------------
# Amber Trajectory Tool for WESTPA, Modified by Isabel Thompson
# --------------------------------
# 
# Written by Anthony Bogetti on 28.08.18, Modified 17.02.25
# 
# This script will stitch together a trajectory file from your Amber-WESTPA
# simulation that can be viewed in VMD or another molecular dynmaics 
# visualization software.  Run this script with the command ./amberTraj.sh
# from the same directory where the west.h5 file from your WESTPA simulation
# is located.  The results of this analysis will be stored in a new folder
# called trajAnalysis as the file trace.nc.  Load trace.nc into VMD to 
# visualize the trajectory.  As a note, you will need to have your computer
# configured to run w_trace from the WESTPA software package and cpptraj from 
# the Amber software package.  Though, if the simulation has completed successfully,
# these commands will most likely be ready to run.


# The variables defined below are the name of the new analysis directory that
# will be created and the name of an intermediate file in the process of 
# stitching together the trajectory file.
dir=trajAnalysis
file=path.txt

# The analysis directory is then made and the parameter file for the system is
# copied into it.  All analysis will take place within this directory.
if [ -d "$dir" ]; then
  rm -r $dir
fi
mkdir $dir
cp bstates/StructureFiles/struct_0/struct.prmtop $dir


# The input file for cpptraj is prepared.
if [ -f "cpptraj.in" ]; then
  rm "cpptraj.in"
fi

# Take iteration segment input variables from command line
siter=$1
sseg=$2

echo Iteration=$siter
echo Segment=$sseg

# w_trace is run, generating a history of the successful trajectory specified
# above.  This will create a list of all of the iterations and segments that
# need to be stitched together to create a smooth, viewable, successful trajectory.
w_trace $siter:$sseg

# Output files from w_trace are moved into the trajAnalysis directory.
mv $(echo 'traj_'$siter'_'$sseg'_trace.txt') $dir
mv trajs.h5 $dir
cd $dir

# Calculate, print wallclock and CPU time
awk '
!/^#/ {
    wallclock += $4
    cpu += $5
}
END {
    printf "Wallclock time: %.4f seconds (%d:%02d:%02d)\n", 
           wallclock, 
           int(wallclock/3600), 
           int((wallclock%3600)/60), 
           int(wallclock%60)
    printf "CPU time: %.4f seconds (%d:%02d:%02d)\n",
           cpu,
           int(cpu/3600),
           int((cpu%3600)/60),
           int(cpu%60)
}' 'traj_'$siter'_'$sseg'_trace.txt'

# The first few lines of the output of w_trace are removed (including the 
# initial state of the system, which doesn't have an iter:seg ID)
cat $(echo 'traj_'$siter'_'$sseg'_trace.txt') | tail -n +9 > path.txt


# Now, the file listing all of the successful trajectory's historical iterations
# and segments is read line by line and the iteration IDs and segment IDs
# are added to a variable that specifies the path to the coordinate file of
# that successful trajectory.  This path is then appended to the cpptraj input
# file following the trajin command.


# Please note that while the iteration and segment IDs here are padded to six
# digits with zeroes, the length of this number is specified in the west.cfg file
# in the main WESTPA simuation directory and can be changed by the user.  If you
# ran the simulation with more than 100000 iterations or segments and adjusted this
# parameter in the west.cfg file you will need to adjust it here too.  For 99% of
# users, however, the following should work just fine.

while read file; do
	iter=$(echo $file | awk '{print $1}')
	seg=$(echo $file | awk '{print $2}')
	filestring='../traj_segs/'$(printf "%06d" $iter)'/'$(printf "%06d" $seg)'/''seg.nc' 
        echo "trajin $filestring" >> cpptraj.in	
done < "path.txt"

# These two lines will specify the name of the file where the stitched rtajectory
# is written to and a line to commence the cpptraj run
printf "autoimage\ntrajout trace_$iter-$seg.nc\nrun" >> cpptraj.in 

# Now, cpptraj is called using the parameter file and the cpptraj.in file
# that was created above as input.  The text displayed to the terminal is written
# to the file traj.log.
cpptraj -p struct.prmtop -i cpptraj.in > traj.log

echo Trajectory file creation is complete.
echo To view your trajectory, load the parameter file into VMD/Chimera followed by the trace.nc file, both located in the trajAnalysis directory.

# The intermediary files are removed to clean up the analysis directory.
rm path.txt trajs.h5 
cd ..