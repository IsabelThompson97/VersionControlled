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

# ln -sv $WEST_SIM_ROOT/common_files/1hs3foldedDES_stripped.prmtop .

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
        #cp -v $WEST_PARENT_DATA_REF/struct.prmtop $WEST_CURRENT_SEG_DATA_REF/struct.prmtop
    ;;
    SEG_INITPOINT_NEWTRAJ)
        sed "s/RAND/$WEST_RAND16/g" $WEST_SIM_ROOT/common_files/md0.in > md.in
        ln -sv $WEST_SIM_ROOT/westpa_scripts/get_pcoord.cpptraj ./get_pcoord.cpptraj
        ln -sv $WEST_PARENT_DATA_REF/md4.ncrst ./parent.rst
    	ln -sv $WEST_PARENT_DATA_REF/struct.prmtop ./struct.prmtop
    ;;

    *)
        echo "unknown init point type $WEST_CURRENT_SEG_INITPOINT_TYPE"
        exit 21
    ;;
esac


####=========== Submitting the job  ===========####

# Set the CUDA_VISIBLE_DEVICES environment variable
# export CUDA_VISIBLE_DEVICES=$WM_PROCESS_INDEX

# Run the molecular dynamics simulation using PMEMD
$PMEMD -p struct.prmtop -i md.in -c parent.rst -o seg.out -r seg.rst -inf seg.info -x seg.nc || exit 1

#Get progress coordinate
$AMBERHOME/bin/cpptraj -i get_pcoord.cpptraj
$BARNABA ERMSD --ref ../../../common_files/closest_averagefoldedDES.pdb --trj seg.nc --top struct.prmtop

# Extract data from the input files
RoG_data=$(tail -n +2 RoG.dat | awk '{print $2}')
eRMSD_data=$(awk '
  NR == 3 {first = $2 + 0}
  NR > 2 {last = $2 + 0}
  END {
    print first
    print last
  }
' outfile.ERMSD.out)

paste <(echo "$eRMSD_data")  <(echo "$RoG_data") > $WEST_PCOORD_RETURN
paste <(echo "$eRMSD_data") <(echo "$RoG_data") > checkpcoord.dat

#echo $firstLine > $WEST_PCOORD_RETURN || exit 1
#echo $lastLine >> $WEST_PCOORD_RETURN || exit 1


rm -f get_pcoord.cpptraj md.in parent.rst seg.info # getClosestWat.py getMGW.py


