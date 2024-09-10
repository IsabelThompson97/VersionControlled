#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N rmsd_ggcfolded

#### To run processing script from production/process_cpptraj directory but access .nc files in /production
#### .in files and .dat files saved in production/process_cpptraj

module load amber/22.0

# Change working directory to /production where .nc files are located
cd ..

# Call cpptraj with .in file located --Inside-- /process_cpptraj
# Will save datafiles to /process_cpptraj instead of /production
cpptraj -i ./process_cpptraj/process_rmsd.in

# Move to process_cpptraj directory
cd process_cpptraj

# Copy datafile .dat to text file .txt for processing with python script
cp rmsd.dat rmsd.txt

# ----------------------------------------
# cpptraj -i ./process_cpptraj/process_hbondframes.in
# cd process_cpptraj
# cp hbonds.dat hbonds.txt

#_____________________________________________
# cpptraj -i ./process_cpptraj/process_minDist.in
# cd process_cpptraj
# cp minDist.dat minDist.txt


###################################
#___________________________________________Alternatively, for different file structure
#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N rmsd_ggcfolded

module load amber/22.0

cd ..

cpptraj -i ./process_cpptraj/process_rmsd.in
# mv rmsd.dat process_cpptraj/rmsd.dat
# cd process_cpptraj
# cp rmsd.dat rmsd.txt

# cpptraj -i ./process_cpptraj/process_hbondframes.in
# mv hbonds.dat process_cpptraj/hbonds.dat
# cd process_cpptraj
# cp hbonds.dat hbonds.txt


# cpptraj -i ./process_cpptraj/process_min_dist.in
# mv minDist.dat process_cpptraj/minDist.dat
# cd process_cpptraj
# cp minDist.dat minDist.txt