#!/bin/bash

#
# args
#

FILEID=$1
TAG=$2
COPYDIR=$3

return

echo "[wrapper] FILEID    = " ${FILEID}
echo "[wrapper] COPYDIR   = " ${COPYDIR}

#
# set up environment
#
CMSSW_VERSION=CMSSW_9_4_1

###version using cvmfs install of CMSSW
echo "[wrapper] setting env"
export SCRAM_ARCH=slc6_amd64_gcc630
source /cvmfs/cms.cern.ch/cmsset_default.sh
OLDDIR=`pwd`
cd /cvmfs/cms.cern.ch/$SCRAM_ARCH/cms/cmssw/$CMSSW_VERSION/src
#cmsenv
eval `scramv1 runtime -sh`
cd $OLDDIR


echo "[wrapper] hostname  = " `hostname`
echo "[wrapper] date      = " `date`
echo "[wrapper] linux timestamp = " `date +%s`

#
# untar input sandbox
#

echo "[wrapper] current directory is:"
pwd

echo "[wrapper] extracting input sandbox"
TARFILE=`ls *.tar.xz`
tar -xJf $TARFILE

#source job_input/setupenv.sh
#printenv

echo "[wrapper] input contents are"
ls -a


#
# run it
#
INFILE="/hadoop/cms/store/user/bemarsh/LGAD/traj_inputs_for_jonathan/${TAG}/output_${FILEID}.txt"
echo "[wrapper] running: python chronosim.py" "stl_files" $INFILE "output.root" 

python chronosim.py stl_files $INFILE output.root

#
# do something with output
#

echo "[wrapper] output is"
ls -lh


echo "[wrapper] copying file"
OUTPUT=output.root
echo "[wrapper] OUTPUT = " ${OUTPUT}

#
# clean up
#

if [ ! -d "${COPYDIR}" ]; then
    echo "creating output directory " ${COPYDIR}
    mkdir ${COPYDIR}
fi

export LD_PRELOAD=/usr/lib64/gfal2-plugins/libgfal_plugin_xrootd.so
gfal-copy -p -f -t 4200 --verbose file://`pwd`/${OUTPUT} gsiftp://gftp.t2.ucsd.edu${COPYDIR}/output_${FILEID}.root

echo "[wrapper] cleaning up"
for FILE in `find . -not -name "*stderr" -not -name "*stdout"`; do rm -rf $FILE; done
echo "[wrapper] cleaned up"
pwd
ls
#
