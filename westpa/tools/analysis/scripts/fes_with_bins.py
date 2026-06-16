#!/usr/bin/env python3
"""
fes_with_bins.py  (E5 + E6)

A free-energy surface that never drifts out of sync with the binning scheme and
re-orients itself to whatever trial it is dropped into.

  E5  WE bin boundaries are read from progress_logs/bins.log (which is generated
      FROM system.py), so the overlaid grid always matches the real mapper — no
      hardcoded boundary arrays to fall stale (the bug in the old pdist_plotbins.py).
  E6  Folded / unfolded reference points and the axis labels are parsed from this
      trial's system.py docstring at runtime (fallback: west.cfg states), so
      moving the script to a new trial directory automatically re-annotates it
      with that trial's references and coordinate names.

The 2D histogram is computed directly from west.h5 (final pcoord points, weighted),
so no pdist.h5 file or fixed grid is required.

Run from the trial root (after `source env.sh`):
    python3 analysis/scripts/fes_with_bins.py
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import we_lib as L

NBINS_FINE = 100  # fine uniform grid for the density itself


def main():
    p = L.paths()
    os.makedirs(p["analysis"], exist_ok=True)
    h5, running = L.data_file()

    # --- gather all final pcoord points + weights across iterations ---
    N = L.last_completed_iter(h5)
    allpc, allw = [], []
    for n in range(1, N + 1):
        try:
            pc, w = L.iter_final_pcoord(n, h5)
        except Exception:
            continue
        allpc.append(pc)
        allw.append(w)
    pc = np.vstack(allpc)
    w = np.concatenate(allw)
    ndim = pc.shape[1]
    if ndim < 2:
        print("FES plot needs >=2 pcoord dims; got", ndim)
        return

    labels = L.short_labels(ndim)

    # --- WE boundaries (E5) from bins.log ---
    parsed = L.parse_bins_log()
    edges = parsed["edges"]

    # --- fine weighted 2D histogram over the explored region ---
    x, y = pc[:, 0], pc[:, 1]
    H, xe, ye = np.histogram2d(x, y, bins=NBINS_FINE, weights=w)
    P = np.ma.masked_where(H <= 0, H)
    with np.errstate(divide="ignore", invalid="ignore"):
        F = -np.log(P)
    F -= F.min()

    cmap = mpl.colormaps["viridis"].copy()
    cmap.set_bad("lightgray")

    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    ax.set_facecolor("white")
    mesh = ax.pcolormesh(xe, ye, F.T, shading="auto", cmap=cmap)
    fig.colorbar(mesh, ax=ax, label=r"$F\ /\ k_BT$")

    # E5 overlay: WE bin boundaries from bins.log
    if len(edges) >= 2:
        for xb in edges[0]:
            ax.axvline(xb, color="black", lw=0.3, alpha=0.30)
        for yb in edges[1]:
            ax.axhline(yb, color="black", lw=0.3, alpha=0.30)
        ax.set_xlim(edges[0].min(), edges[0].max())
        ax.set_ylim(edges[1].min(), edges[1].max())

    # E6 annotation: reference points parsed at runtime
    refs = L.reference_points()
    for name, marker, color in (("folded", "*", "white"), ("unfolded", "X", "red")):
        coords = refs.get(name)
        if coords and len(coords) >= 2 and None not in coords[:2]:
            ax.scatter([coords[0]], [coords[1]], marker=marker, s=240,
                       edgecolors="black", linewidths=1.2, color=color, zorder=5)
            ax.annotate(f"{name}\n({coords[0]:.1f}, {coords[1]:.1f})",
                        (coords[0], coords[1]), textcoords="offset points",
                        xytext=(8, 8), fontsize=8, color="black",
                        bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7))

    ax.set_xlabel(labels[0])
    ax.set_ylabel(labels[1])
    ax.set_title(f"FES + WE bins — {os.path.basename(p['root'])}\n"
                 f"refs: {refs['source']}" + ("  [westBackup.h5]" if running else ""),
                 fontsize=10)

    fig.tight_layout()
    out = os.path.join(p["analysis"], "fes_with_bins.png")
    fig.savefig(out, dpi=200)
    print(f"wrote {out}")
    print(f"reference source: {refs['source']}  folded={refs.get('folded')}  "
          f"unfolded={refs.get('unfolded')}")


if __name__ == "__main__":
    main()
