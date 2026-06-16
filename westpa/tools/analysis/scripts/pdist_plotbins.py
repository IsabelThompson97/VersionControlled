#!/usr/bin/env python3
"""
Overlay WE bin boundaries on a fine-grid w_pdist free-energy surface.

Workflow:
    w_pdist -W westBackup.h5 -b '[100, 100]'   # fine UNIFORM grid, auto-ranged
    python pdist_plotbins.py             # this script

The histogram uses 100 uniform bins per dimension over the EXPLORED region
(fine resolution where the density actually lives). The WE bin boundaries are
drawn as overlaid lines, and the viewport is forced to the full WE domain so
boundaries sitting over unexplored space are visible rather than cropped out.
"""

import os
import sys
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# ---------------------------------------------------------------------------
# WE bin boundaries — pulled automatically from progress_logs/bins.log via the
# co-located we_lib (no ~/.claude dependency), so they ALWAYS match system.py
# and re-derive themselves in whatever trial this script is dropped into.
# we_lib.sim_root() walks up from the CWD to find west.cfg, so this works run
# from the trial root, from analysis/, or from analysis/scripts/.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import we_lib as L

_parsed = L.parse_bins_log()              # reads <trial>/progress_logs/bins.log
_edges  = _parsed['edges']
if len(_edges) < 2:
    raise SystemExit("bins.log has no bin boundaries — run `w_bins info "
                     "--detail --bins-from-system > progress_logs/bins.log` first.")
we_bounds_x = _edges[0]                    # pcoord 0 boundaries (e.g. MinDist)
we_bounds_y = _edges[1]                    # pcoord 1 boundaries (e.g. RMSD-Loop)
_labels = L.short_labels(len(_edges))      # axis labels parsed from system.py

# Resolve I/O under the trial's analysis/ dir so outputs land there no matter the
# cwd (run from the trial root via run_all.sh, or standalone from analysis/).
_adir = L.paths()['analysis']
PDIST_FILE = os.path.join(_adir, 'pdist.h5')
OUT_FILE   = os.path.join(_adir, 'pdist_with_bins.png')

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
ax.set_xlim(we_bounds_x.min(), we_bounds_x.max())   # full WE domain (from bins.log)
ax.set_ylim(we_bounds_y.min(), we_bounds_y.max())   # full WE domain (from bins.log)

ax.set_xlabel(_labels[0])
ax.set_ylabel(_labels[1])

plt.tight_layout()
plt.savefig(OUT_FILE, dpi=200)
print(f'wrote {OUT_FILE}')