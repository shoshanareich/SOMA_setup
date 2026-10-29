"""Make the seasonally varying zonal wind-stress file (zonalWindFile).

Spatial pattern (Wolfram et al. 2015 SOMA double-gyre wind), on (XG, YC) points:
    g(y) = (1 - xi*dy) * exp(-dy^2) * cos(pi*dy),  dy = (y - yc)/30,  xi = 0.5
Amplitude: a monthly cosine, (tau_max - tau_min)/2 * cos(phase) + (tau_max + tau_min)/2, in
N/m^2, with tau_max in January.
The file holds one 248 x 248 record per 1200 s time step for one year (~6.4 GB).

File name: wind_sv_{tau_min}_{tau_max}_cos_1200s_248.bin, the name that
input/data's zonalWindFile points to (the published runs used tau_min = 0.1 and
tau_max in 0.1, 0.2, 0.3, 0.4, 0.5).

Usage:
    python make_wind.py --tau-max 0.4 [--tau-min 0.1] [--out-dir DIR]
"""
import argparse
from pathlib import Path

import numpy as np

import soma_grid as g

XI = 0.5            # north-south asymmetry of the wind pattern

WIND_YO = 14
WIND_YNORTH = WIND_YO + (g.NY - 8) * g.DY


def wind_pattern():
    """Unit-amplitude zonal wind-stress pattern, shape (NY, NX)."""
    x = np.linspace(g.XO - g.DX, g.XEAST, g.NX)
    y = np.linspace(WIND_YO - g.DY, WIND_YNORTH, g.NY) + g.DY / 2
    Y, _ = np.meshgrid(y, x, indexing='ij')     # zonal wind-stress on (XG,YC) points
    delY = (Y - g.YC) / 30
    return (1 - XI * delY) * np.exp(-np.square(delY)) * np.cos(np.pi * delY)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--tau-max', type=float, required=True,
                        help='peak (January) wind-stress amplitude, N/m^2')
    parser.add_argument('--tau-min', type=float, default=0.1,
                        help='trough of the seasonal cosine, N/m^2 (default 0.1)')
    parser.add_argument('--out-dir', default='input_binaries', help='output directory')
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    pattern = wind_pattern()
    amps = g.monthly_cosine(args.tau_min, args.tau_max)

    path = out_dir / f'wind_sv_{args.tau_min}_{args.tau_max}_cos_{g.DELTA_T}s_{g.NX}.bin'
    g.write_monthly_records(path, [a * pattern for a in amps])
    print(f'wrote {path}  monthly amplitude {amps.min():.3f} to {amps.max():.3f} N/m^2')


if __name__ == '__main__':
    main()
