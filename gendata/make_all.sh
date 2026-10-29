#!/bin/bash
# Make every input binary used by the paper runs (~45 GB in total):
# bathymetry, SST/SSS restoring, and the five wind scenarios
# (tau_min = 0.1, tau_max = 0.1 ... 0.5).
#
# Usage: bash gendata/make_all.sh [OUT_DIR]   (default: input_binaries)
set -e
here=$(cd "$(dirname "$0")" && pwd)
out=${1:-input_binaries}

python "$here/make_bathymetry.py" --out-dir "$out"
python "$here/make_relaxation.py" --out-dir "$out"
for tau_max in 0.1 0.2 0.3 0.4 0.5; do
    python "$here/make_wind.py" --tau-min 0.1 --tau-max "$tau_max" --out-dir "$out"
done
