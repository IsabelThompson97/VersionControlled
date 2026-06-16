#!/usr/bin/env python3
"""
we_trends.py  (E1 + E2 + E3)

Per-iteration diagnostics, read straight from west.h5 (robust to west.log being
overwritten by run.sh). Produces a 4-panel figure and prints a text table that
the analyst report embeds.

Panels:
  E1  Occupied bins vs iteration   -> convergence of coverage
  E2  Segments (n_particles) vs it -> walker-count / explosion watch
  E3  Dynamic range (kT) vs it     -> how far probability is spreading
      Walltime (h) vs iteration    -> cost per iteration

Run from the trial root (after `source env.sh`):
    python3 analysis/scripts/we_trends.py
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import we_lib as L


def main():
    p = L.paths()
    os.makedirs(p["analysis"], exist_ok=True)
    h5, running = L.data_file()

    summ = L.iter_summary(h5)
    # drop any trailing not-yet-run iteration (WESTPA pre-creates the next group)
    ncomp = L.last_completed_iter(h5)
    keep = summ["iters"] <= ncomp
    summ = {k: v[keep] for k, v in summ.items()}
    parsed = L.parse_bins_log()
    edges = parsed["edges"]
    if edges:
        it_occ, occ = L.occupied_per_iter(edges, h5)
    else:
        it_occ, occ = np.array([]), np.array([])

    fig, ax = plt.subplots(2, 2, figsize=(11, 8))
    fig.suptitle(f"WE iteration trends — {os.path.basename(p['root'])}"
                 + ("  [westBackup.h5]" if running else ""), fontsize=12)

    ax[0, 0].plot(it_occ, occ, "o-", color="#2b8cbe")
    ax[0, 0].set(title="E1  Occupied bins", xlabel="iteration", ylabel="occupied bins")

    ax[0, 1].plot(summ["iters"], summ["n_particles"], "o-", color="#d95f0e")
    ax[0, 1].set(title="E2  Segments per iteration", xlabel="iteration", ylabel="n_particles")

    ax[1, 0].plot(summ["iters"], summ["dynrange_kT"], "o-", color="#31a354")
    ax[1, 0].set(title="E3  Dynamic range", xlabel="iteration", ylabel="kT")

    ax[1, 1].plot(summ["iters"], summ["walltime_h"], "o-", color="#756bb1")
    ax[1, 1].set(title="Wallclock per iteration", xlabel="iteration", ylabel="hours")

    for a in ax.flat:
        a.grid(alpha=0.3)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out = os.path.join(p["analysis"], "we_trends.pdf")
    fig.savefig(out, dpi=150)
    print(f"wrote {out}")

    # text table for the report
    print("\n--- iteration trend table ---")
    print(f"{'iter':>4} {'segments':>9} {'occ_bins':>9} {'dyn_kT':>7} {'wall_h':>7}")
    occ_map = dict(zip(it_occ.tolist(), occ.tolist()))
    for i, it in enumerate(summ["iters"]):
        ob = occ_map.get(int(it), "")
        print(f"{int(it):>4} {int(summ['n_particles'][i]):>9} {str(ob):>9} "
              f"{summ['dynrange_kT'][i]:>7.2f} {summ['walltime_h'][i]:>7.2f}")


if __name__ == "__main__":
    main()
