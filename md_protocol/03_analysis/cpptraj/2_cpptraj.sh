#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -pe smp 8
#$ -q gpu
#$ -l gpu_card=1
#$ -N HRMcpptraj

module load amber/24.0

# # -----------------------------------------
cpptraj -i 1_sugarPuckerU7C8.in
cp sugarPucker_U7.dat sugarPucker_U7.txt
less sugarPuckerStats_U7.dat >> analysisOutput_2KOCFolded_HRM.txt 
cp sugarPucker_C8.dat sugarPucker_C8.txt
less sugarPuckerStats_C8.dat >> analysisOutput_2KOCFolded_HRM.txt 

# # -----------------------------------------
# cpptraj -i 1_G9dihedral.in
# cp G9_dihedral.dat G9_dihedral.txt
# less G9_dihedral_stats.dat >> analysisOutput_2KOCFolded_HRM.txt 

# # -----------------------------------------
# cpptraj -i 1_radiusGyr.in
# cp radGyr.dat radGyr.txt

# # -----------------------------------------
# cpptraj -i 1_rmsdtoNMR.in
# cp rmsd_toNMR.dat rmsd_toNMR.txt

# # -----------------------------------------
# cpptraj -i 1_rmsd.in
# cp rmsd.dat rmsd.txt

# #_____________________________________________
# cpptraj -i 1_minDistEnds.in
# cp minDistEnds.dat minDistEnds.txt

# #_____________________________________________
# cpptraj -i 1_minDistLoopContacts.in
# cp minDistG9-U6.dat minDistG9-U6.txt
# cp minDistG9-U6sugar-base.dat minDistG9-U6sugar-base.txt
# cp minDistG9-U7sugar-base.dat minDistG9-U7sugar-base.txt
# cp minDistU7-C8base-phosphate.dat minDistU7-C8base-phosphate.txt

# # -----------------------------------------
# cpptraj -i 1_rmsdtoNMRBackbone.in
# cp rmsd_toNMRBackbone.dat rmsd_toNMRBackbone.txt

# # -----------------------------------------
# cpptraj -i 1_rmsdtoNMRStem.in
# cp rmsd_toNMRStem.dat rmsd_toNMRStem.txt

# # -----------------------------------------
# cpptraj -i 1_rmsdtoNMRLoop.in
# cp rmsd_toNMRLoop.dat rmsd_toNMRLoop.txt

# # -----------------------------------------
# cpptraj -i 1_rmsdtoNMR1-14Bases.in
# cp rmsd_toNMR1-14Bases.dat rmsd_toNMR1-14Bases.txt

# # ----------------------------------------
# cpptraj -i 1_hbondFrames.in
# cp hbondFrames.dat hbondFrames.txt

# # -----------------------------------------
# cpptraj -i 1_hbondsLifetimeLoop.in
# cp hbondLifetimeLoop.dat hbondLifetimeLoop.txt

# # -----------------------------------------
# cpptraj -i 1_hbondsLifetime.in

# ----------------------------------------
# # BOX VOLUME:
# # No. Sodium Ions: 18
# # Sodium Density: 18 atoms/ Å³
# # No. Chloride Ions: 6
# # Chloride Density: 6 atoms/ Å³ 

# cpptraj -i 1_IonRDF.in
# cp RDF-Na.dat RDF-Na.txt
# cp RDF-Cl.dat RDF-Cl.txt
