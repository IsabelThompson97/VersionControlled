"""
pipeline_template.py
====================
Generalised cpptraj post-processing pipeline driven by a METRICS list.

Usage
-----
1. Copy this file into your analysis directory.
2. Edit the "Configuration" section at the top.
3. Populate METRICS with one dict per observable.
4. Run:
       python pipeline_template.py

The script processes every entry in METRICS in order, then (optionally) runs
2-D cross-metric plots from a master CSV via CROSS_METRIC_PLOTS.

Metric types
------------
"time_series"
    Reads a two-column cpptraj .txt, converts to .csv, scales frames to ns,
    computes statistics, writes a time-series plot and optional histogram.

"histogram_only"
    Same I/O as "time_series" but produces only a histogram (use for
    angular observables such as sugar pucker or backbone dihedrals).

"rdf"
    Merges two ion RDF .txt files, reports peak positions, plots g(r).

Required keys per type
-----------------------
All "time_series" / "histogram_only" entries need:
    txt       str   cpptraj output .txt file
    csv       str   output .csv path
    columns   list  column names (first must be "Frame")
    y_column  str   data column name (must be in columns)
    title     str   human-readable label for plots and the report
    unit      str   physical unit (e.g. "Å", "°", "")
    fig       str   output .png path

Optional keys for "time_series":
    y_label   str   y-axis label override (defaults to title)
    hist      bool  also save a histogram (default False)
    hist_fig  str   histogram .png path (required when hist=True)
    color     str   matplotlib colour string (default "darkslateblue")
    linewidth float plot line width (default 0.3)

Optional keys for "histogram_only":
    bins      int   number of histogram bins (default 50)
    color     str   bar fill colour (default "purple")
    density   bool  plot density rather than frequency (default True)

"rdf" entries need:
    ion1, ion2   str   ion labels
    txt1, txt2   str   input .txt files
    csv          str   merged output .csv
    fig          str   output .png

Cross-metric 2-D plots (CROSS_METRIC_PLOTS)
--------------------------------------------
After all per-observable processing is done, any entries in
CROSS_METRIC_PLOTS trigger plot_2d_suite(), which produces four PNGs
(scatter, log-count hist2d, density hist2d, contour) for each column pair.

Each entry needs:
    csv        str   master CSV file containing both columns
    x_col      str   x-axis column name in the CSV
    y_col      str   y-axis column name in the CSV
    xlabel     str   x-axis label for plots
    ylabel     str   y-axis label for plots
    out_prefix str   filename prefix for the four output PNGs

Optional:
    vlines     list  x positions for vertical reference lines (e.g. [0.7])
    hlines     list  y positions for horizontal reference lines
    bins       int   histogram bins (default 50)
    cmap       str   colourmap (default "viridis")
"""

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))

from cpptrajAnalysis import (
    convert_txt_to_csv,
    scale_x_to_ns,
    analyze_time_series,
    analyze_histogram_only,
    process_rdf,
    plot_2d_suite,
)
import pandas as pd

# ── Configuration ──────────────────────────────────────────────────────────────

TOTAL_NS    = 1000           # Total simulation time in nanoseconds
OUTPUT_FILE = "analysis_output.txt"   # Cumulative plain-text summary report

# ── Per-observable metrics ─────────────────────────────────────────────────────
# Add, remove, or comment out entries to match your trajectory.

METRICS = [

    # ── Radius of Gyration ────────────────────────────────────────────────────
    dict(
        type      = "time_series",
        txt       = "radGyr.txt",
        csv       = "radGyr.csv",
        columns   = ["Frame", "RadiusofGyration"],
        y_column  = "RadiusofGyration",
        title     = "Radius of Gyration",
        unit      = "Å",
        fig       = "radGyr.png",
    ),

    # ── RMSD to NMR (all heavy atoms) ────────────────────────────────────────
    dict(
        type      = "time_series",
        txt       = "rmsd_toNMR.txt",
        csv       = "rmsd_toNMR.csv",
        columns   = ["Frame", "RMSD"],
        y_column  = "RMSD",
        title     = "RMSD to NMR",
        unit      = "Å",
        fig       = "rmsd_toNMR.png",
        hist      = True,
        hist_fig  = "rmsd_toNMR_Hist.png",
    ),

    # ── RMSD to NMR — backbone ───────────────────────────────────────────────
    dict(
        type      = "time_series",
        txt       = "rmsd_toNMRBackbone.txt",
        csv       = "rmsd_toNMRBackbone.csv",
        columns   = ["Frame", "RMSD"],
        y_column  = "RMSD",
        title     = "RMSD to NMR Backbone",
        unit      = "Å",
        fig       = "rmsd_toNMRBackbone.png",
        hist      = True,
        hist_fig  = "rmsd_toNMRBackbone_Hist.png",
    ),

    # ── RMSD to NMR — loop ───────────────────────────────────────────────────
    dict(
        type      = "time_series",
        txt       = "rmsd_toNMRLoop.txt",
        csv       = "rmsd_toNMRLoop.csv",
        columns   = ["Frame", "RMSD"],
        y_column  = "RMSD",
        title     = "RMSD to NMR Loop",
        unit      = "Å",
        fig       = "rmsd_toNMRLoop.png",
        hist      = True,
        hist_fig  = "rmsd_toNMRLoop_Hist.png",
    ),

    # ── RMSD to NMR — stem ───────────────────────────────────────────────────
    dict(
        type      = "time_series",
        txt       = "rmsd_toNMRStem.txt",
        csv       = "rmsd_toNMRStem.csv",
        columns   = ["Frame", "RMSD"],
        y_column  = "RMSD",
        title     = "RMSD to NMR Stem",
        unit      = "Å",
        fig       = "rmsd_toNMRStem.png",
        hist      = True,
        hist_fig  = "rmsd_toNMRStem_Hist.png",
    ),

    # ── RMSD to NMR — bases 1-14 ────────────────────────────────────────────
    dict(
        type      = "time_series",
        txt       = "rmsd_toNMR1-14Bases.txt",
        csv       = "rmsd_toNMR1-14Bases.csv",
        columns   = ["Frame", "RMSD"],
        y_column  = "RMSD",
        title     = "RMSD to NMR Bases",
        unit      = "Å",
        fig       = "rmsd_toNMR1-14Bases.png",
        hist      = True,
        hist_fig  = "rmsd_toNMR1-14Bases_Hist.png",
    ),

    # ── RMSD to first frame ───────────────────────────────────────────────────
    dict(
        type      = "time_series",
        txt       = "rmsd.txt",
        csv       = "rmsd.csv",
        columns   = ["Frame", "RMSD"],
        y_column  = "RMSD",
        title     = "RMSD to First Frame",
        unit      = "Å",
        fig       = "rmsd.png",
    ),

    # ── Minimum distance — ends (Res1–Res14) ─────────────────────────────────
    dict(
        type      = "time_series",
        txt       = "minDistEnds.txt",
        csv       = "minDistEnds.csv",
        columns   = ["Frame", "MinDist"],
        y_column  = "MinDist",
        y_label   = "Minimum Distance",
        title     = "Minimum Distance Res1–Res14",
        unit      = "Å",
        fig       = "minDist.png",
    ),

    # ── Minimum distance — loop contact G9·U6 ────────────────────────────────
    dict(
        type      = "time_series",
        txt       = "minDistG9-U6.txt",
        csv       = "minDistG9-U6.csv",
        columns   = ["Frame", "MinDist"],
        y_column  = "MinDist",
        y_label   = "Minimum Distance",
        title     = "Loop Contact G9–U6",
        unit      = "Å",
        fig       = "minDistG9-U6.png",
    ),

    # ── Minimum distance — loop contact G9·U6 sugar-base ─────────────────────
    dict(
        type      = "time_series",
        txt       = "minDistG9-U6sugar-base.txt",
        csv       = "minDistG9-U6sugar-base.csv",
        columns   = ["Frame", "MinDist"],
        y_column  = "MinDist",
        y_label   = "Minimum Distance",
        title     = "Loop Contact G9–U6 sugar-base",
        unit      = "Å",
        fig       = "minDistG9-U6sugar-base.png",
    ),

    # ── Minimum distance — loop contact G9·U7 sugar-base ─────────────────────
    dict(
        type      = "time_series",
        txt       = "minDistG9-U7sugar-base.txt",
        csv       = "minDistG9-U7sugar-base.csv",
        columns   = ["Frame", "MinDist"],
        y_column  = "MinDist",
        y_label   = "Minimum Distance",
        title     = "Loop Contact G9–U7 sugar-base",
        unit      = "Å",
        fig       = "minDistG9-U7sugar-base.png",
    ),

    # ── Minimum distance — loop contact U7·C8 base-phosphate ─────────────────
    dict(
        type      = "time_series",
        txt       = "minDistU7-C8base-phosphate.txt",
        csv       = "minDistU7-C8base-phosphate.csv",
        columns   = ["Frame", "MinDist"],
        y_column  = "MinDist",
        y_label   = "Minimum Distance",
        title     = "Loop Contact U7–C8 base-phosphate",
        unit      = "Å",
        fig       = "minDistU7-C8base-phosphate.png",
    ),

    # ── Hydrogen bonds per frame ──────────────────────────────────────────────
    dict(
        type      = "time_series",
        txt       = "hbondFrames.txt",
        csv       = "hbondFrames.csv",
        columns   = ["Frame", "HBonds"],
        y_column  = "HBonds",
        y_label   = "Number of Hydrogen Bonds",
        title     = "HBonds per Frame",
        unit      = "",
        fig       = "hbondFrames.png",
        hist      = True,
        hist_fig  = "hbondFrames_Hist.png",
    ),

    # ── Template: sugar pucker (histogram only) — uncomment and adapt ─────────
    # dict(
    #     type     = "histogram_only",
    #     txt      = "sugarPucker_U7.txt",
    #     csv      = "sugarPucker_U7.csv",
    #     columns  = ["Frame", "Pucker"],
    #     y_column = "Pucker",
    #     title    = "U7 Sugar Pucker",
    #     unit     = "°",
    #     fig      = "sugarPucker_U7.png",
    # ),

    # ── Template: backbone dihedral (histogram only) — uncomment and adapt ────
    # dict(
    #     type     = "histogram_only",
    #     txt      = "G9_chi.txt",
    #     csv      = "G9_chi.csv",
    #     columns  = ["Frame", "Chi"],
    #     y_column = "Chi",
    #     title    = "G9 Chi Dihedral",
    #     unit     = "°",
    #     fig      = "G9_chi.png",
    # ),

    # ── Template: ion RDF — uncomment and adapt ───────────────────────────────
    # dict(
    #     type = "rdf",
    #     ion1 = "Na+",
    #     txt1 = "RDF-Na.txt",
    #     ion2 = "Cl-",
    #     txt2 = "RDF-Cl.txt",
    #     csv  = "RDF_ions.csv",
    #     fig  = "RDF_ions.png",
    # ),
]

# ── Cross-metric 2-D plots ────────────────────────────────────────────────────
# Requires a master CSV (e.g. ermsd_metrics.csv) that merges barnaba eRMSD
# with the cpptraj observables.  Set to [] to skip this section entirely.

CROSS_METRIC_PLOTS = [

    dict(
        csv        = "ermsd_metrics.csv",
        x_col      = "eRMSD",
        y_col      = "RMSD",
        xlabel     = "eRMSD from native",
        ylabel     = "RMSD from native (nm)",
        out_prefix = "eRMSD_RMSD",
        vlines     = [0.7],
    ),

    dict(
        csv        = "ermsd_metrics.csv",
        x_col      = "eRMSD",
        y_col      = "RadiusOfGyration",
        xlabel     = "eRMSD from native",
        ylabel     = "Radius of Gyration (Å)",
        out_prefix = "eRMSD_RoG",
        vlines     = [0.7],
    ),

    dict(
        csv        = "ermsd_metrics.csv",
        x_col      = "eRMSD",
        y_col      = "LoopRMSD",
        xlabel     = "eRMSD from native",
        ylabel     = "Loop RMSD (Å)",
        out_prefix = "eRMSD_LoopRMSD",
        vlines     = [0.7],
    ),

    dict(
        csv        = "ermsd_metrics.csv",
        x_col      = "eRMSD",
        y_col      = "MinimumDistanceEnds",
        xlabel     = "eRMSD from native",
        ylabel     = "Minimum End-to-End Distance (Å)",
        out_prefix = "eRMSD_MinDist",
        vlines     = [0.7],
    ),

    # ── Template: add any column pair from ermsd_metrics.csv ──────────────────
    # dict(
    #     csv        = "ermsd_metrics.csv",
    #     x_col      = "eRMSD",
    #     y_col      = "MinimumDistanceG9-U6",
    #     xlabel     = "eRMSD from native",
    #     ylabel     = "G9–U6 Contact Distance (Å)",
    #     out_prefix = "eRMSD_G9U6",
    #     vlines     = [0.7],
    # ),
]


# ── Pipeline dispatch ──────────────────────────────────────────────────────────

for m in METRICS:
    mtype = m["type"]

    if mtype == "time_series":
        convert_txt_to_csv(m["txt"], m["csv"], m["columns"])
        scale_x_to_ns(m["csv"], TOTAL_NS)
        analyze_time_series(
            csv_path        = m["csv"],
            y_column        = m["y_column"],
            output_file_path= OUTPUT_FILE,
            title_prefix    = m["title"],
            unit            = m.get("unit", ""),
            y_label         = m.get("y_label", ""),
            fig_path        = m["fig"],
            has_hist        = m.get("hist", False),
            hist_fig_path   = m.get("hist_fig"),
            color           = m.get("color", "darkslateblue"),
            linewidth       = m.get("linewidth", 0.3),
        )
        print(f"[done] {m['title']}")

    elif mtype == "histogram_only":
        convert_txt_to_csv(m["txt"], m["csv"], m["columns"])
        scale_x_to_ns(m["csv"], TOTAL_NS)
        analyze_histogram_only(
            csv_path        = m["csv"],
            y_column        = m["y_column"],
            output_file_path= OUTPUT_FILE,
            title_prefix    = m["title"],
            unit            = m.get("unit", ""),
            fig_path        = m["fig"],
            bins            = m.get("bins", 50),
            color           = m.get("color", "purple"),
            density         = m.get("density", True),
        )
        print(f"[done] {m['title']}")

    elif mtype == "rdf":
        process_rdf(
            ion1            = m["ion1"],
            txt_path1       = m["txt1"],
            ion2            = m["ion2"],
            txt_path2       = m["txt2"],
            output_csv_path = m["csv"],
            output_file_path= OUTPUT_FILE,
            fig_path        = m["fig"],
        )
        print(f"[done] RDF {m['ion1']} / {m['ion2']}")

    else:
        print(f"[warn] Unknown metric type '{mtype}' — skipping")


# ── Cross-metric 2-D plots ────────────────────────────────────────────────────

for p in CROSS_METRIC_PLOTS:
    import os
    if not os.path.isfile(p["csv"]):
        print(f"[skip] {p['csv']} not found — skipping {p['out_prefix']}")
        continue
    data = pd.read_csv(p["csv"])
    if p["x_col"] not in data.columns or p["y_col"] not in data.columns:
        print(f"[skip] columns missing in {p['csv']} — skipping {p['out_prefix']}")
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
    print(f"[done] 2D suite → {p['out_prefix']}_*.png")
