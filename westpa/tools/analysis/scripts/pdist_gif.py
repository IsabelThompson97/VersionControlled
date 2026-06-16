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

import os
import sys
import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')                 # headless: no display needed (CRC-safe)
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.animation import FuncAnimation, PillowWriter

# WE bin boundaries + axis labels are pulled automatically from this trial's
# files (progress_logs/bins.log + system.py) via the co-located we_lib — no
# ~/.claude dependency, nothing hardcoded per trial. we_lib.sim_root() walks up
# from the CWD to find west.cfg, so this works from the trial root, analysis/,
# or analysis/scripts/.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import we_lib as L
_edges  = L.parse_bins_log()['edges']
_labels = L.short_labels(len(_edges) if _edges else 2)

# ===========================================================================
# CONFIG
# ===========================================================================
# Resolve I/O under the trial's analysis/ dir so outputs land there regardless of
# cwd (run from the trial root via run_all.sh, or standalone from analysis/).
_adir        = L.paths()['analysis']
PDIST_FILE   = os.path.join(_adir, 'pdist.h5')
OUT_FILE     = os.path.join(_adir, 'pdist_evolution.gif')

XLABEL       = _labels[0]             # pcoord 0 label (from system.py)
YLABEL       = _labels[1]             # pcoord 1 label (from system.py)

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
# Pulled from bins.log via we_lib above, so they always match system.py.
WE_BOUNDS_X = _edges[0] if len(_edges) >= 2 else None
WE_BOUNDS_Y = _edges[1] if len(_edges) >= 2 else None

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