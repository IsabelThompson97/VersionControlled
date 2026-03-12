"""
ClaudeCpptrajAnalysis
=====================
Generalised utilities for converting, analysing, and plotting cpptraj output
from AMBER MD simulations.  Works with any trajectory length and any
scalar observable that cpptraj writes as a two-column (Frame, Value) or
multi-column whitespace-delimited text file.

Public API
----------
Data I/O
~~~~~~~~
    convert_txt_to_csv      Whitespace-delimited cpptraj .dat/.txt  →  .csv
    scale_x_to_ns           Add/update a Time(ns) column from Frame numbers

Statistics & reporting
~~~~~~~~~~~~~~~~~~~~~~
    analyze_time_series     Stats + time-series line plot + optional histogram
    analyze_histogram_only  Stats + histogram only (no time axis)
    process_rdf             Merge two ion RDF files, peak stats, plot g(r)
    append_to_output        Append a text block to the running summary report

2-D cross-metric plotting
~~~~~~~~~~~~~~~~~~~~~~~~~
    plot_scatter            Scatter of two arrays
    plot_hist2d             2-D histogram  (log-count  or  probability-density)
    plot_contour            2-D probability-density filled-contour
    plot_2d_suite           All four 2-D plot types for one column pair

Quick-start
-----------
    from ClaudeCpptrajAnalysis import (
        convert_txt_to_csv, scale_x_to_ns, analyze_time_series, plot_2d_suite,
    )
    import pandas as pd

    # --- Per-observable pipeline ---
    convert_txt_to_csv("radGyr.txt", "radGyr.csv", ["Frame", "RoG"])
    scale_x_to_ns("radGyr.csv", total_ns=1000)
    analyze_time_series(
        "radGyr.csv", "RoG", "report.txt",
        title_prefix="Radius of Gyration", unit="Å", fig_path="radGyr.png",
    )

    # --- Cross-metric 2-D plots ---
    data = pd.read_csv("ermsd_metrics.csv")
    plot_2d_suite(
        data["eRMSD"].values, data["RadiusOfGyration"].values,
        xlabel="eRMSD from native",
        ylabel="Radius of Gyration (Å)",
        out_prefix="eRMSD_RoG",
        vlines=[0.7],
    )
"""

import time as _time

import matplotlib.colors as _mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# ─── I/O helpers ──────────────────────────────────────────────────────────────

def append_to_output(output_file_path, text):
    """
    Append *text* followed by a blank line to *output_file_path*.

    The file is created if it does not yet exist.

    Parameters
    ----------
    output_file_path : str
        Path to the running plain-text summary report.
    text : str
        Block of text to append.
    """
    with open(output_file_path, "a") as fh:
        fh.write(text + "\n\n")


def convert_txt_to_csv(input_txt_path, output_csv_path, column_names,
                       skiprows=1, sep=r"\s+"):
    """
    Convert a whitespace-delimited cpptraj output file to CSV.

    cpptraj writes a one-line comment header by default (skiprows=1).
    The first column is always the frame index and should be named ``"Frame"``.

    Parameters
    ----------
    input_txt_path : str
        Path to the .dat / .txt file produced by cpptraj.
    output_csv_path : str
        Destination .csv path.
    column_names : list of str
        Column labels.  Must match the number of data columns in the file.
        Convention: first entry is ``"Frame"``.
    skiprows : int, optional
        Header rows to skip (default 1).
    sep : str, optional
        Column-separator regex (default ``r'\\s+'`` — any whitespace).

    Returns
    -------
    str
        Confirmation message.

    Examples
    --------
    >>> convert_txt_to_csv("radGyr.txt", "radGyr.csv", ["Frame", "RoG"])
    >>> convert_txt_to_csv("rmsd_toNMR.txt", "rmsd.csv", ["Frame", "RMSD"])
    """
    data = pd.read_csv(input_txt_path, sep=sep, skiprows=skiprows,
                       names=column_names)
    data.to_csv(output_csv_path, index=False)
    return f"Converted {input_txt_path} → {output_csv_path}"


def scale_x_to_ns(csv_path, total_ns, time_column="Time(ns)",
                  frame_column="Frame"):
    """
    Add (or overwrite) a time column by scaling frame numbers to nanoseconds.

    Scaling: ``Time(ns) = Frame × (total_ns / max_frame)``

    This assumes uniform frame spacing (every *n*-th snapshot written).
    The CSV is modified in place.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file produced by :func:`convert_txt_to_csv`.
    total_ns : float
        Total simulation length in nanoseconds.
    time_column : str, optional
        Name of the column to create/update (default ``"Time(ns)"``).
    frame_column : str, optional
        Name of the frame-index column (default ``"Frame"``).

    Returns
    -------
    str
        Confirmation message.
    """
    data = pd.read_csv(csv_path)
    total_frames = data[frame_column].max()
    data[time_column] = data[frame_column] * (total_ns / total_frames)
    data.to_csv(csv_path, index=False)
    return f"Scaled to {total_ns} ns → {csv_path}"


# ─── Statistics & reporting ───────────────────────────────────────────────────

def analyze_time_series(csv_path, y_column, output_file_path, title_prefix,
                        unit="", y_label="",
                        time_column="Time(ns)", frame_column="Frame",
                        fig_path="plot.png",
                        has_hist=False, hist_fig_path=None,
                        linewidth=0.3, color="darkslateblue"):
    """
    Compute summary statistics, append them to a report, and save plots.

    Always produces a time-series line plot.  Optionally also saves a
    histogram using Sturges' rule for bin count.

    Statistics written to the report
    ---------------------------------
    Maximum, minimum, mean, median, standard deviation; top-5 and
    bottom-5 frames by value.

    Parameters
    ----------
    csv_path : str
        CSV file with columns *frame_column*, *time_column*, *y_column*.
        Must have been scaled with :func:`scale_x_to_ns` first.
    y_column : str
        Name of the observable column to analyse.
    output_file_path : str
        Plain-text summary report (opened in append mode).
    title_prefix : str
        Human-readable label used in plot titles and the report,
        e.g. ``"Radius of Gyration"`` or ``"RMSD to NMR"``.
    unit : str, optional
        Physical unit shown in axis labels, e.g. ``"Å"`` or ``"°"``.
    y_label : str, optional
        Y-axis label override.  Defaults to *title_prefix* when empty.
    time_column : str, optional
        Time column name (default ``"Time(ns)"``).
    frame_column : str, optional
        Frame-index column name (default ``"Frame"``).
    fig_path : str, optional
        Output path for the time-series PNG (default ``"plot.png"``).
    has_hist : bool, optional
        If ``True``, save a histogram PNG as well (default ``False``).
    hist_fig_path : str, optional
        Output path for the histogram PNG.  When ``None`` and *has_hist*
        is ``True``, the path is derived from *fig_path* by inserting
        ``"_Hist"`` before the extension.
    linewidth : float, optional
        Line width for the time-series plot (default 0.3).
    color : str, optional
        Matplotlib colour for line and histogram bars (default
        ``"darkslateblue"``).
    """
    data = pd.read_csv(csv_path)
    time_ns = data[time_column]
    values  = data[y_column]

    max_val   = values.max()
    min_val   = values.min()
    average   = values.mean()
    median    = values.median()
    std_dev   = values.std()
    max_frame = data.loc[values.idxmax(), frame_column]
    min_frame = data.loc[values.idxmin(), frame_column]
    top5_hi   = data.nlargest(5, y_column)
    top5_lo   = data.nsmallest(5, y_column)

    unit_str = f" ({unit})" if unit else ""
    report = (
        f"Maximum {title_prefix}{unit_str}: {max_val} (Frame: {max_frame})\n"
        f"Minimum {title_prefix}{unit_str}: {min_val} (Frame: {min_frame})\n"
        f"Average {title_prefix}{unit_str}: {average}\n"
        f"Median  {title_prefix}{unit_str}: {median}\n"
        f"Std Dev {title_prefix}{unit_str}: {std_dev}\n\n"
        f"Top 5 largest:\n"
        f"{top5_hi[[frame_column, y_column]].to_string(index=False)}\n\n"
        f"Top 5 smallest:\n"
        f"{top5_lo[[frame_column, y_column]].to_string(index=False)}\n"
    )
    ts = _time.asctime()
    append_to_output(
        output_file_path,
        f"{'─'*52}\n{title_prefix}  [{ts}]\n{'─'*52}\n\n{report}"
    )

    # ── Time-series line plot ──
    axis_label = y_label if y_label else title_prefix
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(time_ns, values, color=color, alpha=0.95, linewidth=linewidth)
    ax.axhline(average, color="r", linestyle="-",
               label=f"Mean: {average:.3f}{' ' + unit if unit else ''}")
    ax.set_xlim(0, time_ns.max())
    ax.set_xlabel("Time (ns)")
    ax.set_ylabel(f"{axis_label}{unit_str}")
    ax.set_title(f"{title_prefix}{unit_str}")
    ticks = np.linspace(0, time_ns.max(), num=11)
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t:.1f}" for t in ticks])
    ax.legend()
    fig.tight_layout()
    fig.savefig(fig_path)
    plt.close(fig)

    # ── Optional histogram ──
    if has_hist:
        if hist_fig_path is None:
            hist_fig_path = fig_path.replace(".png", "_Hist.png")
        n_bins = int(np.ceil(np.log2(len(values)) + 1))   # Sturges' rule
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.hist(values, bins=n_bins, color=color, alpha=0.75, edgecolor="black")
        ax.axvline(average, color="r", linestyle="-",
                   label=f"Mean: {average:.3f}{' ' + unit if unit else ''}")
        ax.axvline(median, color="g", linestyle="--",
                   label=f"Median: {median:.3f}{' ' + unit if unit else ''}")
        ax.set_xlabel(f"{axis_label}{unit_str}")
        ax.set_ylabel("Frequency")
        ax.set_title(f"{title_prefix}{unit_str} — Distribution")
        ax.legend()
        fig.tight_layout()
        fig.savefig(hist_fig_path)
        plt.close(fig)


def analyze_histogram_only(csv_path, y_column, output_file_path, title_prefix,
                           unit="",
                           time_column="Time(ns)", frame_column="Frame",
                           fig_path="hist.png",
                           bins=50, color="purple", edgecolor="purple",
                           density=True):
    """
    Compute summary statistics and save a histogram — no time-series plot.

    Best suited for angular or circular observables (sugar pucker, backbone
    dihedrals) where the distribution shape is of primary interest.

    Parameters
    ----------
    csv_path : str
        CSV containing at least *frame_column* and *y_column*.
    y_column : str
        Name of the observable column.
    output_file_path : str
        Plain-text summary report (append mode).
    title_prefix : str
        Human-readable label, e.g. ``"U7 Sugar Pucker"``.
    unit : str, optional
        Physical unit, e.g. ``"°"``.
    time_column : str, optional
        Kept for API consistency; not used in the plot.
    frame_column : str, optional
        Frame-index column (default ``"Frame"``).
    fig_path : str, optional
        Output PNG path (default ``"hist.png"``).
    bins : int, optional
        Number of histogram bins (default 50).
    color : str, optional
        Bar fill colour (default ``"purple"``).
    edgecolor : str, optional
        Bar edge colour (default ``"purple"``).
    density : bool, optional
        Plot probability density rather than raw frequency (default ``True``).
    """
    data   = pd.read_csv(csv_path)
    values = data[y_column]

    max_val   = values.max()
    min_val   = values.min()
    average   = values.mean()
    std_dev   = values.std()
    max_frame = data.loc[values.idxmax(), frame_column]
    min_frame = data.loc[values.idxmin(), frame_column]
    top5_hi   = data.nlargest(5, y_column)
    top5_lo   = data.nsmallest(5, y_column)

    unit_str = f" ({unit})" if unit else ""
    report = (
        f"Maximum {title_prefix}{unit_str}: {max_val} (Frame: {max_frame})\n"
        f"Minimum {title_prefix}{unit_str}: {min_val} (Frame: {min_frame})\n"
        f"Average {title_prefix}{unit_str}: {average}\n"
        f"Std Dev {title_prefix}{unit_str}: {std_dev}\n\n"
        f"Top 5 largest:\n"
        f"{top5_hi[[frame_column, y_column]].to_string(index=False)}\n\n"
        f"Top 5 smallest:\n"
        f"{top5_lo[[frame_column, y_column]].to_string(index=False)}\n"
    )
    ts = _time.asctime()
    append_to_output(
        output_file_path,
        f"{'─'*52}\n{title_prefix}  [{ts}]\n{'─'*52}\n\n{report}"
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.hist(values, density=density, bins=bins, alpha=0.5,
            edgecolor=edgecolor, color=color)
    ax.set_ylabel("Density" if density else "Frequency")
    ax.set_xlabel(f"{title_prefix}{unit_str}")
    ax.set_title(f"{title_prefix} — Distribution")
    fig.tight_layout()
    fig.savefig(fig_path)
    plt.close(fig)


def process_rdf(ion1, txt_path1, ion2, txt_path2,
                output_csv_path, output_file_path, fig_path,
                title="Radial Distribution Function",
                xlabel="Distance (Å)", ylabel="g(r)",
                color1="darkslateblue", color2="darkorange"):
    """
    Merge two ion RDF files, report peak positions, and plot g(r).

    Each input file must be a two-column whitespace-delimited cpptraj RDF
    output: ``Distance`` and ``g(r)``.

    Parameters
    ----------
    ion1 : str
        Label for the first ion, e.g. ``"Na+"``.
    txt_path1 : str
        RDF .txt file for ion1.
    ion2 : str
        Label for the second ion, e.g. ``"Cl-"``.
    txt_path2 : str
        RDF .txt file for ion2.
    output_csv_path : str
        Merged output CSV (columns: Distance, ion1, ion2).
    output_file_path : str
        Plain-text summary report (append mode).
    fig_path : str
        Output PNG path.
    title : str, optional
        Plot title (default ``"Radial Distribution Function"``).
    xlabel, ylabel : str, optional
        Axis labels.
    color1, color2 : str, optional
        Line colours for ion1 and ion2.
    """
    d1 = pd.read_csv(txt_path1, sep=r"\s+", skiprows=1,
                     names=["Distance", ion1])
    d2 = pd.read_csv(txt_path2, sep=r"\s+", skiprows=1,
                     names=["Distance", ion2])

    distance    = d1["Distance"].values
    ion1_values = d1[ion1].values
    ion2_values = d2[ion2].values

    merged = pd.DataFrame({"Distance": distance,
                            ion1: ion1_values,
                            ion2: ion2_values})
    merged.to_csv(output_csv_path, index=False)

    max1, dist1 = ion1_values.max(), merged.loc[ion1_values.argmax(), "Distance"]
    max2, dist2 = ion2_values.max(), merged.loc[ion2_values.argmax(), "Distance"]

    report = (
        f"Peak {ion1} g(r): {max1:.4f} at {dist1:.3f} Å\n"
        f"Peak {ion2} g(r): {max2:.4f} at {dist2:.3f} Å\n"
    )
    ts = _time.asctime()
    append_to_output(
        output_file_path,
        f"{'─'*52}\nRDF {ion1} / {ion2}  [{ts}]\n{'─'*52}\n\n{report}"
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(distance, ion1_values, color=color1, alpha=0.95, label=ion1)
    ax.plot(distance, ion2_values, color=color2, alpha=0.95, label=ion2)
    ax.set_xlim(0, distance.max())
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ticks = np.linspace(0, distance.max(), num=11)
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t:.1f}" for t in ticks])
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(fig_path)
    plt.close(fig)


# ─── 2-D cross-metric plotting ────────────────────────────────────────────────

def plot_scatter(x_vals, y_vals, xlabel, ylabel, title, out_path,
                 vlines=None, hlines=None,
                 s=1, alpha=0.5, color="steelblue",
                 figsize=(8, 6), dpi=300):
    """
    Scatter plot of two observable arrays.

    Parameters
    ----------
    x_vals, y_vals : array-like
        Data arrays of equal length.
    xlabel, ylabel : str
        Axis labels.
    title : str
        Plot title.
    out_path : str
        Output PNG path.
    vlines : list of float, optional
        X positions for vertical dashed reference lines (e.g. ``[0.7]``).
    hlines : list of float, optional
        Y positions for horizontal dashed reference lines.
    s : float, optional
        Marker size (default 1).
    alpha : float, optional
        Marker transparency (default 0.5).
    color : str, optional
        Marker colour (default ``"steelblue"``).
    figsize : tuple, optional
        Figure size in inches (default ``(8, 6)``).
    dpi : int, optional
        Output resolution (default 300).
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(x_vals, y_vals, s=s, alpha=alpha, c=color)
    _add_ref_lines(ax, vlines, hlines)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def plot_hist2d(x_vals, y_vals, xlabel, ylabel, title, out_path,
                vlines=None, hlines=None,
                bins=50, mode="density",
                cmap="viridis",
                figsize=(8, 6), dpi=300):
    """
    2-D histogram of two observable arrays.

    Two colour-scaling modes are available:

    * ``"density"``    — probability density; empty bins rendered as white
      via a transparent colourmap floor so the plot background stays clean.
    * ``"log_count"``  — raw frame counts on a logarithmic colour scale,
      useful for highlighting sparsely sampled regions.

    Parameters
    ----------
    x_vals, y_vals : array-like
        Data arrays of equal length.
    xlabel, ylabel : str
        Axis labels.
    title : str
        Plot title.
    out_path : str
        Output PNG path.
    vlines : list of float, optional
        X positions for vertical reference lines.
    hlines : list of float, optional
        Y positions for horizontal reference lines.
    bins : int, optional
        Number of bins along each axis (default 50).
    mode : ``"density"`` | ``"log_count"``, optional
        Colour-scaling mode (default ``"density"``).
    cmap : str, optional
        Matplotlib colourmap name (default ``"viridis"``).
    figsize : tuple, optional
        Figure size in inches (default ``(8, 6)``).
    dpi : int, optional
        Output resolution (default 300).
    """
    fig, ax = plt.subplots(figsize=figsize)

    if mode == "log_count":
        _, _, _, img = ax.hist2d(x_vals, y_vals, bins=bins, cmap=cmap,
                                 norm=_mcolors.LogNorm())
        fig.colorbar(img, ax=ax).set_label("Count (log scale)")
    else:  # density
        cmap_obj = plt.colormaps.get_cmap(cmap).copy()
        cmap_obj.set_under("white", alpha=0)
        _, _, _, img = ax.hist2d(x_vals, y_vals, bins=bins, density=True,
                                 cmap=cmap_obj, vmin=1e-10)
        fig.colorbar(img, ax=ax).set_label("Probability Density")

    _add_ref_lines(ax, vlines, hlines)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def plot_contour(x_vals, y_vals, xlabel, ylabel, title, out_path,
                 vlines=None, hlines=None,
                 bins=50, levels_fill=20, levels_line=10,
                 cmap="viridis",
                 figsize=(8, 6), dpi=300):
    """
    Filled probability-density contour plot for two observable arrays.

    The 2-D histogram is computed with ``numpy.histogram2d`` (density=True)
    and then rendered as filled contours.  Semi-transparent white lines are
    overlaid for clarity.

    Parameters
    ----------
    x_vals, y_vals : array-like
        Data arrays of equal length.
    xlabel, ylabel : str
        Axis labels.
    title : str
        Plot title.
    out_path : str
        Output PNG path.
    vlines : list of float, optional
        X positions for vertical reference lines.
    hlines : list of float, optional
        Y positions for horizontal reference lines.
    bins : int, optional
        Histogram resolution used to estimate the density (default 50).
    levels_fill : int, optional
        Number of filled contour levels (default 20).
    levels_line : int, optional
        Number of white contour line levels overlaid (default 10).
    cmap : str, optional
        Matplotlib colourmap name (default ``"viridis"``).
    figsize : tuple, optional
        Figure size in inches (default ``(8, 6)``).
    dpi : int, optional
        Output resolution (default 300).
    """
    h, xedges, yedges = np.histogram2d(x_vals, y_vals,
                                        bins=bins, density=True)
    X, Y = np.meshgrid(
        (xedges[:-1] + xedges[1:]) / 2,
        (yedges[:-1] + yedges[1:]) / 2,
    )

    fig, ax = plt.subplots(figsize=figsize)
    cf = ax.contourf(X, Y, h.T, levels=levels_fill, cmap=cmap)
    ax.contour(X, Y, h.T, levels=levels_line,
               colors="white", alpha=0.5, linewidths=0.5)
    fig.colorbar(cf, ax=ax).set_label("Probability Density")
    _add_ref_lines(ax, vlines, hlines)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi)
    plt.close(fig)


def plot_2d_suite(x_vals, y_vals, xlabel, ylabel, out_prefix,
                  vlines=None, hlines=None,
                  bins=50, cmap="viridis",
                  figsize=(8, 6), dpi=300):
    """
    Generate a full suite of four 2-D comparison plots for two observables.

    Files saved
    -----------
    * ``<out_prefix>_scatter.png``
    * ``<out_prefix>_hist2d_logcount.png``
    * ``<out_prefix>_hist2d_density.png``
    * ``<out_prefix>_contour.png``

    Parameters
    ----------
    x_vals, y_vals : array-like
        Data arrays of equal length.
    xlabel, ylabel : str
        Axis labels shared by all four plots.
    out_prefix : str
        Filename prefix for the four output PNGs.  Can include a directory
        component, e.g. ``"plots/eRMSD_RoG"``.
    vlines : list of float, optional
        X positions for vertical reference lines shown in every plot.
    hlines : list of float, optional
        Y positions for horizontal reference lines shown in every plot.
    bins : int, optional
        Histogram bins for the 2-D histogram and contour plots (default 50).
    cmap : str, optional
        Matplotlib colourmap name (default ``"viridis"``).
    figsize : tuple, optional
        Figure size for each individual plot (default ``(8, 6)``).
    dpi : int, optional
        Output resolution for each plot (default 300).

    Examples
    --------
    >>> import pandas as pd
    >>> from ClaudeCpptrajAnalysis import plot_2d_suite
    >>> data = pd.read_csv("ermsd_metrics.csv")
    >>> plot_2d_suite(
    ...     data["eRMSD"].values, data["LoopRMSD"].values,
    ...     xlabel="eRMSD from native",
    ...     ylabel="Loop RMSD (Å)",
    ...     out_prefix="eRMSD_LoopRMSD",
    ...     vlines=[0.7],
    ... )
    """
    base = f"{ylabel} vs {xlabel}"
    kw   = dict(vlines=vlines, hlines=hlines,
                figsize=figsize, dpi=dpi)

    plot_scatter(
        x_vals, y_vals, xlabel, ylabel,
        f"Scatter: {base}",
        f"{out_prefix}_scatter.png",
        **kw,
    )
    plot_hist2d(
        x_vals, y_vals, xlabel, ylabel,
        f"2D Histogram (log count): {base}",
        f"{out_prefix}_hist2d_logcount.png",
        bins=bins, mode="log_count", cmap=cmap,
        **kw,
    )
    plot_hist2d(
        x_vals, y_vals, xlabel, ylabel,
        f"2D Probability Density: {base}",
        f"{out_prefix}_hist2d_density.png",
        bins=bins, mode="density", cmap=cmap,
        **kw,
    )
    plot_contour(
        x_vals, y_vals, xlabel, ylabel,
        f"Probability Density Contour: {base}",
        f"{out_prefix}_contour.png",
        bins=bins, cmap=cmap,
        **kw,
    )


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _add_ref_lines(ax, vlines, hlines):
    """Draw dashed vertical and horizontal reference lines on *ax*."""
    for x in (vlines or []):
        ax.axvline(x, ls="--", c="k", alpha=0.7)
    for y in (hlines or []):
        ax.axhline(y, ls="--", c="k", alpha=0.7)
