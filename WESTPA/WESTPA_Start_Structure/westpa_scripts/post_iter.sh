#!/bin/bash

if [ -n "$SEG_DEBUG" ] ; then
    set -x
    env | sort
fi

cd $WEST_SIM_ROOT || exit 1

cp west.h5 westBackup.h5

cp westBackup.h5 westBackup-backup.h5

ITER=$(printf "%06d" $WEST_CURRENT_ITER)


FileCount=$( ls seg_logs | wc -l )
if [ $FileCount -gt 30000 ] ; then
    FirstIter=$(ls seg_logs | head -1 | awk -F'[-]' '{print $1}' )
    LastIter=$(ls seg_logs | sort -n | tail -1 | awk -F '[-]' '{print $1}' )
    mkdir seg_logs/overflow$FirstIter-$LastIter
    mv seg_logs/*.log seg_logs/overflow$FirstIter-$LastIter
fi
