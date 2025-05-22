#!/bin/bash

module load amber/22.0

for n in $(cat frames.txt);
do
    echo 'Processing: $n'

    cp exportExamples.in input_$n.in
    sed -i 's/FRAME/'$n'/' input_$n.in
    sed -i 's/FRAME/'$n'/' input_$n.in
    sed -i 's/FRAME/'$n'/' input_$n.in  
    sed -i 's/FRAME/'$n'/' input_$n.in 
    sed -i 's/FRAME/'$n'/' input_$n.in

    $AMBERHOME/bin/cpptraj -i input_$n.in

    rmsd_data=$(tail -n +2 rmsd_toCrystal_$n.dat | awk '{print $2}')
    paste <(echo "$n") <(echo "$rmsd_data") >> rmsd_toCrystal.csv

done

rm input_*
rm rmsd_toCrystal_*.dat