#!/bin/bash

#SBATCH -J soma4_spinup
#SBATCH -o soma4_spinup.%j.out
#SBATCH -e soma4_spinup.%j.err
#SBATCH -N 3
#SBATCH -n 64
#SBATCH -t 72:00:00

# 100-year spin-up at tau_max=0.4, from rest (tRef/sRef in input/data).
# Writes a pickup every year and no daily snapshots.

nprocs=64

#--- set dir ------------
basedir=/path/to/SOMA_setup              # this repository
bindir=/path/to/input_binaries           # output of gendata/ where input binaries are stored
workdir=/path/to/run_spinup              # run directory

mkdir ${workdir}
cd ${workdir}

#--- namelists ---------
cp ${basedir}/input/* .
ln -s ${bindir}/* .

# start from rest, run 100 years, no snapshots, spin-up diagnostics
sed -i -e 's/ nIter0=1,/ nIter0=0,/' \
       -e 's/ nTimesteps = 518400.,/ nTimesteps = 2592000.,/' \
       -e 's/ dumpFreq=86400,/ dumpFreq=0,/' data
mv data.diagnostics_spinup data.diagnostics

#--- executable --------
cp -p ${basedir}/build/mitgcmuv .

#--- run ----------------------------------
set -x
date > run.MITGCM.timing

mpiexec -n ${nprocs} ./mitgcmuv

date >> run.MITGCM.timing
