#!/bin/bash

if [ -n "$SEG_DEBUG" ] ; then
    set -x
    env | sort
fi
cd $WEST_SIM_ROOT

mkdir -pv $WEST_CURRENT_SEG_DATA_REF || exit 1
cd $WEST_CURRENT_SEG_DATA_REF || exit 1

export PMEMD="$(which pmemd.cuda) -O"
export USE_LOCAL_SCRATCH=1
# module load mpich/3.3/gcc/8.5.0 cuda/10.2 westpa/2022.07
module load mpich/4.1.2/intel/24.2 westpa/2022.07
#module load westpa/2.0
export AMBERHOME=/opt/crc/a/amber/22.0/amber22
export PATH=$AMBERHOME/bin:$PATH
export LD_LIBRARY_PATH=$AMBERHOME/lib:$LD_LIBRARY_PATH


#module load amber/22.0
#module load westpa/2022.07
####========== Making a symbolic link================####

ln -sv $WEST_SIM_ROOT/common_files/{averageFoldedDES.pdb,1hs3foldedDES_stripped.prmtop,closest_avgfoldedDES.rst7} .

#ln -sv $WEST_SIM_ROOT/westpa_scripts/{ } .


function cleanup() {
    if [[ "$USE_LOCAL_SCRATCH" == "1" ]] ; then
        cp * $WEST_CURRENT_SEG_DATA_REF || exit 1
        cd $WEST_CURRENT_SEG_DATA_REF
        $SWROOT/$JOB_ID*/rm -Rf *
    else
        $SWROOT/$JOB_ID/rm -f *.nc *.prmtop *.rst
    fi
}


####========== Set up the run ==========####

case $WEST_CURRENT_SEG_INITPOINT_TYPE in
    SEG_INITPOINT_CONTINUES)
        # A continuation from a prior segment
        sed "s/RAND/$WEST_RAND16/g" $WEST_SIM_ROOT/common_files/md.in > md.in
        ln -sv $WEST_SIM_ROOT/westpa_scripts/get_pcoord.cpptraj ./get_pcoord.cpptraj
        ln -sv $WEST_PARENT_DATA_REF/seg.rst ./parent.rst
	    ln -sv $WEST_PARENT_DATA_REF/struct.prmtop ./struct.prmtop
        # ^^ Change to cp every 35-38 iterations, MAX 40 ln in a row
	    #cp -v $WEST_PARENT_DATA_REF/struct.prmtop $WEST_CURRENT_SEG_DATA_REF/struct.prmtop
    ;;
    SEG_INITPOINT_NEWTRAJ)
        sed "s/RAND/$WEST_RAND16/g" $WEST_SIM_ROOT/common_files/md0.in > md.in
        ln -sv $WEST_SIM_ROOT/westpa_scripts/get_pcoord.cpptraj ./get_pcoord.cpptraj
        ln -sv $WEST_PARENT_DATA_REF/md4.ncrst ./parent.rst
        ln -sv $WEST_SIM_ROOT/common_files/md4.ncrst ./parent.rst
	ln -sv $WEST_PARENT_DATA_REF/struct.prmtop ./struct.prmtop
    ;;

    *)
        echo "unknown init point type $WEST_CURRENT_SEG_INITPOINT_TYPE"
        exit 21
    ;;
esac


####=========== Submitting the job  ===========####

# Set the CUDA_VISIBLE_DEVICES environment variable
#export CUDA_VISIBLE_DEVICES=$WM_PROCESS_INDEX

# Run the molecular dynamics simulation using PMEMD
$PMEMD -p struct.prmtop -i md.in -c parent.rst -o seg.out -r seg.rst -inf seg.info -x seg.nc || exit 1

#Get progress coordinate
$AMBERHOME/bin/cpptraj -i get_pcoord.cpptraj

# Extract data from the input files
# mindist_data=$(tail -n +2 mindist.dat | awk '{print $2}')
rmsd_data=$(tail -n +2 rmsd_toCrystal.dat | awk '{print $2}')
# brmsd2_data=$(tail -n +2 DMY-bindingrmsd_2.dat | awk '{print $2}')


# python3 getClosestWat.py
# python3 getMGW.py

#MGW_Parent=$(tail -n +1 MGW.dat | awk '{print $1}')
#MGW_Segment=$(tail -n +2 MGW.dat | awk {'print $1'})

# WAT_parent_seg=$(tail -n +1 WaterPcoord.dat | awk '{print $1}') 
# MGW_parent_seg=$(tail -n +1 MGW.dat | awk '{print $1}')


# Find the minimum value between brmsd1 and brmsd2 for each row
# paste <(echo "$mindist_data") <(echo "$brmsd1_data") <(echo "$brmsd2_data") <(echo "$MGW_parent_seg") <(echo "$WAT_parent_seg") | awk '{if ($2 < $3) print $1"\t"$2"\t"$4"\t"$5; else print $1"\t"$3"\t"$4"\t"$5}'  > $WEST_PCOORD_RETURN
paste <(echo "$rmsd_data") > $WEST_PCOORD_RETURN
paste <(echo "$rmsd_data") > checkpcoord.dat

#echo $firstLine > $WEST_PCOORD_RETURN || exit 1
#echo $lastLine >> $WEST_PCOORD_RETURN || exit 1


rm -f get_pcoord.cpptraj md.in parent.rst seg.info # getClosestWat.py getMGW.py


