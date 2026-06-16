#!/usr/bin/env python3
"""
we_kinetics.py  (E7)

Estimate inter-state rate constants with the WESTPA direct (Bayesian bootstrap)
estimator, using whatever macrostates the trial defines in west.cfg
analysis_schemes. This is only meaningful once there are repeated transitions
between states; with few iterations or a downhill (one-way) process the result
will be noisy or empty. The script ALWAYS reports honestly which case it is in
rather than printing a misleading number.

Pipeline (all read trial files at runtime):
    w_assign --config-from-file --scheme <scheme>   -> assign.h5
    w_direct all --config-from-file --scheme <scheme> -> direct.h5
then summarise rate_evolution (final cumulative estimate) per state pair.

Run from the trial root (after `source env.sh`):
    python3 analysis/scripts/we_kinetics.py
"""
import os
import re
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import we_lib as L


def first_scheme():
    cfg = L._read(L.paths()["cfg"])
    m = re.search(r"analysis_schemes:\s*\n\s*(\w+):", cfg)
    return m.group(1) if m else None


def run(cmd, cwd=None):
    print(f"  $ {' '.join(cmd)}" + (f"   (cwd={cwd})" if cwd else ""))
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return r.returncode, (r.stdout + r.stderr)


def main():
    p = L.paths()
    os.makedirs(p["analysis"], exist_ok=True)
    h5, running = L.data_file()
    if running:
        print("NOTE: run appears live — using", os.path.basename(h5))
    scheme = first_scheme()
    if not scheme:
        print("E7 kinetics: no analysis_schemes found in west.cfg — skipping.")
        return
    print(f"E7 kinetics: scheme '{scheme}', data {os.path.basename(h5)}")

    # with --config-from-file --scheme, WESTPA writes into <analysis_dir>/<scheme>/
    # and that subdirectory must already exist.
    scheme_dir = os.path.join(p["analysis"], scheme)
    os.makedirs(scheme_dir, exist_ok=True)
    assign = os.path.join(scheme_dir, "assign.h5")
    direct = os.path.join(scheme_dir, "direct.h5")

    # w_assign reads states/bins from west.cfg's scheme and writes into the scheme dir
    rc, out = run(["w_assign", "-W", h5, "--config-from-file", "--scheme", scheme])
    if rc != 0:
        print("  w_assign failed — kinetics unavailable:\n", out[-600:])
        return
    # w_direct uses a plain CLI (no --scheme). Its 'all' sub-steps re-open the
    # output by its default relative name, so run inside the scheme dir with
    # relative filenames and an absolute -W.
    rc, out = run(["w_direct", "all", "-W", h5, "-a", "assign.h5", "-o", "direct.h5"],
                  cwd=scheme_dir)
    if rc != 0:
        print("  w_direct failed — likely too few transitions for a rate estimate.")
        print(out[-600:])
        return

    try:
        import h5py
        import numpy as np
        with h5py.File(direct, "r") as f:
            if "rate_evolution" not in f:
                print("  direct.h5 has no rate_evolution — insufficient transitions.")
                return
            re_ds = f["rate_evolution"][:]
            labels = [s.decode() if isinstance(s, bytes) else str(s)
                      for s in f["state_labels"][:]] if "state_labels" in f else None
        last = re_ds[-1]  # final cumulative window, shape (nstates, nstates)
        print("\n--- rate constants (final cumulative estimate) ---")
        ns = last.shape[0]
        names = labels or [f"s{i}" for i in range(ns)]
        any_nonzero = False
        for i in range(ns):
            for j in range(ns):
                if i == j:
                    continue
                val = last[i, j]["expected"] if last.dtype.names else last[i, j]
                if np.isfinite(val) and val > 0:
                    any_nonzero = True
                print(f"  k({names[i]} -> {names[j]}) = {val:.4e} (1/tau)")
        if not any_nonzero:
            print("  All rates zero/undefined — no completed transitions yet. "
                  "Rate estimates need repeated recrossings; revisit after more iterations.")
    except Exception as e:
        print(f"  could not parse direct.h5: {e}")


if __name__ == "__main__":
    main()
