"""Shared grid constants and I/O for the 1/4-degree SOMA input binaries.

The model grid (input/data, PARM04) is 248 x 248 points at 0.25 degrees,
xgOrigin=-1, ygOrigin=14. Time-varying forcing files hold one record per
model time step over one 360-day year (externForcingPeriod = deltaT = 1200 s,
externForcingCycle = 31104000 s), i.e. 25920 records of 248 x 248.

All binaries are big-endian float32, as MITgcm expects (readBinaryPrec=32).
"""
import numpy as np

NX = 248            # gridpoints in x
NY = 248            # gridpoints in y
DX = 0.25           # grid spacing in x (degrees longitude)
DY = 0.25           # grid spacing in y (degrees latitude)
XO = 0              # origin in x,y for ocean domain
YO = 15             # (i.e. southwestern corner of ocean domain)
XC = 30             # domain center in x
YC = 45             # and in y
XEAST = XO + (NX - 8) * DX     # eastern extent of ocean domain
YNORTH = YO + (NY - 8) * DY    # northern extent of ocean domain

DELTA_T = 1200                              # model time step (s), deltaT in input/data
SEC_PER_MONTH = 30 * 24 * 3600              # 360-day calendar
NT_PER_MONTH = SEC_PER_MONTH // DELTA_T     # 2160 records per month
N_MONTHS = 12


def tracer_grid():
    """(Y, X) on tracer points, shape (NY, NX)."""
    x = np.linspace(XO, XEAST, NX)
    y = np.linspace(YO, YNORTH, NY)
    return np.meshgrid(y, x, indexing='ij')


def monthly_cosine(vmin, vmax):
    """12 monthly values on a cosine that is vmax in January and vmin mid-year. """
    phase = np.linspace(0, 2 * np.pi, N_MONTHS)
    return (vmax - vmin) / 2 * np.cos(phase) + (vmax + vmin) / 2


def write_field(path, field):
    """Write one 2-D field as big-endian float32."""
    np.asarray(field, dtype='>f4').tofile(path)


def write_monthly_records(path, monthly_fields):
    """Write a 1-year forcing file: each monthly 2-D field repeated NT_PER_MONTH times."""
    with open(path, 'wb') as f:
        for field in monthly_fields:
            rec = np.asarray(field, dtype='>f4').tobytes()
            for _ in range(NT_PER_MONTH):
                f.write(rec)
