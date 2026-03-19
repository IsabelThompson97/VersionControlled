# AMBER Trajectory Analysis Pipeline
### cpptraj + barnaba eRMSD — User Guide

> **System:** University of Notre Dame CRC
> **Simulation target:** 2KOC RNA hairpin (14-residue, OL3 force field)
> **Trajectory type:** AMBER NetCDF (`.nc`), stripped topology (`.prmtop`)
> **Python environment:** `rna` conda env (Python 3.12, barnaba, numpy, pandas, matplotlib)
> **AMBER module:** `amber/24.0`

---

## Table of Contents

1. [Overview](#1-overview)
2. [Repository Layout](#2-repository-layout)
3. [Prerequisites](#3-prerequisites)
4. [Quick Start](#4-quick-start)
5. [Stage 1 — cpptraj Analysis Scripts](#5-stage-1--cpptraj-analysis-scripts)
6. [Stage 2 — Per-Observable Processing](#6-stage-2--per-observable-processing)
7. [Stage 3 — barnaba eRMSD and Master CSV](#7-stage-3--barnaba-ermsd-and-master-csv)
8. [Stage 4 — Cross-Metric 2-D Plots](#8-stage-4--cross-metric-2-d-plots)
9. [Utility Scripts](#9-utility-scripts)
10. [Adapting the Pipeline to a New Simulation](#10-adapting-the-pipeline-to-a-new-simulation)
11. [Configuration Reference](#11-configuration-reference)
12. [Output Files Reference](#12-output-files-reference)
13. [Troubleshooting](#13-troubleshooting)
14. [Theoretical Background](#14-theoretical-background)

---

## 1. Overview

This pipeline performs end-to-end structural analysis of AMBER molecular dynamics (MD) trajectories for RNA systems. It is organized into four sequential stages, each of which can be run independently or skipped as needed:

| Stage | Tool | What it does |
|-------|------|-------------|
| 1 | cpptraj | Computes structural observables (RMSD, R_g, hydrogen bonds, contact distances) from the raw trajectory |
| 2 | Python / cpptrajAnalysis | Converts cpptraj output to CSV, scales frame indices to nanoseconds, computes statistics, and generates time-series and histogram plots |
| 3 | barnaba | Calculates eRMSD and heavy-atom RMSD relative to the native NMR structure; assembles a master CSV combining all Stage 2 metrics |
| 4 | Python / cpptrajAnalysis | Generates cross-metric 2-D scatter, 2-D histogram, and contour plots from the master CSV |

All configuration lives in clearly labelled sections at the top of `full_pipeline.py`. You generally do not need to touch anything below the configuration block.

---

## 2. Repository Layout

```
cpptraj/
├── full_pipeline.py               # Main entry point — runs all four stages
├── pipeline_template.py           # Minimal template for adapting to new simulations
├── submit_pipeline.sh             # SGE job submission script (Notre Dame CRC)
├── getFrameData.py                # Utility: extract per-frame data from master CSV
├── eRMSD_createGIF.py             # Utility: animated eRMSD probability density movie
├── eRMSD_cumulativeEvolutionGIF.py # Utility: cumulative eRMSD density animation
│
├── 2KOCFolded_NMR.pdb             # Native reference structure (Model 1 of NMR ensemble)
├── 2KOCFolded_NMR.prmtop          # AMBER topology for the native reference
├── 2KOCFolded_NMR.rst7            # AMBER restart coordinates for the native reference
│
├── USER_GUIDE.md                  # This guide
├── README_cpptrajAnalysis.md      # cpptrajAnalysis.py function reference
│
└── scripts/
    ├── cpptrajAnalysis.py         # Shared analysis library (I/O, stats, plotting)
    ├── 1_radiusGyr.in             # cpptraj: radius of gyration
    ├── 1_rmsd.in                  # cpptraj: RMSD to first trajectory frame
    ├── 1_rmsdtoNMR.in             # cpptraj: RMSD to NMR reference (all heavy atoms)
    ├── 1_rmsdtoNMRBackbone.in     # cpptraj: RMSD to NMR reference (backbone only)
    ├── 1_rmsdtoNMRStem.in         # cpptraj: RMSD to NMR reference (stem residues)
    ├── 1_rmsdtoNMRLoop.in         # cpptraj: RMSD to NMR reference (loop residues)
    ├── 1_rmsdtoNMR1-14Bases.in    # cpptraj: RMSD to NMR reference (all bases)
    ├── 1_minDistEnds.in           # cpptraj: minimum distance between hairpin ends (Res1–Res14)
    ├── 1_minDistLoopContacts.in   # cpptraj: specific loop contact distances
    ├── 1_hbondFrames.in           # cpptraj: total hydrogen bonds per frame
    ├── 1_hbondsLifetime.in        # cpptraj: hbond lifetimes (all residues)
    ├── 1_hbondsLifetimeLoop.in    # cpptraj: hbond lifetimes (loop residues 6–9)
    └── 1_IonRDF.in                # cpptraj: radial distribution function for Na+/Cl- (optional)
```

The trajectory and topology files are **not** stored in this directory. They live in a `stripped_trajectories/` folder two levels up relative to the `cpptraj/` folder:

```
<simulation_root>/
├── production
│   ├── <name>_production.nc         # trajectory
│   └── <name>.prmtop                # topology
├── stripped_trajectories/                  
│   ├── <name>_productionStripped.nc        # stripped trajectory
│   └── <name>_stripped.prmtop              # stripped topology
└── analysis/
    ├── mdOut/
    └── cpptraj/           ← you are here
```

---

## 3. Prerequisites

### Software

- **AMBER 24.0** — provides `cpptraj`
  `module load amber/24.0`
- **conda environment `rna`** — Python 3.12 with the following packages:
  - `barnaba` (≥ 0.1.14)
  - `numpy`
  - `pandas`
  - `matplotlib`

To create the `rna` environment from scratch:

```bash
conda create -n rna python=3.12
conda activate rna
pip install barnaba numpy pandas matplotlib
```

### Files required before running

| File | Purpose |
|------|---------|
| `../../stripped_trajectories/<name>_production.nc` | AMBER NetCDF trajectory |
| `../../stripped_trajectories/<name>_stripped.prmtop` | Stripped topology (no solvent) |
| `2KOCFolded_NMR.pdb` | Native reference structure for eRMSD |
| `2KOCFolded_NMR.prmtop` | Topology for the NMR reference |
| `2KOCFolded_NMR.rst7` | Coordinates for the NMR reference |

All `.in` cpptraj scripts must also be present in the working directory.

---

## 4. Quick Start

### Running interactively

```bash
cd /scratch365/ithomps3/rnaHairpins/2KOC_OL3_HRM/unfolded/production_retake/analysis/cpptraj
module load amber/24.0
conda activate rna
python3 full_pipeline.py
```

### Submitting to the CRC SGE queue

```bash
qsub submit_pipeline.sh
```

Progress is written to `pipeline.log`; errors go to `pipeline.err`. You will receive an email when the job starts, ends, or aborts.

### Skipping stages

Open `full_pipeline.py` and set the appropriate variable:

| To skip... | Set... |
|-----------|--------|
| Stage 1 (cpptraj) | `CPPTRAJ_JOBS = []` |
| Stages 3 and 4 | `ERMSD_CONFIG = None` |
| Stage 4 only | `CROSS_METRIC_PLOTS = []` |

This is useful when cpptraj has already run and you only want to re-run the Python analysis, or when you want to inspect Stage 2 outputs before committing to the more expensive barnaba calculation.

---

## 5. Stage 1 — cpptraj Analysis Scripts

### How it works

Stage 1 iterates through the `CPPTRAJ_JOBS` list in `full_pipeline.py`. For each entry it calls:

```bash
cpptraj -i <in_file>
```

and then copies the resulting `.dat` file(s) to `.txt` counterparts so that downstream Python code can identify them unambiguously.

### cpptraj script conventions

All `.in` scripts share the same structure:

```
parm  <topology>           # load topology
trajin <trajectory>        # load trajectory

[optional: autoimage]      # re-image molecules into the primary unit cell

<analysis commands>

run
quit
```

The `autoimage` command recalculates periodic-boundary imaging so that the molecule is not split across box faces. It should be included wherever distance-based metrics (RMSD, contact distances, R_g) are computed.

### Topology labelling for multi-topology scripts

Scripts that compute RMSD relative to the NMR reference load two topologies and must label each explicitly to avoid ambiguity:

```
parm ../../../stripped_trajectories/2KOCUnfolded_HRM_stripped.prmtop [trajfoldedParm]
trajin ../../../stripped_trajectories/2KOCUnfolded_HRM_production.nc parm [trajfoldedParm]

parm ../2KOCFolded_NMR.prmtop [NMR]
reference ../2KOCFolded_NMR.rst7 [NMR] parm [NMR]

rmsd ToNMR :1-14&!@H= ref [NMR] :1-14&!@H= out rmsd_toNMR.dat
```

The bracket notation `[label]` associates each trajectory frame and reference with the correct topology. Without it, cpptraj will raise a topology mismatch error.

### Atom selection syntax

cpptraj uses a mask syntax to select subsets of atoms:

| Mask | Meaning |
|------|---------|
| `:1-14` | Residues 1 through 14 (all atoms) |
| `:1-14&!@H=` | Residues 1–14, heavy atoms only (exclude hydrogens) |
| `:6-9` | Loop residues 6–9 |
| `:6@184` | Atom index 184 in residue 6 |
| `@P,OP1,OP2,O5',C5',C4',C3',O3',O4',C1',C2',O2'` | Backbone atom names |

The `&` operator is AND, `!` is NOT, and `@` selects by atom name or index.

### Implemented cpptraj scripts

**`1_radiusGyr.in`** — Radius of gyration of all heavy atoms (residues 1–14). Uses the `mass` keyword for mass-weighted R_g and `nomax` to suppress the maximum-extent output column.

**`1_rmsd.in`** — RMSD of all heavy atoms relative to the **first trajectory frame**. Useful for measuring internal structural drift rather than proximity to any reference structure.

**`1_rmsdtoNMR.in`** — Heavy-atom RMSD relative to the NMR reference structure. This is the broadest structural metric: it quantifies global deviation from the folded state.

**`1_rmsdtoNMRBackbone.in`** — RMSD of backbone atoms only (`P, OP1, OP2, O5', C5', C4', C3', O3', O4', C1', C2', O2'`). More sensitive than whole-molecule RMSD to sugar-phosphate backbone geometry while ignoring base orientation.

**`1_rmsdtoNMRStem.in`** — RMSD for the stem region only. Isolates whether the Watson–Crick base-paired stem remains folded even when the loop is disordered.

**`1_rmsdtoNMRLoop.in`** — RMSD for the loop region (residues 6–9). The loop is the most structurally variable region of the hairpin and often unfolds first.

**`1_rmsdtoNMR1-14Bases.in`** — RMSD of all base heavy atoms. Bases carry the most chemical information about the folded state; this metric is complementary to the backbone RMSD.

**`1_minDistEnds.in`** — Minimum distance between residue 1 and residue 14 (the two hairpin ends). A small value indicates that the ends are in contact, consistent with a compact hairpin; a large value indicates the chain is extended.

**`1_minDistLoopContacts.in`** — Four specific loop contact distances tracking the non-Watson–Crick interactions in the GNRA-type loop:
- G9–U6 (tSW base pair atoms)
- G9–U6 sugar–base contact
- G9–U7 sugar–base contact
- U7–C8 base–phosphate contact

These distances are derived from the known structure of 2KOC and serve as reporters for whether the characteristic loop geometry is intact.

**`1_hbondFrames.in`** — Total number of hydrogen bonds per trajectory frame across all residues. Uses cpptraj's `hbond` command with default distance (3.5 Å) and angle (120°) cutoffs.

**`1_hbondsLifetime.in`** — Hydrogen bond lifetime analysis for all residues (1–14). Outputs both a per-bond average (`hbondLifetimeAvg.dat`) and a time series suitable for autocorrelation analysis (`hbondLifetime.gnu`).

**`1_hbondsLifetimeLoop.in`** — Same as above, restricted to loop residues 6–9.

**`1_IonRDF.in`** *(optional, commented out by default)* — Radial distribution function g(r) for Na⁺ and Cl⁻ ions around the RNA. Uncomment in `CPPTRAJ_JOBS` if ion solvation analysis is needed.

---

## 6. Stage 2 — Per-Observable Processing

### Data flow

Each metric entry in the `METRICS` list follows this chain:

```
<metric>.txt
    └─► convert_txt_to_csv()  →  <metric>.csv
            └─► scale_x_to_ns()   (adds Time(ns) column, edits CSV in place)
                    └─► analyze_time_series()  or  analyze_histogram_only()
                                └─► time-series plot (.png)
                                └─► histogram (.png, if requested)
                                └─► statistics appended to analysis_output.txt
```

### Metric types

#### `"time_series"`

Produces a time-series line plot with a mean reference line, optionally paired with a distribution histogram. Best suited for scalar observables that evolve continuously over the simulation: RMSD, R_g, contact distances, and hydrogen bond counts.

Sturges' rule determines the number of histogram bins automatically:

$$N_{\text{bins}} = \lceil \log_2 N + 1 \rceil$$

where $N$ is the total number of data points (frames). This rule provides a conservative bin count that avoids over-smoothing for large datasets.

#### `"histogram_only"`

Produces only a distribution histogram (no time axis). Intended for angular observables such as sugar pucker pseudorotation angles or backbone dihedral angles, where the distribution shape matters more than temporal evolution.

#### `"rdf"`

Merges two ion RDF files from cpptraj, reports the peak position and peak g(r) value for each ion species, and plots both g(r) curves on a shared axis. Requires two separate `.txt` files as input (one per ion species).

### Time scaling

The `scale_x_to_ns()` function computes:

$$t_i = i \cdot \frac{T_{\text{total}}}{N_{\text{frames}}}$$

where $i$ is the frame index, $T_{\text{total}}$ is the value of `TOTAL_NS`, and $N_{\text{frames}}$ is the maximum frame index. This assumes uniform snapshot spacing throughout the trajectory. If frames were written at non-uniform intervals, this function will produce incorrect time values.

### Statistics written to `analysis_output.txt`

For each metric, the following statistics are appended to the cumulative report:

- Maximum value and the frame at which it occurs
- Minimum value and the frame at which it occurs
- Mean
- Median
- Standard deviation
- Top 5 frames by value (largest)
- Top 5 frames by value (smallest)

These extremal frames are useful starting points for structure extraction with cpptraj's `trajout` command to examine specific conformations.

---

## 7. Stage 3 — barnaba eRMSD and Master CSV

### What is eRMSD?

The **eRMSD** (extended RMSD) is an RNA-specific structural metric developed by Bottaro, Di Palma, and Bussi (2014). Unlike standard RMSD, which operates in Cartesian space and is sensitive to global translation and rotation, eRMSD encodes the **relative orientation of base pairs** through a set of dimensionless vectors $\vec{r}_{IJ}$ defined for each nucleotide pair $(I, J)$:

$$\vec{r}_{IJ} = \frac{1}{b} \mathbf{R}_I^{-1} (\mathbf{x}_J - \mathbf{x}_I)$$

where $\mathbf{x}_I$ and $\mathbf{x}_J$ are the centers of the bases, $\mathbf{R}_I$ is the local reference frame of base $I$, and $b = 3.4$ Å is a normalisation factor (the average base-stacking distance in A-form RNA). The eRMSD between two structures is then:

$$\text{eRMSD}(A, B) = \sqrt{\frac{1}{N} \sum_{IJ} \left| \vec{r}_{IJ}^A - \vec{r}_{IJ}^B \right|^2}$$

The key practical consequence is that eRMSD is **insensitive to backbone geometry and sugar pucker** — it measures whether the bases are in the same relative spatial arrangement, which is the correct criterion for asking whether an RNA has the same fold as a reference structure. A commonly used threshold for "folded" is **eRMSD < 0.7** relative to the native structure.

### How Stage 3 runs

```python
import barnaba as bb

ermsd = bb.ermsd(native_pdb, trajectory_nc, topology=topology_prmtop)
rmsd  = bb.rmsd(native_pdb, trajectory_nc, topology=topology_prmtop, heavy_atom=True)
```

barnaba reads the AMBER trajectory directly via MDTraj (which requires both the `.nc` trajectory and `.prmtop` topology). It returns a NumPy array of length $N_{\text{frames}}$ for each metric.

The heavy-atom RMSD computed by barnaba uses its own superposition code and is reported in **nanometers** (not Ångströms). Keep this in mind when comparing with cpptraj RMSD values, which are in Ångströms.

### Master CSV assembly

After the eRMSD and RMSD arrays are computed, Stage 3 merges them with any additional columns requested in `ERMSD_CONFIG["extra_columns"]`. Each extra column is read from a CSV produced in Stage 2 and aligned by row index (i.e., frame order). The result is written to `ermsd_metrics.csv`:

| Column | Units | Source |
|--------|-------|--------|
| `Frame` | — | integer index |
| `eRMSD` | dimensionless | barnaba |
| `RMSD` | nm | barnaba |
| `RadiusOfGyration` | Å | Stage 2 (`radGyr.csv`) |
| `MinimumDistanceEnds` | Å | Stage 2 (`minDistEnds.csv`) |
| `MinimumDistanceG9-U6` | Å | Stage 2 |
| `MinimumDistanceG9-U6SugarBase` | Å | Stage 2 |
| `MinimumDistanceG9-U7SugarBase` | Å | Stage 2 |
| `MinimumDistanceU7-C8BasePhosphate` | Å | Stage 2 |
| `LoopRMSD` | Å | Stage 2 (`rmsd_toNMRLoop.csv`) |

**Important:** The number of rows in every extra-column CSV must equal the number of trajectory frames. If there is a mismatch, that column is silently dropped from the master CSV and a warning is printed.

---

## 8. Stage 4 — Cross-Metric 2-D Plots

### What is generated

For each entry in `CROSS_METRIC_PLOTS`, the function `plot_2d_suite()` generates four complementary plots from the same pair of columns in `ermsd_metrics.csv`:

| Filename suffix | Plot type | Use |
|----------------|-----------|-----|
| `_scatter.png` | Scatter plot (1 pt per frame) | Shows raw frame density and outliers |
| `_hist2d_logcount.png` | 2-D histogram, log-count colormap | Highlights sparsely sampled regions |
| `_hist2d_density.png` | 2-D histogram, probability density | Shows the true statistical weight of each region |
| `_contour.png` | Filled probability-density contour | Smooth representation of the free-energy landscape |

### Vertical reference lines

The `vlines` parameter adds a dashed vertical line at the specified x-axis value(s). For eRMSD plots, a line is drawn at eRMSD = 0.7 by convention, marking the boundary between "folded-like" (eRMSD < 0.7) and "unfolded" configurations.

### Current plot suites

- **eRMSD vs. RMSD** — The primary folding landscape. Frames in the lower-left (low eRMSD, low RMSD) represent folded states.
- **eRMSD vs. R_g** — Distinguishes compact misfolded states (low R_g but high eRMSD) from extended unfolded states.
- **eRMSD vs. Loop RMSD** — Determines whether the loop or the global fold unfolds first.
- **eRMSD vs. Minimum End-to-End Distance** — Quantifies hairpin compaction as a function of fold quality.

---

## 9. Utility Scripts

### `getFrameData.py`

Extracts the complete row from `ermsd_metrics.csv` for one or more specific frames. Useful for quickly retrieving all metrics for frames of interest identified from the plots.

```bash
# Single frame
python getFrameData.py 12345

# Multiple frames
python getFrameData.py 12345 67890 100000

# Save to a custom file
python getFrameData.py 12345 67890 results.txt
```

Output is a plain-text table with all columns from `ermsd_metrics.csv` for the requested frames.

### `eRMSD_createGIF.py`

Creates an animated GIF showing the evolution of the eRMSD–RMSD probability density landscape over time. The trajectory is divided into `n_time_windows` windows (default: 500) with fractional overlap (default: 20%). Axis ranges are fixed across all frames to allow visual comparison.

Configuration variables at the top of the script:

```python
n_time_windows = 500       # number of animation frames
overlap_fraction = 0.2     # fraction of overlap between consecutive windows
min_frames_per_window = 10000  # minimum frames for meaningful statistics
```

This script requires `ermsd_metrics.csv` to exist in the working directory (i.e., Stage 3 must have run first).

### `eRMSD_cumulativeEvolutionGIF.py`

Similar to `eRMSD_createGIF.py`, but shows a **cumulative** density: each animation frame includes all trajectory data from the beginning up to that point. This is useful for assessing convergence — a simulation that has converged will show a density landscape that stops changing significantly in later animation frames.

---

## 10. Adapting the Pipeline to a New Simulation

The recommended workflow for a new simulation is to start from `pipeline_template.py` rather than editing `full_pipeline.py` directly. `pipeline_template.py` contains only the configuration sections with no project-specific settings.

### Step-by-step

**1. Copy the template**

```bash
cp pipeline_template.py my_new_simulation.py
```

**2. Set global parameters**

```python
TOTAL_NS    = 500         # your simulation length
OUTPUT_FILE = "my_analysis.txt"
CPPTRAJ_EXE = "cpptraj"   # or full path if not on PATH
```

**3. Write cpptraj `.in` scripts**

Copy the most similar existing `.in` file from `scripts/` as a starting point. Adjust:
- The topology path (`parm ...`)
- The trajectory path (`trajin ...`)
- The residue mask (`:1-14` → whatever your system has)
- The output filename

Place the new `.in` file in `scripts/`.

**4. Add entries to `CPPTRAJ_JOBS`**

```python
CPPTRAJ_JOBS = [
    dict(
        in_file = "scripts/1_myObservable.in",
        copies  = [("myObservable.dat", "myObservable.txt")],
    ),
]
```

**5. Add entries to `METRICS`**

For a standard scalar observable:

```python
dict(
    type     = "time_series",
    txt      = "myObservable.txt",
    csv      = "myObservable.csv",
    columns  = ["Frame", "MyValue"],
    y_column = "MyValue",
    title    = "My Observable",
    unit     = "Å",
    fig      = "myObservable.png",
    hist     = True,
    hist_fig = "myObservable_Hist.png",
),
```

For an angular observable (no time axis):

```python
dict(
    type     = "histogram_only",
    txt      = "sugarPucker.txt",
    csv      = "sugarPucker.csv",
    columns  = ["Frame", "Pucker"],
    y_column = "Pucker",
    title    = "U7 Sugar Pucker",
    unit     = "°",
    fig      = "sugarPucker.png",
),
```

**6. Configure `ERMSD_CONFIG`**

Update the paths to your native reference PDB, trajectory, and topology, and add any extra columns you want merged into the master CSV.

**7. Add entries to `CROSS_METRIC_PLOTS`**

```python
dict(
    csv        = "ermsd_metrics.csv",
    x_col      = "eRMSD",
    y_col      = "MyValue",
    xlabel     = "eRMSD from native",
    ylabel     = "My Observable (Å)",
    out_prefix = "eRMSD_MyObs",
    vlines     = [0.7],
),
```

---

## 11. Configuration Reference

### `full_pipeline.py` top-level variables

| Variable | Type | Description |
|----------|------|-------------|
| `TOTAL_NS` | `float` | Total simulation length in nanoseconds. Used to convert frame indices to time. |
| `OUTPUT_FILE` | `str` | Path to the cumulative plain-text statistics report. Opened in append mode; delete before re-running if you want a clean report. |
| `CPPTRAJ_EXE` | `str` | Name or path of the cpptraj executable. Default `"cpptraj"` assumes it is on `$PATH`. |
| `FAIL_FAST` | `bool` | If `True`, the pipeline aborts immediately on the first cpptraj error. If `False` (default), it logs the error and continues with remaining jobs. |

### `CPPTRAJ_JOBS` entry keys

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `in_file` | `str` | yes | cpptraj input script filename |
| `copies` | `list` of `(src, dst)` | yes | List of `(source .dat, destination .txt)` pairs to copy after the run. Pass `[]` if no copies are needed. |

### `METRICS` entry keys

| Key | Types | Required | Description |
|-----|-------|----------|-------------|
| `type` | `str` | yes | `"time_series"`, `"histogram_only"`, or `"rdf"` |
| `txt` | `str` | yes (ts, hist) | Input `.txt` file (cpptraj output) |
| `csv` | `str` | yes | Output CSV path |
| `columns` | `list` | yes (ts, hist) | Column names; first must be `"Frame"` |
| `y_column` | `str` | yes (ts, hist) | Data column name |
| `title` | `str` | yes | Human-readable label for plots and the report |
| `unit` | `str` | yes | Physical unit (use `""` if dimensionless) |
| `fig` | `str` | yes | Output PNG path for the primary plot |
| `y_label` | `str` | no | Y-axis label override (defaults to `title`) |
| `hist` | `bool` | no | Also generate a histogram PNG (default `False`) |
| `hist_fig` | `str` | no | Histogram PNG path (required when `hist=True`) |
| `color` | `str` | no | Matplotlib color string (default `"darkslateblue"`) |
| `linewidth` | `float` | no | Time-series line width (default `0.3`) |
| `bins` | `int` | no | Histogram bins for `histogram_only` (default `50`) |
| `density` | `bool` | no | Probability density vs. frequency for `histogram_only` (default `True`) |
| `ion1`, `ion2` | `str` | yes (rdf) | Ion labels |
| `txt1`, `txt2` | `str` | yes (rdf) | RDF input files |

### `ERMSD_CONFIG` keys

| Key | Type | Description |
|-----|------|-------------|
| `native` | `str` | Path to the native reference PDB |
| `traj` | `str` | Path to the AMBER trajectory (`.nc`) |
| `top` | `str` | Path to the AMBER topology (`.prmtop`) |
| `master_csv` | `str` | Output master CSV filename |
| `extra_columns` | `list` | List of `(column_name, source_csv, source_column)` tuples |

### `CROSS_METRIC_PLOTS` entry keys

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `csv` | `str` | yes | CSV file containing both columns |
| `x_col` | `str` | yes | X-axis column name |
| `y_col` | `str` | yes | Y-axis column name |
| `xlabel` | `str` | yes | X-axis label |
| `ylabel` | `str` | yes | Y-axis label |
| `out_prefix` | `str` | yes | Filename prefix for the four output PNGs |
| `vlines` | `list` | no | X positions for vertical reference lines |
| `hlines` | `list` | no | Y positions for horizontal reference lines |
| `bins` | `int` | no | 2-D histogram bins (default `50`) |
| `cmap` | `str` | no | Matplotlib colormap (default `"viridis"`) |

---

## 12. Output Files Reference

### Intermediate files (generated by Stage 1 and Stage 2)

| File | Stage | Description |
|------|-------|-------------|
| `*.dat` | 1 | Raw cpptraj output (whitespace-delimited) |
| `*.txt` | 1 | Copy of `.dat` for Python to read |
| `*.csv` | 2 | Cleaned CSV with `Frame`, `Time(ns)`, and data column(s) |
| `*.png` | 2 | Time-series and histogram plots |
| `analysis_output.txt` | 2 | Cumulative statistics report (append mode) |

### Stage 3 and 4 outputs

| File | Description |
|------|-------------|
| `ermsd_metrics.csv` | Master CSV: `Frame`, `eRMSD`, `RMSD` (nm), and all extra columns |
| `eRMSD_RMSD_scatter.png` | Scatter: eRMSD vs RMSD |
| `eRMSD_RMSD_hist2d_logcount.png` | Log-count 2-D histogram |
| `eRMSD_RMSD_hist2d_density.png` | Probability density 2-D histogram |
| `eRMSD_RMSD_contour.png` | Filled probability-density contour |
| *(same pattern for other column pairs)* | |

### hbond-specific outputs from `1_hbondsLifetime.in`

| File | Description |
|------|-------------|
| `hbondLifetimeAvg.dat` | Per-bond average occupancy and lifetime |
| `hbondLifetime.gnu` | Per-bond time series (gnuplot format, also readable as CSV) |
| `hbondContactsLifetime.dat` | Lifetime autocorrelation for all contacts |
| `hbondLifetimeAvgLoop.dat` | Same as above, loop only |
| `hbondLifetimeLoop.gnu` | Same as above, loop only |
| `hbondContactsLifetimeLoop.dat` | Same as above, loop only |

---

## 13. Troubleshooting

### `cpptraj: command not found`

The AMBER module is not loaded. Run `module load amber/24.0` before executing the pipeline, or add it to `submit_pipeline.sh`.

### `barnaba is not installed`

The `rna` conda environment is not active. Run `conda activate rna`. If barnaba is missing from the environment: `pip install barnaba`.

### `[!] <file>.txt not found — skipping <metric>`

The cpptraj job that should produce this file either was not listed in `CPPTRAJ_JOBS`, failed silently, or produced a differently named output. Check `pipeline.err` (or your terminal stderr) for cpptraj error messages. With `FAIL_FAST = False`, cpptraj errors do not stop the pipeline.

### `[!] <source.csv> has N rows but trajectory has M frames`

A Stage 2 CSV has a different number of rows than the trajectory has frames. This usually means `TOTAL_NS` is wrong (causing `scale_x_to_ns` to silently pass), or that a cpptraj job was run on a different trajectory. Verify that all `.in` scripts point to the same trajectory file.

### eRMSD values seem too high (> 2.0 for every frame)

Check that `native` in `ERMSD_CONFIG` points to the correct reference PDB. barnaba requires the reference to have the same residue numbering as the trajectory topology. Residue numbering mismatches produce spurious eRMSD values rather than a crash.

### Out-of-memory errors when running barnaba on a long trajectory

barnaba loads the full trajectory into memory. For very long trajectories (> 10⁶ frames), you may need to run barnaba on a subset of frames. One approach is to use cpptraj to write a stride-sampled NetCDF file first:

```
parm ../../../stripped_trajectories/2KOCUnfolded_HRM_stripped.prmtop
trajin ../../../stripped_trajectories/2KOCUnfolded_HRM_production.nc 1 last 10
trajout traj_stride10.nc netcdf
run
quit
```

Then set `traj` in `ERMSD_CONFIG` to `"traj_stride10.nc"` and ensure that the extra-column CSVs are also stride-sampled (or that you use only every 10th row).

### Plots look empty or all values are zero

This almost always means the `.txt` file exists but contains only a header and no data rows. Open the file in a text editor and check for content. A common cause is that cpptraj ran but the `out` filename in the `.in` script does not match the `copies` entry in `CPPTRAJ_JOBS`.

---

## 14. Theoretical Background

### Why RMSD alone is insufficient for RNA

Standard heavy-atom RMSD measures Euclidean distance in 3-D Cartesian space after least-squares superposition. For RNA, this metric has two significant limitations. First, because RNA has many rotatable bonds and a flexible backbone, two structures with very similar base-stacking geometry can have large RMSD values simply because the backbone adopts a slightly different path. Second, RMSD is sensitive to the choice of atoms used for superposition: aligning on the backbone will give a different RMSD value than aligning on the bases. eRMSD addresses both issues by working in a normalized, local reference frame centered on each base.

### The folding criterion eRMSD < 0.7

The threshold of 0.7 was established empirically by Bottaro et al. by analyzing the distribution of eRMSD values within known crystal structure ensembles and between different crystal forms of the same RNA. Structures with eRMSD < 0.7 relative to a reference are considered to be in the same "basin" of conformational space — they have the same overall base-stacking topology. This threshold is more physically meaningful than an arbitrary RMSD cutoff because it is calibrated against real structural variability rather than against an arbitrary length scale.

### Radius of gyration as a compaction metric

The mass-weighted radius of gyration is:

$$R_g = \sqrt{\frac{\sum_i m_i |\mathbf{r}_i - \mathbf{r}_{\text{cm}}|^2}{\sum_i m_i}}$$

where $m_i$ is the mass of atom $i$ and $\mathbf{r}_{\text{cm}}$ is the center of mass. For a hairpin RNA, a folded state should have a small $R_g$ (compact structure) while an extended, unfolded state will have a large $R_g$. However, $R_g$ cannot distinguish between a correctly folded compact state and a misfolded one, which is why it is most useful in combination with eRMSD.

### Hydrogen bond analysis

cpptraj's `hbond` command uses a geometric definition: a hydrogen bond exists between a donor–hydrogen pair D–H and an acceptor A when the D···A distance is less than 3.5 Å and the D–H···A angle is greater than 120°. These are soft defaults; they can be tightened or loosened with the `dist` and `angle` keywords in the `.in` script. The lifetime analysis uses an autocorrelation approach to report both the average occupancy (fraction of frames where the bond is present) and the autocorrelation decay time.

---

*Generated March 2026 — Isabel Thompson, Computational Chemistry, University of Notre Dame*
