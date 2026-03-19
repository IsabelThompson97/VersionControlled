#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -N compile_pcoord
#$ -pe smp 16
#$ -q long

module load amber/22.0

set -e

for n in $(cat struct.txt);
do
    cp get_pcoord.cpptraj $n.in
    sed -i 's/INDEX/'$n'/' $n.in
    mv $n.in input_$n.in

    $AMBERHOME/bin/cpptraj -i input_$n.in

    # mindist_data=$(tail -n +2 StructureFiles/struct_$n/mindist.dat | awk '{print $2}')
    rmsd_data=$(tail -n +2 StructureFiles/struct_$n/rmsd_toNMR.dat | awk '{print $2}')

    paste <(echo "$rmsd_data") > StructureFiles/struct_$n/pcoordreturn.dat
    # paste <(echo "$mindist_data") <(echo "$rmsd_data") > StructureFiles/struct_$n/pcoordreturn.dat

done

rm input_*
