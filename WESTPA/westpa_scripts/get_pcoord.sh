#!/bin/bash
source env.sh

if [ -n "$SEG_DEBUG" ] ; then
  set -x
  env | sort
fi

cd $WEST_SIM_ROOT



awk '{print}' $WEST_BSTATE_DATA_REF/pcoordreturn.dat > $WEST_PCOORD_RETURN
#awk '{print}' $WEST_SIM_ROOT/bstates/pcoordreturn.dat > $WEST_PCOORD_RETURN


head -v $WEST_PCOORD_RETURN

if [ -n "$SEG_DEBUG" ] ; then
  head -v $WEST_PCOORD_RETURN
fi
