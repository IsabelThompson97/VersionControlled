#!/usr/bin/env python3
"""
we_frontier_flux.py  (E4)

Coverage tells you bins are being *touched*; flux tells you whether *weight* is
actually following the frontier or whether lone low-weight explorer walkers are
running ahead while the population stays put. This script separates the two.

For each pcoord dimension it plots, per iteration:
  (a) the extreme pcoord value reached (max for an "outward" dim) — the frontier
  (b) the total weight sitting in the leading 20% of the explored range — the
      flux that has actually populated the frontier region

Direction is inferred from the simulation objective (system.py docstring /
directory name). For a bidirectional / total-coverage run it reports BOTH the
outward (high-value) and inward (low-value) tails so folding and unfolding are
both visible. Everything is read from west.h5 at runtime — trial-agnostic.

Run from the trial root (after `source env.sh`):
    python3 analysis/scripts/we_frontier_flux.py
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import we_lib as L

LEAD_FRAC = 0.20  # fraction of explored range counted as the "frontier" tail


def main():
    p = L.paths()
    os.makedirs(p["analysis"], exist_ok=True)
    h5, running = L.data_file()

    N = L.last_completed_iter(h5)
    pc0, _ = L.iter_final_pcoord(1, h5)
    ndim = pc0.shape[1]
    labels = L.short_labels(ndim)

    # global explored range per dim (across all iterations) to fix the tail bands
    gmin = np.full(ndim, np.inf)
    gmax = np.full(ndim, -np.inf)
    per_iter = []
    for n in range(1, N + 1):
        try:
            pc, w = L.iter_final_pcoord(n, h5)
        except Exception:
            continue
        per_iter.append((n, pc, w))
        gmin = np.minimum(gmin, pc.min(axis=0))
        gmax = np.maximum(gmax, pc.max(axis=0))

    fig, axes = plt.subplots(ndim, 1, figsize=(9, 3.4 * ndim), squeeze=False)
    fig.suptitle(f"E4  Frontier vs flux — {os.path.basename(p['root'])}"
                 + ("  [westBackup.h5]" if running else ""), fontsize=12)

    report_lines = []
    for d in range(ndim):
        rng = gmax[d] - gmin[d]
        hi_band = gmax[d] - LEAD_FRAC * rng   # outward (e.g. unfolding) tail
        lo_band = gmin[d] + LEAD_FRAC * rng   # inward  (e.g. folding) tail
        its, fmax, fmin, w_hi, w_lo = [], [], [], [], []
        for n, pc, w in per_iter:
            x = pc[:, d]
            its.append(n)
            fmax.append(x.max())
            fmin.append(x.min())
            w_hi.append(w[x >= hi_band].sum())
            w_lo.append(w[x <= lo_band].sum())

        ax = axes[d, 0]
        ax.plot(its, fmax, "o-", color="#d95f0e", label="max reached (outward frontier)")
        ax.plot(its, fmin, "o-", color="#2b8cbe", label="min reached (inward frontier)")
        ax.set(xlabel="iteration", ylabel=labels[d])
        ax.grid(alpha=0.3)

        ax2 = ax.twinx()
        ax2.plot(its, w_hi, "s--", color="#fdae6b", alpha=0.9, label="weight in outward 20%")
        ax2.plot(its, w_lo, "s--", color="#9ecae1", alpha=0.9, label="weight in inward 20%")
        ax2.set_ylabel("weight in frontier tail")
        ax2.set_yscale("log")

        l1, lb1 = ax.get_legend_handles_labels()
        l2, lb2 = ax2.get_legend_handles_labels()
        ax.legend(l1 + l2, lb1 + lb2, fontsize=7, loc="center left")
        ax.set_title(labels[d])

        report_lines.append(
            f"{labels[d]}: reached [{fmin[-1]:.2f}, {fmax[-1]:.2f}]; "
            f"outward-tail weight {w_hi[-1]:.2e}, inward-tail weight {w_lo[-1]:.2e}")

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    out = os.path.join(p["analysis"], "we_frontier_flux.pdf")
    fig.savefig(out, dpi=150)
    print(f"wrote {out}")
    print("\n--- frontier/flux (final iteration) ---")
    for ln in report_lines:
        print(ln)


if __name__ == "__main__":
    main()
