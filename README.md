# SOMA_setup

MITgcm configuration for the 1/4° SOMA (Simulating Ocean Mesoscale Activity,
Wolfram et al. 2015) double-gyre ocean, used to generate the training data for

> *Data-Driven Ocean Emulation: Using Operator Inference to Emulate a Double Gyre Ocean System.*

The domain is a 248 × 248 × 31 basin at 0.25°, forced by a seasonally varying zonal wind
stress and relaxation to surface temperature and salinity. Wind scenarios are labelled by
the peak wind stress `tau_max` (the seasonal cycle runs between 0.1 and `tau_max` N/m²).
The paper uses `tau_max` = 0.2, 0.3, 0.4, 0.5.

| Path | Contents |
|---|---|
| `code/` | compile-time options (`SIZE.h`, `packages.conf`, `*_OPTIONS.h`) |
| `input/` | run-time namelists (`data`, `data.pkg`, `data.diagnostics`, ...) |
| `linux_amd64_ifort+mpi_sverdrup` | build optfile used for the paper runs |
| `gendata/` | scripts that write the input binaries (bathymetry, forcing) |
| `run_spinup.sh` | SLURM job: 100-year spin-up |
| `run_soma.sh` | SLURM job: 20-year scenario run from the spin-up |
| `make_states_nc.py` | collects a run's daily snapshots into one master file `states_20yrs.nc` |

## 1. Get MITgcm (checkpoint68q)

Clone MITgcm next to this repository and check out the checkpoint used for the paper:

```bash
git clone https://github.com/MITgcm/MITgcm.git
cd MITgcm
git checkout checkpoint68q
cd ..
```

The commands below assume this layout:

```
MITgcm/
SOMA_setup/
```

## 2. Build

The optfile is for an Intel compiler + Intel MPI cluster with NetCDF. Load the
modules it lists, e.g.

```bash
module load intel impi netcdf netcdf-fortran phdf5
```

and build:

```bash
cd SOMA_setup
mkdir build && cd build
../../MITgcm/tools/genmake2 -rootdir ../../MITgcm -mods ../code -mpi \
    -optfile ../linux_amd64_ifort+mpi_sverdrup
make depend
make
cd ..
```

This produces `build/mitgcmuv`. `code/SIZE.h` splits the domain into 8 × 8 tiles of
31 × 31 points, so the model runs on **64 MPI processes**. On other machines, start from
one of the optfiles in `MITgcm/tools/build_options/`; it must compile with big-endian I/O
(`-convert big_endian` for Intel).

## 3. Create the input binaries

The scripts need Python 3 with `numpy`. Create all files used in the paper (~45 GB) with

```bash
bash gendata/make_all.sh /path/to/input_binaries
```

or one at a time:

```bash
python gendata/make_bathymetry.py --out-dir /path/to/input_binaries   # bathy4.bin
python gendata/make_relaxation.py --out-dir /path/to/input_binaries   # SST and SSS restoring
python gendata/make_wind.py --tau-max 0.4 --out-dir /path/to/input_binaries
```

| File | Contents |
|---|---|
| `bathy4.bin` | SOMA bowl: 3500 m basin with a 100 m shelf |
| `SST_relax_change_max_1200s_248.bin` | SST restoring, linear in latitude to −1.8 °C at the northern edge; the southern value follows a seasonal cycle between 25 and 30 °C |
| `SSS_relax_yrly_1200s_248.bin` | SSS restoring, 36 psu (south) to 35 psu (north), constant in time |
| `wind_sv_{tau_min}_{tau_max}_cos_1200s_248.bin` | zonal wind stress: double-gyre pattern times a seasonal cosine from `tau_max` (January) to `tau_min` |

Each forcing file holds one 248 × 248 record per model time step (1200 s) for one 360-day
year (~6.4 GB). The model cycles through it every year. `make_wind.py` takes any amplitudes,
e.g. `--tau-min 0.05 --tau-max 0.35` (default `--tau-min 0.1`).

## 4. Spin-up

Edit the three paths at the top of `run_spinup.sh` (`basedir` = this repository,
`bindir` = the input binaries, `workdir` = a new run directory), then submit:

```bash
sbatch run_spinup.sh
```

This runs 100 years at `tau_max` = 0.4 from rest (the reference T/S profiles in
`input/data`), writing a pickup every year and no snapshots. 

## 5. Scenario runs

Each scenario starts from the spin-up's **year-90 pickup** (iteration 2332800) and runs
20 years with the wind of that scenario, writing daily snapshots. Edit the top of
`run_soma.sh`:

- `basedir`, `bindir`: as for the spin-up
- `workdir`: a new run directory, e.g. `run_20yrs_tau0.2`
- `pickupdir`: the spin-up run directory (`pickupts=0002332800` is year 90)
- the `sed` line: set the second file name to the scenario's wind file, e.g.
  `wind_sv_0.1_0.2_cos_1200s_248.bin`

and submit:

```bash
sbatch run_soma.sh
```

A 20-year run takes ~13 hours on 64 cores and writes ~300 GB of daily snapshots
(`U`, `V`, `W`, `T`, `S`, `Eta`, `PH`, `PHL`).

## 6. Make the training-data NetCDF file

`make_states_nc.py` merges a run's daily `U`, `V`, `Eta`, `T`, `S` snapshots into one file,
`states_20yrs.nc` (7201 snapshots, ~220 GB), which is what the ROM code reads. It needs
`numpy`, `xarray`, `xmitgcm` and `netCDF4`:

```bash
pip install numpy xarray xmitgcm netCDF4
python make_states_nc.py /path/to/run_20yrs_tau0.2 /path/to/run_spinup
```

The second argument is a directory with the MITgcm grid files (`RC.meta`, ...). The spin-up
writes them; runs started from a pickup do not.

## References

- Wolfram, P. J., T. D. Ringler, M. E. Maltrud, D. W. Jacobsen, and M. R. Petersen (2015).
  Diagnosing isopycnal diffusivity in an eddying, idealized midlatitude ocean basin via
  Lagrangian, in Situ, Global, High-Performance Particle Tracking (LIGHT).
  *J. Phys. Oceanogr.*, 45, 2114–2133.
- MITgcm: https://mitgcm.org
