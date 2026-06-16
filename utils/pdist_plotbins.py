#!/usr/bin/env python3
"""
Overlay WE bin boundaries on a fine-grid w_pdist free-energy surface.

Workflow:
    w_pdist -W westBackup.h5 -b '[100, 100]'   # fine UNIFORM grid, auto-ranged
    python pdist_plotbins.py                   # this script

The histogram uses 100 uniform bins per dimension over the EXPLORED region
(fine resolution where the density actually lives). The WE bin boundaries are
drawn as overlaid lines, and the viewport is forced to the full WE domain so
boundaries sitting over unexplored space are visible rather than cropped out.
"""

import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# ---------------------------------------------------------------------------
# WE bin boundaries — source of truth for both the overlay and the axis limits
# ---------------------------------------------------------------------------
we_bounds_x = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25,
                        3.5, 3.75, 4.0, 4.25, 4.5, 4.75, 5.0, 5.1, 5.2, 5.3,
                        5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.0, 6.1, 6.2, 6.3,
                        6.4, 6.5, 6.6, 6.7, 6.8, 6.9, 7.0, 7.25, 7.5, 7.75,
                        8.0, 8.5, 9.0, 9.5, 10.0, 11.0, 12.0, 14.0, 16.0,
                        18.0, 20.0, 22.0, 25.0])
we_bounds_y = np.array([0.0, 1.0, 1.25, 1.5, 1.75, 2.0, 2.1, 2.2, 2.3, 2.4,
                        2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.25, 3.5, 3.75, 4.0,
                        4.25, 4.5, 4.75, 5.0, 5.25, 5.5, 5.75, 6.0, 6.25,
                        6.5, 6.75, 7.0, 7.25, 7.5, 7.75, 8.0, 8.25, 8.5,
                        8.75, 9.0, 9.25, 9.5, 9.75, 10.0])

PDIST_FILE = 'pdist.h5'
OUT_FILE   = 'pdist_with_bins.png'

# ---------------------------------------------------------------------------
# Read the fine-grid histogram and its (uniform, auto-ranged) edges
# ---------------------------------------------------------------------------
with h5py.File(PDIST_FILE, 'r') as f:
    # histograms shape is typically (n_iters, nbins_x, nbins_y)
    hist    = f['histograms'][:]
    edges_x = f['binbounds_0'][:]
    edges_y = f['binbounds_1'][:]

# Average over iterations to get a single 2D distribution.
# NOTE: this mixes the transient WE distributions over the whole run; it is a
# fine visual diagnostic but is NOT a RiteWeight-corrected equilibrium FES.
P = hist.mean(axis=0)
P = np.ma.masked_where(P <= 0, P)

F  = -np.log(P)            # free energy in units of kT, up to a constant
F -= F.min()

# ---------------------------------------------------------------------------
# Plot: fine grid as heatmap, WE boundaries as overlaid lines
# ---------------------------------------------------------------------------
# Distinguish explored-but-low-density (masked, inside mesh -> "bad" color)
# from never-explored (outside mesh -> axes facecolor).
cmap = mpl.colormaps['viridis'].copy()
cmap.set_bad('lightgray')

fig, ax = plt.subplots(figsize=(8, 6))
ax.set_facecolor('white')   # never-explored space reads white

# pcolormesh respects the explicit edges; .T fixes the axis-order convention
# (w_pdist stores progress coord 0 as the leading array axis = screen rows).
mesh = ax.pcolormesh(edges_x, edges_y, F.T, shading='flat', cmap=cmap)
fig.colorbar(mesh, ax=ax, label=r'$F\ /\ k_BT$')

# Overlay the WE bin boundaries
for xb in we_bounds_x:
    ax.axvline(xb, color='black', lw=0.4, alpha=0.4)
for yb in we_bounds_y:
    ax.axhline(yb, color='black', lw=0.4, alpha=0.4)

# Force the viewport to the FULL WE domain, driven from the boundary arrays
# so the frame can never drift out of sync with the binning scheme.
ax.set_xlim(we_bounds_x.min(), we_bounds_x.max())   # 0.0 -> 25.0
ax.set_ylim(we_bounds_y.min(), we_bounds_y.max())   # 0.0 -> 10.0

ax.set_xlabel('progress coordinate 0')
ax.set_ylabel('progress coordinate 1')

plt.tight_layout()
plt.savefig(OUT_FILE, dpi=200)
print(f'wrote {OUT_FILE}')
