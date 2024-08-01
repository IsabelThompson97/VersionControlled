#1HS3 FOLDED PREP
#run with tleap -s -f leap.in on CL

source leaprc.RNA.OL3
source leaprc.water.tip3p
mol = loadpdb 1HS3out.pdb
addions mol Na+ 0
solvateoct mol TIP3PBOX 10.0
addionsrand mol Na+ 44 Cl- 44
savepdb mol 1HS3final.pdb
saveamberparm mol 1HS3.prmtop 1HS3.inpcrd
saveamberparm mol 1HS3.prmtop 1HS3.rst7
check mol
quit