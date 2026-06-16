#!/usr/bin/env python3
"""
Animate the WE probability density as iteration time increases.

Each frame is the transient distribution p(x, t_i) at one iteration (optionally
smoothed over a short trailing window), rendered as a free-energy surface
F = -ln p. Unlike `plothist average` over the whole run, this shows the
distribution *moving* rather than collapsing it into a single time-average.

Reads the per-iteration histogram stack directly from pdist.h5 (shape
(n_iter, nbins_x, nbins_y)), so it does NOT shell out to plothist per frame.

Prerequisite:
    w_pdist -W westBackup.h5 -b '[100, 100]'   # or your chosen binning

Usage:
    python pdist_gif.py
Adjust the CONFIG block below.
"""

import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')                 # headless: no display needed (CRC-safe)
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.animation import FuncAnimation, PillowWriter

# ===========================================================================
# CONFIG
# ===========================================================================
PDIST_FILE   = 'pdist.h5'
OUT_FILE     = 'pdist_evolution.gif'

XLABEL       = r'RMSD to Stem (Å)'
YLABEL       = r'RMSD to Loop (Å)'

# Frame smoothing: each frame averages a trailing window of this many
# iterations. WINDOW=1 -> pure single-iteration frames (noisy but honest).
# Keep small; large windows reintroduce the non-stationary-average smear.
WINDOW       = 1

# Subsample iterations for the frame sequence (1 = every iteration).
# Use >1 if you have hundreds of iterations and want a shorter GIF.
STRIDE       = 1

# First WE iteration number corresponding to array index 0 of `histograms`.
# If w_pdist was run over the full run starting at iteration 1, set 1.
# If you ran w_pdist over a sub-range, set its --first-iter. Used only for
# the on-frame iteration label; auto-overridden if the file stores iter ids.
ITER_OFFSET  = 1

FPS          = 8         # playback speed
DPI          = 130

# WE bin boundaries to overlay (set to None to skip the overlay).
WE_BOUNDS_X = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25,
                        3.5, 3.75, 4.0, 4.25, 4.5, 4.75, 5.0, 5.1, 5.2, 5.3,
                        5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3,
                        6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.25, 7.5, 7.75,
                        8.0, 8.5, 9.0, 9.5, 10.0, 11.0, 12.0, 14.0, 16.0,
                        18.0, 20.0, 22.0, 25.0])
WE_BOUNDS_Y = np.array([0.0, 1.0, 1.25, 1.5, 1.75, 2.0, 2.1, 2.2, 2.3, 2.4,
                        2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.25, 3.5, 3.75, 4.0,
                        4.25, 4.5, 4.75, 5.0, 5.25, 5.5, 5.75, 6.0, 6.25,
                        6.5, 6.75, 7.0, 7.25, 7.5, 7.75, 8.0, 8.25, 8.5,
                        8.75, 9.0, 9.25, 9.5, 9.75, 10.0])

# ===========================================================================
# Read the per-iteration histogram stack and the bin edges
# ===========================================================================
with h5py.File(PDIST_FILE, 'r') as f:
    hist    = f['histograms'][:]          # (n_iter, nbins_x, nbins_y)
    edges_x = f['binbounds_0'][:]
    edges_y = f['binbounds_1'][:]
    # WESTPA usually stores the actual iteration numbers; use them if present
    if 'n_iter' in f:
        iter_ids = f['n_iter'][:]
    else:
        iter_ids = None

n_iter = hist.shape[0]
print(f'loaded histogram stack: {hist.shape}  '
      f'({n_iter} iterations, grid {hist.shape[1]}x{hist.shape[2]})')

# Frame indices into the stack (array indices, 0-based)
frame_idx = list(range(0, n_iter, STRIDE))

def label_for(arr_idx):
    """Return the WE iteration number to print on the frame."""
    if iter_ids is not None and arr_idx < len(iter_ids):
        return int(iter_ids[arr_idx])
    return arr_idx + ITER_OFFSET

# ===========================================================================
# Pre-compute every frame's F surface so we can lock a GLOBAL color scale.
# A per-frame color scale would make rescaling masquerade as real motion.
# ===========================================================================
def frame_F(arr_idx):
    """Free energy surface for the trailing window ending at arr_idx."""
    lo = max(0, arr_idx - WINDOW + 1)
    P = hist[lo:arr_idx + 1].mean(axis=0)      # window mean; WINDOW=1 -> single iter
    P = np.ma.masked_where(P <= 0, P)
    F = -np.log(P)
    return F

F_frames = [frame_F(i) for i in frame_idx]

# Global F range from real (finite) values across ALL frames.
finite_vals = np.concatenate([F.compressed() for F in F_frames if F.count() > 0])
finite_vals -= finite_vals.min()             # shift global minimum to 0
GLOBAL_MIN  = 0.0
# Cap the top so a few single-count cells don't blow out the scale.
# 99th percentile is a reasonable, honest ceiling; raise if you want the tails.
GLOBAL_MAX  = np.percentile(finite_vals, 99)
print(f'global F range locked to [0, {GLOBAL_MAX:.2f}] kT '
      f'(99th pct; max raw was {finite_vals.max():.1f})')

# Re-shift each frame's F to the same global zero used for GLOBAL_MAX.
global_shift = min(F.min() for F in F_frames if F.count() > 0)
F_frames = [F - global_shift for F in F_frames]

# ===========================================================================
# Build the animation
# ===========================================================================
cmap = mpl.colormaps['viridis'].copy()
#cmap.set_bad('lightgray')                    # in-domain, zero-density cells

try:
    plt.rcParams['text.usetex'] = False      # keep \AA working via mathtext
except Exception:
    pass

fig, ax = plt.subplots(figsize=(8, 6))
ax.set_facecolor('white')

# Initial mesh (frame 0); .T fixes w_pdist's leading-axis = pcoord-0 convention
mesh = ax.pcolormesh(edges_x, edges_y, F_frames[0].T,
                     shading='flat', cmap=cmap,
                     vmin=GLOBAL_MIN, vmax=GLOBAL_MAX)
cbar = fig.colorbar(mesh, ax=ax, label=r'$F\ /\ k_BT$')

# Static WE bin overlay (drawn once; lines persist across frames)
if WE_BOUNDS_X is not None:
    for xb in WE_BOUNDS_X:
        ax.axvline(xb, color='black', lw=0.3, alpha=0.25)
    for yb in WE_BOUNDS_Y:
        ax.axhline(yb, color='black', lw=0.3, alpha=0.25)
    ax.set_xlim(WE_BOUNDS_X.min(), WE_BOUNDS_X.max())
    ax.set_ylim(WE_BOUNDS_Y.min(), WE_BOUNDS_Y.max())

ax.set_xlabel(XLABEL)
ax.set_ylabel(YLABEL)
title = ax.set_title('')

def update(frame_number):
    arr_idx = frame_idx[frame_number]
    F = F_frames[frame_number]
    # pcolormesh with shading='flat' wants the C array flattened to match quads
    mesh.set_array(F.T.ravel())
    win = f' (window {WINDOW})' if WINDOW > 1 else ''
    title.set_text(f'WE iteration {label_for(arr_idx)}{win}')
    return mesh, title

anim = FuncAnimation(fig, update, frames=len(frame_idx), blit=False)

writer = PillowWriter(fps=FPS)
anim.save(OUT_FILE, writer=writer, dpi=DPI)
print(f'wrote {OUT_FILE}  ({len(frame_idx)} frames @ {FPS} fps)')
