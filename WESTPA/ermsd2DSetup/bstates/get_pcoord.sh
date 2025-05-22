#!/bin/bash
#$ -M ithomps3@nd.edu
#$ -m abe
#$ -N compile_pcoord
#$ -pe smp 16
#$ -q long

set -e

for n in $(cat struct.txt);
do
cp get_pcoordERMSD.txt $n.sh
sed -i 's/INDEX/'$n'/' $n.sh
sed -i 's/INDEX/'$n'/' $n.sh
sed -i 's/INDEX/'$n'/' $n.sh
mv $n.sh inputERMSD_$n.sh

./inputERMSD_$n.sh

done

module load amber/22.0

for n in $(cat struct.txt);
do
cp get_pcoord.cpptraj $n.in
sed -i 's/INDEX/'$n'/' $n.in
mv $n.in input_$n.in

$AMBERHOME/bin/cpptraj -i input_$n.in

done 

rm input_* inputERMSD_*
