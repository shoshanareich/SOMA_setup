#!/bin/bash

#SBATCH -J soma4
#SBATCH -o soma4.%j.out
#SBATCH -e soma4.%j.err
#SBATCH -N 3
#SBATCH -n 64
#SBATCH -t 72:00:00

# Example: 20-year run at tau_max=0.4 (daily snapshots), started from the
# year-90 pickup of the spin-up (run_spinup.sh). Edit the variables below
# for other scenarios.

nprocs=64

#--- set dir ------------
basedir=/path/to/SOMA_setup              # this repository
bindir=/path/to/input_binaries           # output of gendata/ where input binaries are stored
workdir=/path/to/run_20yrs_tau0.4        # run directory
pickupdir=/path/to/run_spinup            # directory of spin up run
pickupts=0002332800                      # year 90 of the spin-up

mkdir ${workdir}
cd ${workdir}

#--- namelists ---------
cp ${basedir}/input/* .
ln -s ${bindir}/* .

# wind scenario: change the second file name (e.g. wind_sv_0.1_0.2_cos_1200s_248.bin)
sed -i -e 's/'"wind_sv_0.1_0.4_cos_1200s_248.bin"'/'"wind_sv_0.1_0.4_cos_1200s_248.bin"'/g' data

#--- pickups ---------
cp ${pickupdir}/pickup.${pickupts}.meta ./pickup.0000000001.meta
cp ${pickupdir}/pickup.${pickupts}.data ./pickup.0000000001.data
cp ${pickupdir}/pickup_cd.${pickupts}.meta ./pickup_cd.0000000001.meta
cp ${pickupdir}/pickup_cd.${pickupts}.data ./pickup_cd.0000000001.data

#--- executable --------
cp -p ${basedir}/build/mitgcmuv .

#--- run ----------------------------------
set -x
date > run.MITGCM.timing

mpiexec -n ${nprocs} ./mitgcmuv

date >> run.MITGCM.timing
