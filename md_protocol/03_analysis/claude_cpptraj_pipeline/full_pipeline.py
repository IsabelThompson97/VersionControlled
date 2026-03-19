"""
full_pipeline.py
================
Single end-to-end analysis pipeline for AMBER/cpptraj MD trajectories.

Stages
------
1. cpptraj     Run all .in scripts; copy each .dat → .txt
2. Process     Convert txt→csv, scale frames to ns, compute stats, save plots
3. eRMSD       barnaba eRMSD + heavy-atom RMSD vs. native; build master CSV
4. 2-D plots   Cross-metric scatter / histogram / contour suites

Usage
-----
Load your AMBER module first, then run:

    module load amber/24.0
    python full_pipeline.py

All configuration is in the labelled sections below.  To adapt this pipeline
to a new simulation, edit:

    TOTAL_NS            — simulation length in nanoseconds
    OUTPUT_FILE         — summary report filename
    CPPTRAJ_EXE         — path to cpptraj executable (default "cpptraj")
    CPPTRAJ_JOBS        — which .in scripts to run and which .dat to copy
    METRICS             — per-observable Python analysis
    ERMSD_CONFIG        — barnaba eRMSD calculation and master CSV assembly
    CROSS_METRIC_PLOTS  — 2-D cross-metric plot suites

Set ERMSD_CONFIG = None to skip Stage 3 and 4 entirely.
Set CPPTRAJ_JOBS = [] to skip Stage 1 (e.g. if cpptraj already ran).
"""

import os
import shutil
import subprocess
import sys
import time as _time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

import numpy as np
import pandas as pd

from cpptrajAnalysis import (
    append_to_output,
    convert_txt_to_csv,
    scale_x_to_ns,
    analyze_time_series,
    analyze_histogram_only,
    process_rdf,
    plot_2d_suite,
)


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION — edit everything in this section
# ══════════════════════════════════════════════════════════════════════════════

# ── Global settings ───────────────────────────────────────────────────────────

TOTAL_NS    = 1000                              # simulation length (ns)
OUTPUT_FILE = "analysis_output.txt"             # cumulative plain-text report
CPPTRAJ_EXE = "cpptraj"                         # path to cpptraj binary
FAIL_FAST   = False                             # True → abort on first cpptraj error


# ── Stage 1: cpptraj jobs ─────────────────────────────────────────────────────
# Each dict:
#   in_file  str            cpptraj input script to run
#   copies   list of tuples (source_dat, dest_txt) to copy after the run
#
# cpptraj jobs run sequentially in the order listed.
# Set CPPTRAJ_JOBS = [] to skip Stage 1 entirely.

CPPTRAJ_JOBS = [

    dict(
        in_file = "scripts/1_radiusGyr.in",
        copies  = [("radGyr.dat", "radGyr/radGyr.txt")],
    ),
    dict(
        in_file = "scripts/1_rmsdtoNMR.in",
        copies  = [("rmsd_toNMR.dat", "rmsd/rmsd_toNMR.txt")],
    ),
    dict(
        in_file = "scripts/1_rmsd.in",
        copies  = [("rmsd.dat", "rmsd/rmsd.txt")],
    ),
    dict(
        in_file = "scripts/1_minDistEnds.in",
        copies  = [("minDistEnds.dat", "minDist/minDistEnds.txt")],
    ),
    dict(
        in_file = "scripts/1_minDistLoopContacts.in",
        copies  = [
            ("minDistG9-U6.dat",              "minDist/minDistG9-U6.txt"),
            ("minDistG9-U6sugar-base.dat",    "minDist/minDistG9-U6sugar-base.txt"),
            ("minDistG9-U7sugar-base.dat",    "minDist/minDistG9-U7sugar-base.txt"),
            ("minDistU7-C8base-phosphate.dat","minDist/minDistU7-C8base-phosphate.txt"),
        ],
    ),
    dict(
        in_file = "scripts/1_rmsdtoNMRBackbone.in",
        copies  = [("rmsd_toNMRBackbone.dat", "rmsd/rmsd_toNMRBackbone.txt")],
    ),
    dict(
        in_file = "scripts/1_rmsdtoNMRStem.in",
        copies  = [("rmsd_toNMRStem.dat", "rmsd/rmsd_toNMRStem.txt")],
    ),
    dict(
        in_file = "scripts/1_rmsdtoNMRLoop.in",
        copies  = [("rmsd_toNMRLoop.dat", "rmsd/rmsd_toNMRLoop.txt")],
    ),
    dict(
        in_file = "scripts/1_rmsdtoNMR1-14Bases.in",
        copies  = [("rmsd_toNMR1-14Bases.dat", "rmsd/rmsd_toNMR1-14Bases.txt")],
    ),
    dict(
        in_file = "scripts/1_hbondFrames.in",
        copies  = [("hbondFrames.dat", "hbonds/hbondFrames.txt")],
    ),
    dict(
        in_file = "scripts/1_hbondsLifetimeLoop.in",
        copies  = [("hbondLifetimeLoop.dat", "hbonds/hbondLifetimeLoop.txt")],
    ),
    dict(
        in_file = "scripts/1_hbondsLifetime.in",
        copies  = [],   # outputs multiple files; no single .dat copy needed
    ),

    # ── Template: add new cpptraj jobs here ───────────────────────────────────
    # dict(
    #     in_file = "scripts/1_myNewObs.in",
    #     copies  = [("myNewObs.dat", "myNewObs/myNewObs.txt")],
    # ),

    # ── Ion RDF (commented out — uncomment if needed) ─────────────────────────
    # dict(
    #     in_file = "scripts/1_IonRDF.in",
    #     copies  = [
    #         ("RDF-Na.dat", "rdf/RDF-Na.txt"),
    #         ("RDF-Cl.dat", "rdf/RDF-Cl.txt"),
    #     ],
    # ),
]


# ── Stage 2: per-observable processing ───────────────────────────────────────
# Three metric types are supported:
#
#   "time_series"
#       Required: txt, csv, columns, y_column, title, unit, fig
#       Optional: y_label, hist, hist_fig, color, linewidth
#
#   "histogram_only"
#       Required: txt, csv, columns, y_column, title, unit, fig
#       Optional: bins, color, density
#
#   "rdf"
#       Required: ion1, txt1, ion2, txt2, csv, fig

METRICS = [

    # ── Radius of Gyration ────────────────────────────────────────────────────
    dict(
        type     = "time_series",
        txt      = "radGyr/radGyr.txt",
        csv      = "radGyr/radGyr.csv",
        columns  = ["Frame", "RadiusofGyration"],
        y_column = "RadiusofGyration",
        title    = "Radius of Gyration",
        unit     = "Å",
        fig      = "radGyr/radGyr.png",
    ),

    # ── RMSD to NMR (all heavy atoms) ─────────────────────────────────────────
    dict(
        type     = "time_series",
        txt      = "rmsd/rmsd_toNMR.txt",
        csv      = "rmsd/rmsd_toNMR.csv",
        columns  = ["Frame", "RMSD"],
        y_column = "RMSD",
        title    = "RMSD to NMR",
        unit     = "Å",
        fig      = "rmsd/rmsd_toNMR.png",
        hist     = True,
        hist_fig = "rmsd/rmsd_toNMR_Hist.png",
    ),

    # ── RMSD to NMR — backbone ────────────────────────────────────────────────
    dict(
        type     = "time_series",
        txt      = "rmsd/rmsd_toNMRBackbone.txt",
        csv      = "rmsd/rmsd_toNMRBackbone.csv",
        columns  = ["Frame", "RMSD"],
        y_column = "RMSD",
        title    = "RMSD to NMR Backbone",
        unit     = "Å",
        fig      = "rmsd/rmsd_toNMRBackbone.png",
        hist     = True,
        hist_fig = "rmsd/rmsd_toNMRBackbone_Hist.png",
    ),

    # ── RMSD to NMR — loop ────────────────────────────────────────────────────
    dict(
        type     = "time_series",
        txt      = "rmsd/rmsd_toNMRLoop.txt",
        csv      = "rmsd/rmsd_toNMRLoop.csv",
        columns  = ["Frame", "RMSD"],
        y_column = "RMSD",
        title    = "RMSD to NMR Loop",
        unit     = "Å",
        fig      = "rmsd/rmsd_toNMRLoop.png",
        hist     = True,
        hist_fig = "rmsd/rmsd_toNMRLoop_Hist.png",
    ),

    # ── RMSD to NMR — stem ────────────────────────────────────────────────────
    dict(
        type     = "time_series",
        txt      = "rmsd/rmsd_toNMRStem.txt",
        csv      = "rmsd/rmsd_toNMRStem.csv",
        columns  = ["Frame", "RMSD"],
        y_column = "RMSD",
        title    = "RMSD to NMR Stem",
        unit     = "Å",
        fig      = "rmsd/rmsd_toNMRStem.png",
        hist     = True,
        hist_fig = "rmsd/rmsd_toNMRStem_Hist.png",
    ),

    # ── RMSD to NMR — bases 1-14 ──────────────────────────────────────────────
    dict(
        type     = "time_series",
        txt      = "rmsd/rmsd_toNMR1-14Bases.txt",
        csv      = "rmsd/rmsd_toNMR1-14Bases.csv",
        columns  = ["Frame", "RMSD"],
        y_column = "RMSD",
        title    = "RMSD to NMR Bases",
        unit     = "Å",
        fig      = "rmsd/rmsd_toNMR1-14Bases.png",
        hist     = True,
        hist_fig = "rmsd/rmsd_toNMR1-14Bases_Hist.png",
    ),

    # ── RMSD to first frame ───────────────────────────────────────────────────
    dict(
        type     = "time_series",
        txt      = "rmsd/rmsd.txt",
        csv      = "rmsd/rmsd.csv",
        columns  = ["Frame", "RMSD"],
        y_column = "RMSD",
        title    = "RMSD to First Frame",
        unit     = "Å",
        fig      = "rmsd/rmsd.png",
    ),

    # ── Minimum distance — ends (Res1–Res14) ──────────────────────────────────
    dict(
        type     = "time_series",
        txt      = "minDist/minDistEnds.txt",
        csv      = "minDist/minDistEnds.csv",
        columns  = ["Frame", "MinDist"],
        y_column = "MinDist",
        y_label  = "Minimum Distance",
        title    = "Minimum Distance Res1–Res14",
        unit     = "Å",
        fig      = "minDist/minDist.png",
    ),

    # ── Loop contact: G9–U6 ───────────────────────────────────────────────────
    dict(
        type     = "time_series",
        txt      = "minDist/minDistG9-U6.txt",
        csv      = "minDist/minDistG9-U6.csv",
        columns  = ["Frame", "MinDist"],
        y_column = "MinDist",
        y_label  = "Minimum Distance",
        title    = "Loop Contact G9–U6",
        unit     = "Å",
        fig      = "minDist/minDistG9-U6.png",
    ),

    # ── Loop contact: G9–U6 sugar-base ───────────────────────────────────────
    dict(
        type     = "time_series",
        txt      = "minDist/minDistG9-U6sugar-base.txt",
        csv      = "minDist/minDistG9-U6sugar-base.csv",
        columns  = ["Frame", "MinDist"],
        y_column = "MinDist",
        y_label  = "Minimum Distance",
        title    = "Loop Contact G9–U6 sugar-base",
        unit     = "Å",
        fig      = "minDist/minDistG9-U6sugar-base.png",
    ),

    # ── Loop contact: G9–U7 sugar-base ───────────────────────────────────────
    dict(
        type     = "time_series",
        txt      = "minDist/minDistG9-U7sugar-base.txt",
        csv      = "minDist/minDistG9-U7sugar-base.csv",
        columns  = ["Frame", "MinDist"],
        y_column = "MinDist",
        y_label  = "Minimum Distance",
        title    = "Loop Contact G9–U7 sugar-base",
        unit     = "Å",
        fig      = "minDist/minDistG9-U7sugar-base.png",
    ),

    # ── Loop contact: U7–C8 base-phosphate ───────────────────────────────────
    dict(
        type     = "time_series",
        txt      = "minDist/minDistU7-C8base-phosphate.txt",
        csv      = "minDist/minDistU7-C8base-phosphate.csv",
        columns  = ["Frame", "MinDist"],
        y_column = "MinDist",
        y_label  = "Minimum Distance",
        title    = "Loop Contact U7–C8 base-phosphate",
        unit     = "Å",
        fig      = "minDist/minDistU7-C8base-phosphate.png",
    ),

    # ── Hydrogen bonds per frame ──────────────────────────────────────────────
    dict(
        type     = "time_series",
        txt      = "hbonds/hbondFrames.txt",
        csv      = "hbonds/hbondFrames.csv",
        columns  = ["Frame", "HBonds"],
        y_column = "HBonds",
        y_label  = "Number of Hydrogen Bonds",
        title    = "HBonds per Frame",
        unit     = "",
        fig      = "hbonds/hbondFrames.png",
        hist     = True,
        hist_fig = "hbonds/hbondFrames_Hist.png",
    ),

    # ── Template: sugar pucker (histogram only) ───────────────────────────────
    # dict(
    #     type     = "histogram_only",
    #     txt      = "sugarPucker/sugarPucker_U7.txt",
    #     csv      = "sugarPucker/sugarPucker_U7.csv",
    #     columns  = ["Frame", "Pucker"],
    #     y_column = "Pucker",
    #     title    = "U7 Sugar Pucker",
    #     unit     = "°",
    #     fig      = "sugarPucker/sugarPucker_U7.png",
    # ),

    # ── Template: backbone dihedral (histogram only) ──────────────────────────
    # dict(
    #     type     = "histogram_only",
    #     txt      = "dihedrals/G9_chi.txt",
    #     csv      = "dihedrals/G9_chi.csv",
    #     columns  = ["Frame", "Chi"],
    #     y_column = "Chi",
    #     title    = "G9 Chi Dihedral",
    #     unit     = "°",
    #     fig      = "dihedrals/G9_chi.png",
    # ),

    # ── Template: ion RDF ─────────────────────────────────────────────────────
    # dict(
    #     type = "rdf",
    #     ion1 = "Na+",  txt1 = "rdf/RDF-Na.txt",
    #     ion2 = "Cl-",  txt2 = "rdf/RDF-Cl.txt",
    #     csv  = "rdf/RDF_ions.csv",
    #     fig  = "rdf/RDF_ions.png",
    # ),
]


# ── Stage 3: barnaba eRMSD + master CSV ───────────────────────────────────────
# Set ERMSD_CONFIG = None to skip Stages 3 and 4.
#
# extra_columns: list of (master_col_name, source_csv, source_col) tuples.
# Each cpptraj-derived CSV produced in Stage 2 can contribute one column.
# Columns are aligned by row index (frame order must match the trajectory).

ERMSD_CONFIG = dict(
    native     = "2KOCFolded_NMR.pdb",
    traj       = "../../stripped_trajectories/2KOCUnfolded_HRM_production.nc",
    top        = "../../stripped_trajectories/2KOCUnfolded_HRM_stripped.prmtop",
    master_csv = "eRMSD/ermsd_metrics.csv",
    extra_columns = [
        # (column name in master CSV,        source CSV,                            source column)
        ("RadiusOfGyration",                 "radGyr/radGyr.csv",                   "RadiusofGyration"),
        ("MinimumDistanceEnds",              "minDist/minDistEnds.csv",             "MinDist"),
        ("MinimumDistanceG9-U6",             "minDist/minDistG9-U6.csv",            "MinDist"),
        ("MinimumDistanceG9-U6SugarBase",    "minDist/minDistG9-U6sugar-base.csv",  "MinDist"),
        ("MinimumDistanceG9-U7SugarBase",    "minDist/minDistG9-U7sugar-base.csv",  "MinDist"),
        ("MinimumDistanceU7-C8BasePhosphate","minDist/minDistU7-C8base-phosphate.csv","MinDist"),
        ("LoopRMSD",                         "rmsd/rmsd_toNMRLoop.csv",             "RMSD"),
    ],
)


# ── Stage 4: cross-metric 2-D plot suites ────────────────────────────────────
# Each entry reads two columns from a CSV and calls plot_2d_suite().
# All four plot types are saved: scatter, hist2d_logcount, hist2d_density,
# contour.  Set CROSS_METRIC_PLOTS = [] to skip.

CROSS_METRIC_PLOTS = [

    dict(
        csv        = "eRMSD/ermsd_metrics.csv",
        x_col      = "eRMSD",
        y_col      = "RMSD",
        xlabel     = "eRMSD from native",
        ylabel     = "RMSD from native (nm)",
        out_prefix = "eRMSD/eRMSD_RMSD",
        vlines     = [0.7],
    ),
    dict(
        csv        = "eRMSD/ermsd_metrics.csv",
        x_col      = "eRMSD",
        y_col      = "RadiusOfGyration",
        xlabel     = "eRMSD from native",
        ylabel     = "Radius of Gyration (Å)",
        out_prefix = "eRMSD/eRMSD_RoG",
        vlines     = [0.7],
    ),
    dict(
        csv        = "eRMSD/ermsd_metrics.csv",
        x_col      = "eRMSD",
        y_col      = "LoopRMSD",
        xlabel     = "eRMSD from native",
        ylabel     = "Loop RMSD (Å)",
        out_prefix = "eRMSD/eRMSD_LoopRMSD",
        vlines     = [0.7],
    ),
    dict(
        csv        = "eRMSD/ermsd_metrics.csv",
        x_col      = "eRMSD",
        y_col      = "MinimumDistanceEnds",
        xlabel     = "eRMSD from native",
        ylabel     = "Minimum End-to-End Distance (Å)",
        out_prefix = "eRMSD/eRMSD_MinDist",
        vlines     = [0.7],
    ),

    # ── Template: add any column pair from ermsd_metrics.csv ──────────────────
    # dict(
    #     csv        = "eRMSD/ermsd_metrics.csv",
    #     x_col      = "eRMSD",
    #     y_col      = "MinimumDistanceG9-U6",
    #     xlabel     = "eRMSD from native",
    #     ylabel     = "G9–U6 Contact Distance (Å)",
    #     out_prefix = "eRMSD/eRMSD_G9U6",
    #     vlines     = [0.7],
    # ),
]


# ══════════════════════════════════════════════════════════════════════════════
# PIPELINE — do not edit below this line unless you know what you are doing
# ══════════════════════════════════════════════════════════════════════════════

def _banner(msg):
    width = 60
    print(f"\n{'═'*width}")
    print(f"  {msg}")
    print(f"{'═'*width}")

def _ok(msg):
    print(f"  [✓] {msg}")

def _warn(msg):
    print(f"  [!] {msg}", file=sys.stderr)

def _err(msg):
    print(f"  [✗] {msg}", file=sys.stderr)


# ── Create output subdirectories ──────────────────────────────────────────────
# Collect every directory referenced by METRICS, ERMSD_CONFIG, and
# CROSS_METRIC_PLOTS and create them up front so that file writes never fail
# because the parent directory is missing.

_output_dirs = set()

for _m in METRICS:
    for _key in ("txt", "csv", "fig", "hist_fig", "txt1", "txt2"):
        _path = _m.get(_key)
        if _path:
            _d = os.path.dirname(_path)
            if _d:
                _output_dirs.add(_d)

if ERMSD_CONFIG is not None:
    _d = os.path.dirname(ERMSD_CONFIG.get("master_csv", ""))
    if _d:
        _output_dirs.add(_d)

for _p in CROSS_METRIC_PLOTS:
    _d = os.path.dirname(_p.get("out_prefix", ""))
    if _d:
        _output_dirs.add(_d)

for _d in sorted(_output_dirs):
    os.makedirs(_d, exist_ok=True)

_ok(f"Output directories ready: {', '.join(sorted(_output_dirs))}")


# ── Stage 1: cpptraj ──────────────────────────────────────────────────────────

if CPPTRAJ_JOBS:
    _banner("Stage 1 — cpptraj")
    cpptraj_errors = []

    for job in CPPTRAJ_JOBS:
        in_file = job["in_file"]

        if not os.path.isfile(in_file):
            _warn(f"{in_file} not found — skipping")
            continue

        _ok(f"Running cpptraj -i {in_file}")
        result = subprocess.run(
            [CPPTRAJ_EXE, "-i", in_file],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            _err(f"cpptraj failed on {in_file} (exit {result.returncode})")
            print(result.stderr[-2000:], file=sys.stderr)   # last 2000 chars
            cpptraj_errors.append(in_file)
            if FAIL_FAST:
                sys.exit(1)
        else:
            # Copy .dat → .txt
            for src, dst in job.get("copies", []):
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    _ok(f"  copied {src} → {dst}")
                else:
                    _warn(f"  expected output {src} not found after {in_file}")

    if cpptraj_errors:
        _warn(f"cpptraj errors in: {cpptraj_errors}")
else:
    print("  [–] CPPTRAJ_JOBS is empty — Stage 1 skipped")


# ── Stage 2: per-observable processing ───────────────────────────────────────

_banner("Stage 2 — per-observable analysis")

for m in METRICS:
    mtype = m["type"]

    if mtype in ("time_series", "histogram_only"):
        if not os.path.isfile(m["txt"]):
            _warn(f"{m['txt']} not found — skipping {m['title']}")
            continue
        convert_txt_to_csv(m["txt"], m["csv"], m["columns"])
        scale_x_to_ns(m["csv"], TOTAL_NS)

    if mtype == "time_series":
        analyze_time_series(
            csv_path         = m["csv"],
            y_column         = m["y_column"],
            output_file_path = OUTPUT_FILE,
            title_prefix     = m["title"],
            unit             = m.get("unit", ""),
            y_label          = m.get("y_label", ""),
            fig_path         = m["fig"],
            has_hist         = m.get("hist", False),
            hist_fig_path    = m.get("hist_fig"),
            color            = m.get("color", "darkslateblue"),
            linewidth        = m.get("linewidth", 0.3),
        )
        _ok(m["title"])

    elif mtype == "histogram_only":
        analyze_histogram_only(
            csv_path         = m["csv"],
            y_column         = m["y_column"],
            output_file_path = OUTPUT_FILE,
            title_prefix     = m["title"],
            unit             = m.get("unit", ""),
            fig_path         = m["fig"],
            bins             = m.get("bins", 50),
            color            = m.get("color", "purple"),
            density          = m.get("density", True),
        )
        _ok(m["title"])

    elif mtype == "rdf":
        missing = [f for f in (m["txt1"], m["txt2"]) if not os.path.isfile(f)]
        if missing:
            _warn(f"RDF input(s) not found {missing} — skipping")
            continue
        process_rdf(
            ion1             = m["ion1"],
            txt_path1        = m["txt1"],
            ion2             = m["ion2"],
            txt_path2        = m["txt2"],
            output_csv_path  = m["csv"],
            output_file_path = OUTPUT_FILE,
            fig_path         = m["fig"],
        )
        _ok(f"RDF {m['ion1']} / {m['ion2']}")

    else:
        _warn(f"Unknown metric type '{mtype}' — skipping")


# ── Stage 3: barnaba eRMSD + master CSV ───────────────────────────────────────

if ERMSD_CONFIG is None:
    print("\n  [–] ERMSD_CONFIG is None — Stages 3 and 4 skipped")
else:
    _banner("Stage 3 — barnaba eRMSD + master CSV")

    try:
        import barnaba as bb
    except ImportError:
        _err("barnaba is not installed — Stages 3 and 4 skipped")
        _err("Install with:  pip install barnaba")
        ERMSD_CONFIG = None   # skip Stage 4 as well

if ERMSD_CONFIG is not None:
    native = ERMSD_CONFIG["native"]
    traj   = ERMSD_CONFIG["traj"]
    top    = ERMSD_CONFIG["top"]

    for path, label in ((native, "native PDB"), (traj, "trajectory"), (top, "topology")):
        if not os.path.isfile(path):
            _err(f"{label} not found: {path}")
            _err("Stage 3 aborted — check path settings in ERMSD_CONFIG")
            ERMSD_CONFIG = None
            break

if ERMSD_CONFIG is not None:
    _ok(f"Calculating eRMSD vs {ERMSD_CONFIG['native']} ...")
    ermsd = bb.ermsd(native, traj, topology=top)

    _ok("Calculating heavy-atom RMSD (barnaba) ...")
    rmsd  = bb.rmsd(native, traj, topology=top, heavy_atom=True)

    n_frames = len(ermsd)
    frames   = np.arange(n_frames)
    _ok(f"{n_frames} frames processed")

    master = {"Frame": frames, "eRMSD": ermsd, "RMSD": rmsd}

    for col_name, src_csv, src_col in ERMSD_CONFIG.get("extra_columns", []):
        if not os.path.isfile(src_csv):
            _warn(f"{src_csv} not found — column '{col_name}' omitted from master CSV")
            continue
        col_data = pd.read_csv(src_csv)[src_col].values
        if len(col_data) != n_frames:
            _warn(
                f"{src_csv} has {len(col_data)} rows but trajectory has "
                f"{n_frames} frames — column '{col_name}' omitted"
            )
            continue
        master[col_name] = col_data
        _ok(f"  merged {col_name} from {src_csv}")

    master_csv = ERMSD_CONFIG["master_csv"]
    pd.DataFrame(master).to_csv(master_csv, index=False)
    _ok(f"Master CSV saved → {master_csv}")


# ── Stage 4: cross-metric 2-D plot suites ────────────────────────────────────

if ERMSD_CONFIG is not None and CROSS_METRIC_PLOTS:
    _banner("Stage 4 — cross-metric 2-D plots")

    for p in CROSS_METRIC_PLOTS:
        csv_path = p["csv"]
        if not os.path.isfile(csv_path):
            _warn(f"{csv_path} not found — skipping {p['out_prefix']}")
            continue

        data = pd.read_csv(csv_path)

        missing_cols = [c for c in (p["x_col"], p["y_col"]) if c not in data.columns]
        if missing_cols:
            _warn(f"Columns {missing_cols} missing in {csv_path} — skipping {p['out_prefix']}")
            continue

        plot_2d_suite(
            x_vals     = data[p["x_col"]].values,
            y_vals     = data[p["y_col"]].values,
            xlabel     = p["xlabel"],
            ylabel     = p["ylabel"],
            out_prefix = p["out_prefix"],
            vlines     = p.get("vlines"),
            hlines     = p.get("hlines"),
            bins       = p.get("bins", 50),
            cmap       = p.get("cmap", "viridis"),
        )
        _ok(f"{p['out_prefix']}_{{scatter,hist2d_logcount,hist2d_density,contour}}.png")

elif not CROSS_METRIC_PLOTS:
    print("  [–] CROSS_METRIC_PLOTS is empty — Stage 4 skipped")


# ── Done ──────────────────────────────────────────────────────────────────────

_banner("Pipeline complete")
print(f"  Summary report → {OUTPUT_FILE}\n")
