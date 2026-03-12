# ClaudeCpptrajAnalysis

A generalised Python library for post-processing AMBER/cpptraj MD simulation
output.  Works with any trajectory length and any scalar observable that
cpptraj writes as a whitespace-delimited text file.

---

## Package contents

```
CpptrajPipeline/
├── README_ClaudeCpptrajAnalysis.md   ← this file
│
├── ClaudeCpptrajAnalysis.py          ← Python library (required by both pipelines)
├── full_pipeline.py                  ← end-to-end pipeline: cpptraj → eRMSD → plots
├── pipeline_template.py              ← Python-only pipeline (cpptraj already ran)
├── submit_pipeline.sh                ← SGE job script (Notre Dame CRC)
├── C_get_data.py                     ← utility: look up metrics for specific frames
├── eRMSD_createGIF.py                ← sliding-window eRMSD/RMSD density animation
├── eRMSD_cumulativeEvolutionGIF.py   ← cumulative eRMSD/RMSD density animation
│
└── 1_*.in                            ← cpptraj input scripts (one per observable)
    ├── 1_radiusGyr.in
    ├── 1_rmsd.in
    ├── 1_rmsdtoNMR.in
    ├── 1_rmsdtoNMRBackbone.in
    ├── 1_rmsdtoNMRStem.in
    ├── 1_rmsdtoNMRLoop.in
    ├── 1_rmsdtoNMR1-14Bases.in
    ├── 1_minDistEnds.in
    ├── 1_minDistLoopContacts.in
    ├── 1_hbondFrames.in
    ├── 1_hbondsLifetime.in
    ├── 1_hbondsLifetimeLoop.in
    └── 1_IonRDF.in                   (commented out by default — ion RDF)
```

> **Not included:** trajectory (`.nc`), topology (`.prmtop`), and reference
> structure files (`.pdb`, `.rst7`).  These stay with each simulation directory
> and are referenced by path inside the scripts.

---

## Adapting to a new project

### 1. Copy this directory into your simulation's analysis folder

```bash
cp -r CpptrajPipeline/ /path/to/your/sim/analysis/cpptraj/
cd /path/to/your/sim/analysis/cpptraj/
```

### 2. Add your reference structure files

Place your native/reference `.pdb`, `.prmtop`, and `.rst7` files in this
directory (needed by the RMSD-to-reference `.in` scripts and barnaba).

### 3. Edit `full_pipeline.py`

At minimum, update the top-level configuration block:

```python
TOTAL_NS    = 500          # your simulation length
OUTPUT_FILE = "analysis_output.txt"
```

In `ERMSD_CONFIG`:
```python
ERMSD_CONFIG = dict(
    native = "your_native.pdb",
    traj   = "../../stripped_trajectories/your_production.nc",
    top    = "../../stripped_trajectories/your_stripped.prmtop",
    ...
)
```

### 4. Edit the `1_*.in` scripts

Update the `parm` and `trajin` lines in each `.in` file to point to your
topology and trajectory:

```
parm ../../stripped_trajectories/your_stripped.prmtop
trajin ../../stripped_trajectories/your_production.nc
```

For RMSD-to-reference scripts, update the reference parm and rst7:
```
parm your_native.prmtop [NMR]
reference your_native.rst7 [NMR] parm [NMR]
```

Update atom masks to match your residue numbering (e.g. `:1-14` for a
14-residue RNA).

### 5. Edit `submit_pipeline.sh`

Update the `cd` path and job name:

```bash
#$ -N my_analysis
cd /path/to/your/sim/analysis/cpptraj
```

### 6. Submit

```bash
qsub submit_pipeline.sh
```

---

## Files

| File | Purpose |
|---|---|
| `ClaudeCpptrajAnalysis.py` | Library — all functions documented here |
| `full_pipeline.py` | **Recommended** — single end-to-end pipeline (cpptraj → stats → eRMSD → 2-D plots) |
| `pipeline_template.py` | Python-only pipeline (no cpptraj subprocess, no barnaba); use when cpptraj has already run |
| `submit_pipeline.sh` | SGE job script for Notre Dame CRC — submits `full_pipeline.py` |
| `C_get_data.py` | Query `ermsd_metrics.csv` for specific frame numbers |
| `eRMSD_createGIF.py` | Sliding-window animated GIF of eRMSD vs RMSD probability density |
| `eRMSD_cumulativeEvolutionGIF.py` | Cumulative animated GIF — density builds from frame 0 forward |
| `1_*.in` | cpptraj input scripts — one per observable |
| `README_ClaudeCpptrajAnalysis.md` | This file |

---

## Cluster submission (Notre Dame CRC)

```bash
qsub submit_pipeline.sh
```

`submit_pipeline.sh` loads `amber/24.0` (for cpptraj) and activates the
`rna` conda environment (Python 3.12, barnaba, numpy, pandas, matplotlib),
then runs `full_pipeline.py` from the correct working directory.

Monitor the job:

```bash
qstat -u ithomps3          # check job status
cat pipeline.log           # live stdout
cat pipeline.err           # warnings / errors
```

To re-run only selected stages without resubmitting cpptraj, set at the
top of `full_pipeline.py`:

```python
CPPTRAJ_JOBS = []   # skip Stage 1 — cpptraj already ran
```

---

## Dependencies

| Package | Used for |
|---|---|
| `numpy` | Numerical operations, histogram bins |
| `pandas` | CSV I/O, statistics |
| `matplotlib` | All plots |
| `barnaba` | eRMSD and heavy-atom RMSD vs. native structure |

All are available in the `rna` conda environment
(`/users/ithomps3/.conda/envs/rna`).

---

## Quick-start

### 1. Per-observable workflow

```python
from ClaudeCpptrajAnalysis import convert_txt_to_csv, scale_x_to_ns, analyze_time_series

convert_txt_to_csv("radGyr.txt", "radGyr.csv", ["Frame", "RoG"])
scale_x_to_ns("radGyr.csv", total_ns=1000)
analyze_time_series(
    "radGyr.csv", "RoG", "report.txt",
    title_prefix="Radius of Gyration", unit="Å", fig_path="radGyr.png",
)
```

### 2. Cross-metric 2-D plots

```python
import pandas as pd
from ClaudeCpptrajAnalysis import plot_2d_suite

data = pd.read_csv("ermsd_metrics.csv")
plot_2d_suite(
    data["eRMSD"].values, data["RadiusOfGyration"].values,
    xlabel="eRMSD from native",
    ylabel="Radius of Gyration (Å)",
    out_prefix="eRMSD_RoG",
    vlines=[0.7],          # draw a dashed line at eRMSD = 0.7
)
# Saves: eRMSD_RoG_scatter.png, _hist2d_logcount.png,
#        _hist2d_density.png, _contour.png
```

### 3. Data-driven pipeline

Copy `pipeline_template.py` into your analysis directory, edit
`TOTAL_NS`, `OUTPUT_FILE`, and the `METRICS` / `CROSS_METRIC_PLOTS`
lists, then run:

```bash
python pipeline_template.py
```

---

## Function Reference

### Data I/O

---

#### `convert_txt_to_csv(input_txt_path, output_csv_path, column_names, skiprows=1, sep=r'\s+')`

Convert a whitespace-delimited cpptraj output file to CSV.

| Parameter | Type | Description |
|---|---|---|
| `input_txt_path` | str | cpptraj `.dat` / `.txt` file |
| `output_csv_path` | str | Destination `.csv` |
| `column_names` | list[str] | Column labels; first must be `"Frame"` |
| `skiprows` | int | Header rows to skip (default 1) |
| `sep` | str | Separator regex (default `r'\s+'`) |

**Example**
```python
convert_txt_to_csv("rmsd_toNMR.txt", "rmsd_toNMR.csv", ["Frame", "RMSD"])
convert_txt_to_csv("sugarPucker.txt", "sugarPucker.csv", ["Frame", "Pucker"])
```

---

#### `scale_x_to_ns(csv_path, total_ns, time_column="Time(ns)", frame_column="Frame")`

Add or overwrite a `Time(ns)` column by scaling frame numbers.

Scaling: `Time(ns) = Frame × (total_ns / max_frame)`

The CSV is modified in place.  Call this after `convert_txt_to_csv` and
before any `analyze_*` function.

| Parameter | Type | Description |
|---|---|---|
| `csv_path` | str | CSV to modify in place |
| `total_ns` | float | Total simulation length in ns |
| `time_column` | str | Column to create/update (default `"Time(ns)"`) |
| `frame_column` | str | Frame-index column (default `"Frame"`) |

**Example**
```python
scale_x_to_ns("radGyr.csv", total_ns=1000)
scale_x_to_ns("rmsd.csv",   total_ns=500, time_column="t_ns")
```

---

### Statistics & reporting

All `analyze_*` functions append a formatted block to `output_file_path`.
The block includes maximum, minimum, mean, median (where applicable),
standard deviation, and top-5 / bottom-5 frames.

---

#### `analyze_time_series(...)`

Compute stats, write a time-series line plot, and (optionally) a
histogram.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `csv_path` | str | — | CSV with Frame, Time(ns), and data column |
| `y_column` | str | — | Observable column name |
| `output_file_path` | str | — | Summary report (append mode) |
| `title_prefix` | str | — | Human-readable label, e.g. `"Radius of Gyration"` |
| `unit` | str | `""` | Physical unit, e.g. `"Å"` or `"°"` |
| `y_label` | str | `""` | Y-axis label (defaults to `title_prefix`) |
| `time_column` | str | `"Time(ns)"` | Time column name |
| `frame_column` | str | `"Frame"` | Frame-index column name |
| `fig_path` | str | `"plot.png"` | Time-series PNG output path |
| `has_hist` | bool | `False` | Also save a histogram |
| `hist_fig_path` | str | `None` | Histogram PNG path (auto-derived when `None`) |
| `linewidth` | float | `0.3` | Line width |
| `color` | str | `"darkslateblue"` | Line and bar colour |

The histogram uses **Sturges' rule** for bin count:
`n_bins = ceil(log2(N) + 1)`.  Mean (red) and median (green) are marked.

**Example**
```python
analyze_time_series(
    "rmsd_toNMR.csv", "RMSD", "report.txt",
    title_prefix="RMSD to NMR", unit="Å",
    fig_path="rmsd_toNMR.png",
    has_hist=True, hist_fig_path="rmsd_toNMR_Hist.png",
)
```

---

#### `analyze_histogram_only(...)`

Same as `analyze_time_series` but saves only a histogram — no time axis.
Use for angular observables (sugar pucker, dihedrals) where the
distribution is of primary interest.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `csv_path` | str | — | CSV with Frame and data column |
| `y_column` | str | — | Observable column name |
| `output_file_path` | str | — | Summary report (append mode) |
| `title_prefix` | str | — | Human-readable label |
| `unit` | str | `""` | Physical unit |
| `frame_column` | str | `"Frame"` | Frame-index column name |
| `fig_path` | str | `"hist.png"` | Output PNG path |
| `bins` | int | `50` | Number of histogram bins |
| `color` | str | `"purple"` | Bar fill colour |
| `edgecolor` | str | `"purple"` | Bar edge colour |
| `density` | bool | `True` | Plot probability density vs. frequency |

**Example**
```python
analyze_histogram_only(
    "sugarPucker_U7.csv", "Pucker", "report.txt",
    title_prefix="U7 Sugar Pucker", unit="°",
    fig_path="sugarPucker_U7.png",
)
```

---

#### `process_rdf(ion1, txt_path1, ion2, txt_path2, output_csv_path, output_file_path, fig_path, ...)`

Merge two ion RDF files, report peak positions, and plot g(r).

Each input `.txt` must be a two-column cpptraj RDF output: `Distance` and
`g(r)`.

| Parameter | Type | Description |
|---|---|---|
| `ion1` | str | Label for ion 1, e.g. `"Na+"` |
| `txt_path1` | str | RDF `.txt` for ion 1 |
| `ion2` | str | Label for ion 2, e.g. `"Cl-"` |
| `txt_path2` | str | RDF `.txt` for ion 2 |
| `output_csv_path` | str | Merged CSV (Distance, ion1, ion2) |
| `output_file_path` | str | Summary report (append mode) |
| `fig_path` | str | Output PNG path |
| `title` | str | Plot title (default `"Radial Distribution Function"`) |
| `xlabel` | str | X-axis label (default `"Distance (Å)"`) |
| `ylabel` | str | Y-axis label (default `"g(r)"`) |
| `color1` | str | Line colour for ion 1 (default `"darkslateblue"`) |
| `color2` | str | Line colour for ion 2 (default `"darkorange"`) |

**Example**
```python
process_rdf(
    "Na+", "RDF-Na.txt",
    "Cl-", "RDF-Cl.txt",
    "RDF_ions.csv", "report.txt", "RDF_ions.png",
)
```

---

#### `append_to_output(output_file_path, text)`

Append a block of text to the summary report (file created if absent).

```python
append_to_output("report.txt", "Custom note: equilibration ends at frame 5000.")
```

---

### 2-D cross-metric plotting

These functions operate on **numpy arrays** (not CSV paths) and are
designed for visualising relationships between pairs of observables stored
in a master metrics CSV.

---

#### `plot_scatter(x_vals, y_vals, xlabel, ylabel, title, out_path, ...)`

Scatter plot of two arrays.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `x_vals`, `y_vals` | array-like | — | Data arrays (equal length) |
| `xlabel`, `ylabel` | str | — | Axis labels |
| `title` | str | — | Plot title |
| `out_path` | str | — | Output PNG |
| `vlines` | list[float] | `None` | X positions for vertical reference lines |
| `hlines` | list[float] | `None` | Y positions for horizontal reference lines |
| `s` | float | `1` | Marker size |
| `alpha` | float | `0.5` | Marker transparency |
| `color` | str | `"steelblue"` | Marker colour |
| `figsize` | tuple | `(8,6)` | Figure size in inches |
| `dpi` | int | `300` | Output resolution |

---

#### `plot_hist2d(x_vals, y_vals, xlabel, ylabel, title, out_path, ..., mode="density")`

2-D histogram with two colour-scaling modes:

| `mode` | Colour scale | Colour bar label |
|---|---|---|
| `"density"` | Probability density; zero bins → white | Probability Density |
| `"log_count"` | Raw counts, logarithmic | Count (log scale) |

All parameters are the same as `plot_scatter` plus:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `bins` | int | `50` | Bins per axis |
| `mode` | str | `"density"` | `"density"` or `"log_count"` |
| `cmap` | str | `"viridis"` | Matplotlib colourmap |

---

#### `plot_contour(x_vals, y_vals, xlabel, ylabel, title, out_path, ...)`

Filled probability-density contour.  Uses `numpy.histogram2d` for density
estimation, then `contourf` + semi-transparent white contour lines.

Additional parameters:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `bins` | int | `50` | Histogram resolution |
| `levels_fill` | int | `20` | Number of filled contour levels |
| `levels_line` | int | `10` | Number of white overlay contour lines |
| `cmap` | str | `"viridis"` | Matplotlib colourmap |

---

#### `plot_2d_suite(x_vals, y_vals, xlabel, ylabel, out_prefix, ...)`

Generate all four 2-D plot types in one call.

**Output files**

| Suffix | Plot type |
|---|---|
| `_scatter.png` | Scatter |
| `_hist2d_logcount.png` | 2-D histogram, log-count colour scale |
| `_hist2d_density.png` | 2-D histogram, probability density |
| `_contour.png` | Probability density contour |

| Parameter | Type | Default | Description |
|---|---|---|---|
| `x_vals`, `y_vals` | array-like | — | Data arrays |
| `xlabel`, `ylabel` | str | — | Axis labels (shared by all four plots) |
| `out_prefix` | str | — | Filename prefix, may include directory |
| `vlines` | list[float] | `None` | Reference lines on x axis |
| `hlines` | list[float] | `None` | Reference lines on y axis |
| `bins` | int | `50` | Bins for histogram/contour plots |
| `cmap` | str | `"viridis"` | Colourmap for histogram/contour plots |
| `figsize` | tuple | `(8,6)` | Figure size for each plot |
| `dpi` | int | `300` | Resolution for each plot |

**Example**
```python
import pandas as pd
from ClaudeCpptrajAnalysis import plot_2d_suite

data = pd.read_csv("ermsd_metrics.csv")

plot_2d_suite(
    data["eRMSD"].values, data["LoopRMSD"].values,
    xlabel="eRMSD from native",
    ylabel="Loop RMSD (Å)",
    out_prefix="eRMSD_LoopRMSD",
    vlines=[0.7],
)
```

---

## Using `full_pipeline.py` (recommended)

`full_pipeline.py` runs everything in order: cpptraj → per-observable
analysis → barnaba eRMSD → cross-metric 2-D plots.

```bash
module load amber/24.0
python full_pipeline.py
```

### Four stages, all configurable at the top of the file

| Stage | Config variable | What it does |
|---|---|---|
| 1 — cpptraj | `CPPTRAJ_JOBS` | Runs each `.in` script, copies `.dat → .txt` |
| 2 — Process | `METRICS` | txt→csv, scale to ns, stats, time-series/histogram plots |
| 3 — eRMSD | `ERMSD_CONFIG` | barnaba eRMSD + RMSD; merges cpptraj CSVs → `ermsd_metrics.csv` |
| 4 — 2-D plots | `CROSS_METRIC_PLOTS` | `plot_2d_suite` for every column pair |

**Skip a stage** by setting its variable to `[]` or `None`:

```python
CPPTRAJ_JOBS       = []    # skip Stage 1 (cpptraj already ran)
ERMSD_CONFIG       = None  # skip Stages 3 and 4
CROSS_METRIC_PLOTS = []    # skip Stage 4 only
```

**Abort on cpptraj error** (default is to warn and continue):

```python
FAIL_FAST = True
```

### Adding a new observable end-to-end

1. Write `1_myObs.in` (cpptraj input script outputting `myObs.dat`).
2. Add to `CPPTRAJ_JOBS`:
   ```python
   dict(in_file="1_myObs.in", copies=[("myObs.dat", "myObs.txt")]),
   ```
3. Add to `METRICS`:
   ```python
   dict(
       type="time_series", txt="myObs.txt", csv="myObs.csv",
       columns=["Frame", "MyObs"], y_column="MyObs",
       title="My Observable", unit="Å", fig="myObs.png",
   ),
   ```
4. To include it in cross-metric plots, add to `ERMSD_CONFIG["extra_columns"]`:
   ```python
   ("MyObs", "myObs.csv", "MyObs"),
   ```
5. Add to `CROSS_METRIC_PLOTS`:
   ```python
   dict(csv="ermsd_metrics.csv", x_col="eRMSD", y_col="MyObs",
        xlabel="eRMSD from native", ylabel="My Observable (Å)",
        out_prefix="eRMSD_MyObs", vlines=[0.7]),
   ```

---

## Using `pipeline_template.py`

The template is a self-contained script that runs the full per-observable
pipeline followed by all 2-D cross-metric plots.

### Step 1 — Edit the configuration block

```python
TOTAL_NS    = 1000           # change to match your simulation
OUTPUT_FILE = "analysis_output.txt"
```

### Step 2 — Edit METRICS

Each entry is a plain Python `dict`.  Three types are supported:

```python
# Time-series observable
dict(
    type     = "time_series",
    txt      = "myObs.txt",       # cpptraj output
    csv      = "myObs.csv",       # intermediate CSV
    columns  = ["Frame", "Obs"],  # must match columns in txt
    y_column = "Obs",             # column to plot
    title    = "My Observable",   # label for plots and report
    unit     = "Å",
    fig      = "myObs.png",
    hist     = True,              # also save histogram
    hist_fig = "myObs_Hist.png",
),

# Histogram-only observable (no time axis)
dict(
    type     = "histogram_only",
    txt      = "sugarPucker.txt",
    csv      = "sugarPucker.csv",
    columns  = ["Frame", "Pucker"],
    y_column = "Pucker",
    title    = "Sugar Pucker",
    unit     = "°",
    fig      = "sugarPucker.png",
),

# Ion RDF
dict(
    type = "rdf",
    ion1 = "Na+",  txt1 = "RDF-Na.txt",
    ion2 = "Cl-",  txt2 = "RDF-Cl.txt",
    csv  = "RDF_ions.csv",
    fig  = "RDF_ions.png",
),
```

### Step 3 — Edit CROSS_METRIC_PLOTS (optional)

These run after all per-observable processing.  They require a master CSV
(e.g. produced by `A_calc_eRMSDMetrics_save.py`) that merges all metrics
into one file.

```python
dict(
    csv        = "ermsd_metrics.csv",
    x_col      = "eRMSD",
    y_col      = "RadiusOfGyration",
    xlabel     = "eRMSD from native",
    ylabel     = "Radius of Gyration (Å)",
    out_prefix = "eRMSD_RoG",
    vlines     = [0.7],
),
```

Set `CROSS_METRIC_PLOTS = []` to skip this section entirely.

### Step 4 — Run

```bash
python pipeline_template.py
```

---

## Adding a new observable (checklist)

1. Write a `1_<name>.in` cpptraj input script that outputs `<name>.dat`.
2. Add `cpptraj -i 1_<name>.in` and `cp <name>.dat <name>.txt` to
   `2_cpptraj.sh`.
3. Add an entry to `METRICS` in `pipeline_template.py`.
4. If the observable should appear in cross-metric 2-D plots, add a column
   to `A_calc_eRMSDMetrics_save.py` and add an entry to
   `CROSS_METRIC_PLOTS`.

---

## GIF Animation Scripts

Two standalone scripts generate animated GIFs that visualise how the
eRMSD vs RMSD probability-density landscape evolves over the course of a
trajectory.  Both read from `ermsd_metrics.csv` and write a GIF to the
current directory.

**Prerequisite:** `pillow` must be installed (`pip install pillow`).
It is already present in the `rna` conda environment.

---

### `eRMSD_createGIF.py` — sliding-window animation

Each frame of the GIF shows the probability-density contour for a
**sliding time window** of the trajectory.  The window moves forward
through time, so the animation reveals how the sampled conformational
landscape shifts as the simulation progresses.

**Configuration (top of file)**

| Variable | Default | Description |
|---|---|---|
| `n_time_windows` | `500` | Number of GIF frames |
| `overlap_fraction` | `0.2` | Fraction of window overlap between consecutive frames |
| `min_frames_per_window` | `10000` | Minimum trajectory frames per window; warns if fewer |

**Fixed plot axes**

| Axis | Range |
|---|---|
| eRMSD (x) | 0.2 – 1.7 |
| RMSD / nm (y) | 0.0 – 0.8 |

The colour scale is globally normalised to the full-trajectory density
so all frames share a consistent scale.

**Output files**

| File | Description |
|---|---|
| `movie_frames/frame_*.png` | Individual PNG frames (150 dpi) |
| `D_probability_density_evolution.gif` | Animated GIF (5 fps, 100 dpi) |

**Usage**

```bash
# Make sure ermsd_metrics.csv is present in the current directory
python eRMSD_createGIF.py
```

**Key functions**

```python
create_movie_frames(save_individual_frames=True)
    # Writes movie_frames/frame_NNN.png for each window
    # Returns total number of frames created

create_animated_gif()
    # Builds GIF directly via matplotlib FuncAnimation + pillow writer
    # Does NOT require pre-existing frame PNGs
```

---

### `eRMSD_cumulativeEvolutionGIF.py` — cumulative animation

Each frame of the GIF shows the probability-density contour for **all
data from frame 0 up to a progressively later endpoint**.  The density
landscape accumulates over time, showing how statistics converge (or
continue to shift) as more of the trajectory is included.

A percentage-complete overlay (lightblue box, top-right corner) shows
how far through the trajectory the current frame reaches.

**Configuration (top of file)**

| Variable | Default | Description |
|---|---|---|
| `n_movie_frames` | `500` | Number of GIF frames |
| `min_frames_per_step` | `10000` | First GIF frame includes trajectory frames 0 → `min_frames_per_step` |

Endpoints are spaced with `numpy.linspace(min_frames_per_step, total_frames, n_movie_frames)`,
so coverage grows linearly from the minimum to the full trajectory.

**Fixed plot axes** — same as the sliding-window script (eRMSD 0.2–1.7,
RMSD 0.0–0.8).  The colour scale is normalised to the full-trajectory
density.

**Output files**

| File | Description |
|---|---|
| `cumulative_movie_frames/frame_*.png` | Individual PNG frames (150 dpi) |
| `D_cumulative_probability_density_evolution.gif` | Animated GIF (5 fps, 100 dpi) |

**Usage**

```bash
python eRMSD_cumulativeEvolutionGIF.py
```

**Key functions**

```python
create_cumulative_movie_frames(save_individual_frames=True)
    # Writes cumulative_movie_frames/frame_NNN.png
    # Returns number of frames created

create_cumulative_animated_gif()
    # Builds GIF via FuncAnimation + pillow writer
```

---

### Choosing between the two scripts

| | Sliding-window | Cumulative |
|---|---|---|
| **Question answered** | How does the local landscape change over time? | How do statistics converge as more data are included? |
| **Each frame covers** | One window of `total_frames / n_windows` frames | All frames from 0 to the current endpoint |
| **Good for** | Detecting non-stationarity, late-simulation conformational changes | Checking whether the simulation has converged |

---

## eRMSD reference

The eRMSD threshold of **0.7** is used as a rule-of-thumb native-like
cutoff (Bottaro et al., *Nucleic Acids Res.*, 2014).  Structures with
eRMSD < 0.7 are considered significantly similar to the reference.
This value is passed as `vlines=[0.7]` in all cross-metric plots that
use eRMSD on the x axis.
