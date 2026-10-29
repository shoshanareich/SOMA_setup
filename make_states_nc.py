"""Collect the daily MITgcm state dumps of one run into states_20yrs.nc.

Reads the U, V, Eta, T, S snapshots (dumpFreq = 1 day) from a run directory,
merges them, keeps the first 7201 snapshots (the initial state plus 20 years
of daily output) and writes them to <run_dir>/states_20yrs.nc, the file the
ROM training reads. GRID_DIR is a directory with the MITgcm grid files
(RC.meta, ...), e.g. the spin-up run directory.

Usage:
    python make_states_nc.py RUN_DIR GRID_DIR
"""
import sys

import numpy as np
import xarray as xr
import xmitgcm

run_dir = sys.argv[1].rstrip('/') + '/'
grid_dir = sys.argv[2]

prefixes = ['U', 'V', 'Eta', 'T', 'S']
ds_list = []
for pfx in prefixes:
    ds_list.append(xmitgcm.open_mdsdataset(run_dir, grid_dir=grid_dir, read_grid=False, iters='all', prefix=[pfx],
                                           default_dtype=np.float32, delta_t=1200))

ds = xr.merge(ds_list)
ds.isel(time=slice(0, 7201)).to_netcdf(run_dir + 'states_20yrs.nc')
