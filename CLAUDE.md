# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Computational molecular dynamics (MD) research repository for RNA hairpin structure and dynamics. Core workflows:
1. **AMBER MD simulations** — system preparation, equilibration, production runs
2. **cpptraj post-processing** — trajectory analysis pipeline (`md_protocol/03_analysis/claude_cpptraj_pipeline/`)
3. **WESTPA weighted ensemble sampling** — rare-event pathway sampling (`westpa/`)

## Running the Analysis Pipeline

```bash
# Full end-to-end cpptraj + barnaba analysis
cd md_protocol/03_analysis/claude_cpptraj_pipeline
python full_pipeline.py

# Single-observable template (copy and customize)
python pipeline_template.py

# Generate conformational landscape GIFs
python eRMSD_createGIF.py
python eRMSD_cumulativeEvolutionGIF.py

# Submit to Notre Dame CRC cluster (SGE scheduler)
qsub submit_pipeline.sh
```

## Dependencies

- Python: `numpy`, `pandas`, `matplotlib`, `barnaba`, `pillow`
- External: AMBER 24.0+ (`cpptraj`, `tleap`, `antechamber`, `parmchk2`)
- On cluster: `module load amber/24.0` then `conda activate rna`

No `requirements.txt` exists — install manually or via conda/pip.

## Architecture: cpptrajPipeline

The pipeline in `md_protocol/03_analysis/claude_cpptraj_pipeline/` is the primary analysis tool. It runs in 4 stages:

1. **cpptraj jobs** — executes `.in` input scripts for each observable, outputs `.dat` files
2. **Process** — converts txt→csv, scales frames to nanoseconds, computes statistics, generates per-observable time-series plots
3. **eRMSD** — calls `barnaba` to compute eRMSD + heavy-atom RMSD, merges into a master CSV
4. **2D plots** — generates scatter, 2D histogram (log count), 2D histogram (density), and contour plots for all observable pairs

**Core library:** `md_protocol/03_analysis/claude_cpptraj_pipeline/scripts/cpptrajAnalysis.py` (~1668 lines)
- `convert_txt_to_csv()` — parses cpptraj whitespace-delimited output
- `scale_x_to_ns()` — converts frame numbers to nanosecond timescale
- `analyze_time_series()` — statistics + time-series plots
- `analyze_histogram_only()` — for angular observables
- `plot_2d_suite()` — all 4 2D plot types
- `process_rdf()` — ion radial distribution function analysis

`full_pipeline.py` orchestrates all stages; `pipeline_template.py` is the per-observable customization entry point.

The project-configured analysis (with actual trajectory outputs) lives alongside the pipeline at `md_protocol/03_analysis/cpptraj/`.

## Architecture: WESTPA

WESTPA configurations live in `westpa/Example1D_RMSD/` (1D RMSD template) and `westpa/Example2D_RMSDMinDist/` (active 2D setup):

- `west.cfg` — main YAML config (iteration limits, data storage paths, propagation, analysis schemes)
- `system.py` — defines progress coordinate (pcoord) dimensions and recursive bin mapper for hierarchical phase-space exploration
- `westpa_scripts/runseg.sh` — propagates individual trajectory segments
- `westpa_scripts/get_pcoord.sh` — extracts progress coordinate from each segment
- `westpa_scripts/post_iter.sh` — post-iteration hooks

The active 2D setup uses RMSD (dim 0) × MinDist (dim 1) as progress coordinates with a recursive 4-quadrant bin mapper (280 bins total, targeting 8 walkers/bin).

Bin visualization: `westpa/tools/binviz/westpa_visualizer.py`

## Simulation Protocol

`md_protocol/` contains the full AMBER setup protocol:
- `0_leap.in` — tLeap system parameterization template
- `01_min_eq/` — Minimization (min1, min2) and equilibration (md1–md4) scripts; includes GPU variants (`*GPU.sh`) and `postmd3_calcboxlength.py`
- `02_production/` — 10 × sequential 100 ns NVT blocks (`md_final.in` through `md_final_10.in`) + annotated template
- `03_analysis/` — pipeline tools, project cpptraj outputs, average structure workflow
- `utils/` — cpptraj utilities: `makePDB.in`, `strip.in`, `cpptraj_process.sh`
- `x_OriginalFilesNell/` — original protocol archive from collaborator

## Observable Scripts

13 cpptraj `.in` scripts in `md_protocol/03_analysis/claude_cpptraj_pipeline/scripts/` cover: RMSD (to NMR, backbone, stem, loop, bases), minimum distances (loop ends, contacts), radius of gyration, hydrogen bond counts/lifetimes, and ion RDF.
