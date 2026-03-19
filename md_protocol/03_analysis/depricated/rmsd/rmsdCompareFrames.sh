#!/bin/bash

module load amber/22.0

for REF in $(cat frames.txt)
do
    for FRAME in $(cat frames.txt)
    do

    cp rmsdCompare.in input_$REF.$FRAME.in
    sed -i 's/REF/'$REF'/' input_$REF.$FRAME.in
    sed -i 's/REF/'$REF'/' input_$REF.$FRAME.in
    sed -i 's/FRAME/'$FRAME'/' input_$REF.$FRAME.in 
    sed -i 's/FRAME/'$FRAME'/' input_$REF.$FRAME.in

    $AMBERHOME/bin/cpptraj -i input_$REF.$FRAME.in

    rmsd_data=$(tail -n +2 rmsdCompare_$REF.$FRAME.dat | awk '{print $2}')
    paste <(echo "$REF") <(echo "$FRAME") <(echo "$rmsd_data") >> rmsdCompare_$REF.csv
done
done

cat rmsdCompare_*.csv >> rmsdCompareFrames.csv

rm input_*.in
rm rmsdCompare_*.dat rmsdCompare_*.csv