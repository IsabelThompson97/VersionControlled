# RNA Hairpin MD Simulation Repository

Computational research repository for RNA hairpin folding dynamics using classical molecular dynamics and weighted ensemble sampling.

**Systems:** 1hs3 RNA hairpin (DE Shaw and OL3 force fields) and 2KOC UUCG tetraloop variant
**Methods:** AMBER MD, WESTPA weighted ensemble, cpptraj trajectory analysis, barnaba eRMSD
**Cluster:** Notre Dame CRC (SGE scheduler, `module load amber/24.0`, `rna` conda environment)

---

## Directory Structure

```
md_protocol/       AMBER simulation protocol: tLeap setup, equilibration, production, analysis tools
simulations/       Active simulation systems — force-field setups, equilibration, production runs
westpa/            Weighted ensemble (WESTPA) rare-event sampling configurations
utils/             Miscellaneous repository utilities (archiving, deployment, format conversion)
```

---

## Simulation Systems

Three active systems in `simulations/`:

| System | Force Field | Water Model | Notes |
|--------|-------------|-------------|-------|
| `1hs3_DEShaw/` | DE Shaw RNA | TIP4P-D | System setup only |
| `1hs3_OL3/` | Amber f99+bsc0+χOL3 | TIP3P | Full min/eq/production |
| `2KOC_OL3_HRM/` | Amber f99+bsc0+χOL3 | TIP3P | 14-residue UUCG tetraloop; folded + unfolded states |

All production runs: NVT 300 K, Langevin thermostat (γ = 1.0 ps⁻¹), 2 fs timestep, 50 M steps (100 ns) per block. See `simulations/README.md`.

---

## Weighted Ensemble Sampling

| Setup | Pcoord | Notes |
|-------|--------|-------|
| `westpa/Example1D_RMSD/` | 1D RMSD | Template/reference (incomplete) |
| `westpa/Example2D_RMSDMinDist/` | 2D: RMSD × MinDist | Active, 280 bins, recursive mapper |

See `westpa/README.md`.

---

## Running the Analysis Pipeline

```bash
cd md_protocol/03_analysis/claude_cpptraj_pipeline

# Edit full_pipeline.py: set TOTAL_NS, topology/trajectory paths, metric config
python full_pipeline.py

# Submit to CRC cluster
qsub submit_pipeline.sh
```

Outputs per-observable time-series plots, `ermsd_metrics.csv` (master table with eRMSD, RMSD, RoG, MinDist, LoopRMSD), and all 2D cross-metric plots. See `md_protocol/03_analysis/claude_cpptraj_pipeline/README.md`.

---

## Key Dependencies

- **Python:** `numpy`, `pandas`, `matplotlib`, `barnaba`, `pillow`
- **AMBER 24.0+:** `cpptraj`, `tleap`, `antechamber`, `parmchk2`
- On cluster: `module load amber/24.0` → `conda activate rna`
