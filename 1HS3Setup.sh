#1HS3 FOLDED PREP

source leaprc.RNA.OL3
source leaprc.water.tip3p
mol = loadpdb 1HS3out.pdb
addions mol Na+ 0
solvateoct mol TIP3PBOX 12.0
savepdb mol 1HS3final.pdb
saveamberparm mol 1HS3.prmtop 1HS3.inpcrd
saveamberparm mol 1HS3.prmtop 1HS3.rst7
check mol
quit