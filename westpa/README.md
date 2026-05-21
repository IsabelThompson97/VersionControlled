# WESTPA Weighted Ensemble Simulations

Rare-event sampling using the [WESTPA](https://westpa.github.io/westpa/) framework to characterize RNA hairpin folding/unfolding pathways and kinetics.

---

## Setups

| Directory | Progress Coordinate | Binning | Status |
|-----------|--------------------|---------|----|
| `Example1D_RMSD/` | 1D RMSD | Simple linear | Template/reference (incomplete) |
| `Example2D_RMSDMinDist/` | 2D: RMSD × MinDist | Recursive nested, 280 bins | Active |

---

## Directory Layout (both setups)

### Core configuration and scripts

```
<setup>/
├── west.cfg              Main WESTPA YAML config
├── system.py             Progress coordinate definition and bin mapper
├── env.sh                Environment variables (AMBER paths, conda env)
├── init.sh               Initialize run (create initial segments from bstates)
├── run.sh                Launch: w_run --work-manager processes
├── bstates/              Boundary state structures and pcoord extraction scripts
│   ├── bstates.txt       State definitions (name, pcoord, structure path)
│   └── StructureFiles/   One subdirectory per state with prmtop, rst7, md4.ncrst
├── common_files/         Shared AMBER topology and reference structures
└── westpa_scripts/       Per-segment execution scripts
    ├── runseg.sh         Propagates one MD segment (calls AMBER pmemd.cuda)
    ├── get_pcoord.sh     Extracts progress coordinate from completed segment
    └── post_iter.sh      Post-iteration hooks (cleanup, reweighting)
```

### Runtime data structure (created during execution)

WESTPA generates and organizes simulation data hierarchically by iteration and segment:

```
west_data/
├── 00000001/               Iteration 1
│   ├── seg_logs/           Per-segment execution logs
│   │   ├── 00000001.log    Segment 1 stderr/stdout output from runseg.sh
│   │   ├── 00000002.log    Segment 2 stderr/stdout output from runseg.sh
│   │   └── ...
│   └── traj_seg/           Per-segment trajectory data
│       ├── 00000001/       Segment 1 trajectory directory
│       │   ├── md4.ncrst   Initial state (amber restart)
│       │   ├── md5.nc      Production trajectory (amber netCDF)
│       │   └── md5.log     Amber MD logfile
│       ├── 00000002/       Segment 2 trajectory directory
│       │   ├── md4.ncrst
│       │   ├── md5.nc
│       │   └── md5.log
│       └── ...
├── 00000002/               Iteration 2
│   ├── seg_logs/
│   │   ├── 00000001.log    (reseeded from iter 1, recycles segment ID)
│   │   ├── 00000002.log
│   │   ├── 00000003.log    (new segments from splits)
│   │   └── ...
│   └── traj_seg/
│       ├── 00000001/
│       ├── 00000002/
│       ├── 00000003/
│       └── ...
├── 00000003/
│   └── ...
└── ...
```

**Key points:**
- `seg_logs/NNNNNNNN.log` — captured output from `runseg.sh` for each segment in that iteration
- `traj_seg/NNNNNNNN/` — AMBER trajectory files (`.nc`, `.ncrst`, `.log`) for each segment
- Segment IDs are **recycled** across iterations (e.g., seg 1 in iter 1 and iter 2 are distinct walkers)
- `.nc` files are AMBER NetCDF trajectories (binary); `.ncrst` are restart files
- Individual segment logs and trajectories can be stitched together via `amberTraj.sh` to reconstruct complete pathways

---

## Active 2D Setup: `Example2D_RMSDMinDist/`

**Progress coordinates:** RMSD (dim 0, Å) and MinDist (dim 1, Å)

**Binning scheme** (`system.py`): Recursive 4-quadrant mapper
- Outer split: RMSD at 10 Å, MinDist at 10 Å
- Quad0 (low RMSD, high MinDist): 7×2 = 14 bins
- Quad1 (high RMSD, high MinDist): 3×1 = 3 bins
- Quad2 (low RMSD, low MinDist): 52×5 = 260 bins — fine-grained near folded state
- Quad3 (high RMSD, low MinDist): 1×3 = 3 bins
- **Total: 280 bins**, 8 target walkers/bin
- Max iterations: 70; propagator: `pmemd.cuda`

**Additional subdirectories** (beyond standard layout):
- `progress_logs/` — bin scheme visualizations and project notes
- `analysis/` — analysis outputs

---

## Running a Simulation

```bash
cd Example2D_RMSDMinDist   # or Example1D_RMSD
source env.sh
bash init.sh               # creates initial walkers from boundary states
bash run.sh                # launches: w_run --work-manager processes
```

---

## Analysis

### Command-line tools

See `analysis.txt` (1D) and `analysis2D.txt` (2D) for `w_ipa` workflows covering bin populations, histograms, transition tracking, rate constants, and target flux evolution.

### Reconstruct a pathway trajectory

```bash
bash amberTraj.sh <iteration> <segment_id>
# Stitches segment .nc files into trajAnalysis/trace.nc for VMD
```

### Visualize the bin scheme

```bash
cd tools/binviz
python westpa_visualizer.py ../Example2D_RMSDMinDist/system.py \
    --xlabel "RMSD (Å)" --ylabel "MinDist (Å)" -o bins.png --summary
```

See `tools/binviz/README.md` for all options (PNG/PDF/SVG output, axis labels, nested bin support).

---

## 1D Template: `Example1D_RMSD/`

Reference only. `system.py` contains placeholder (`??`) values for bin boundaries — not ready to run. Use as a starting point for new 1D pcoord systems. Configured for 38 max iterations.
