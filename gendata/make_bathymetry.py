"""Make the SOMA bathymetry for the 1/4-degree grid (bathy4.bin).

The basin is the SOMA bowl (Wolfram et al. 2015): a 3500 m deep circular
basin with a 100 m shelf and a tanh slope, centred at (30E, 45N) with a
28-degree radius, evaluated on the 248 x 248 tracer grid.

Usage:
    python make_bathymetry.py [--out-dir DIR]
"""
import argparse
from pathlib import Path

import numpy as np

import soma_grid as g

HO = 3400       # depth of ocean - Hshelf (m)
HSHELF = 100    # shelf depth (m)
PHI = 0.02      # controls slope steepness (slope width as fraction of domain)
RADIUS = 28     # basin radius (degrees)
SHELF_EDGE = 0.14   # shelf extends to hh = -SHELF_EDGE beyond the slope


def soma_bathymetry():
    Y, X = g.tracer_grid()
    d = np.linalg.norm(np.array([X - g.XC, Y - g.YC]), axis=0)
    hh = 1 - np.square(d / RADIUS)
    return (-HSHELF - HO / 2 * (1 + np.tanh(hh / PHI))) * np.heaviside(hh + SHELF_EDGE, 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out-dir', default='input_binaries', help='output directory')
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    h = soma_bathymetry()

    path = out_dir / 'bathy4.bin'
    g.write_field(path, h)
    print(f'wrote {path}  shape {h.shape}  depth {h.min():.1f} to {h.max():.1f} m')


if __name__ == '__main__':
    main()
