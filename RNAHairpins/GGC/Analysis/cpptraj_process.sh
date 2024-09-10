#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 24
#$ -q long
#$ -N rmsd_ggcfolded

module load amber/22.0

cpptraj -i process_rmsd.in #change .in script for different analyses

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