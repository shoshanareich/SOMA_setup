"""Make the SST and SSS restoring fields (thetaClimFile, saltClimFile).

SST: linear in latitude from Tmax at the southern edge to Tmin = -1.8 C at the
northern edge. Tmax follows a monthly cosine between 25 C and 30 C (warmest
mid-year), giving SST_relax_change_max_1200s_248.bin.

SSS: time-independent, linear in latitude from 36 psu (south) to 35 psu
(north), repeated over the year, giving SSS_relax_yrly_1200s_248.bin.

Both files hold one 248 x 248 record per 1200 s time step for one year
(~6.4 GB each).

Usage:
    python make_relaxation.py [--out-dir DIR] [--only sst|sss]
"""
import argparse
from pathlib import Path

import numpy as np

import soma_grid as g

TMAX_LO = 25.0      # southern-edge restoring SST, January (C)
TMAX_HI = 30.0      # southern-edge restoring SST, mid-year (C)
TMIN = -1.8         # northern-edge restoring SST (C)
SMAX = 36.0         # southern-edge restoring SSS (psu)
SMIN = 35.0         # northern-edge restoring SSS (psu)


def sst_monthly(Y):
    # Tmax is lowest in January (opposite phase to the wind); December = January,
    phase = np.linspace(0, 2 * np.pi, g.N_MONTHS)
    tmax = -(TMAX_HI - TMAX_LO) / 2 * np.cos(phase) + (TMAX_HI + TMAX_LO) / 2
    return [(t - TMIN) / (g.NY - 2) / g.DY * (g.YNORTH - Y) + TMIN for t in tmax]


def sss(Y):
    return (SMAX - SMIN) / (g.NY - 2) / g.DY * (g.YNORTH - Y) + SMIN


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out-dir', default='input_binaries', help='output directory')
    parser.add_argument('--only', choices=['sst', 'sss'], help='write just one of the two files')
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    Y, _ = g.tracer_grid()

    if args.only in (None, 'sst'):
        path = out_dir / f'SST_relax_change_max_{g.DELTA_T}s_{g.NX}.bin'
        g.write_monthly_records(path, sst_monthly(Y))
        print(f'wrote {path}')

    if args.only in (None, 'sss'):
        path = out_dir / f'SSS_relax_yrly_{g.DELTA_T}s_{g.NX}.bin'
        g.write_monthly_records(path, [sss(Y)] * g.N_MONTHS)
        print(f'wrote {path}')


if __name__ == '__main__':
    main()
