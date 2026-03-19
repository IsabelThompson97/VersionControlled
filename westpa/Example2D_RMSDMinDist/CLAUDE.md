# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
You have access to skills in ~/.claude/skills/

## Project Overview

This is a **WESTPA weighted ensemble molecular dynamics simulation** studying **folding of the 2KOC RNA hairpin (14 residues)**. The simulation uses a **2D progress coordinate strategy** with:

- **dim 0 — RMSD (Å)**: heavy-atom RMSD to the NMR folded reference structure (`2KOCFolded_NMR.rst7`), mask `:1-14&!@H=`
- **dim 1 — MinDist (Å)**: minimum distance between residue 1 and residue 14 (via `nativecontacts :1 :14 mindist`)

> **Note**: dim order is the reverse of Trial5. Here RMSD is dim 0, MinDist is dim 1.

Basis state (unfolded): high RMSD, high MinDist. Target state (folded): RMSD≈0.5 Å, MinDist≈0.5 Å. Progress direction is **decreasing** in both dimensions.

## Environment Setup

```bash
source env.sh   # loads westpa/2022.10, mpich, cuda/10.2; sets AMBERHOME and AMBER_EXEC
```

Key environment variables set by `env.sh`:
- `WEST_SIM_ROOT=$PWD`
- `AMBER_EXEC=/opt/crc/a/amber/22.0/amber22/bin/pmemd.cuda` (GPU-accelerated AMBER MD)
- `CPPTRAJ=$AMBERHOME/bin/cpptraj`

## Simulation Commands

```bash
# Initialize simulation (clean start — deletes traj_segs, seg_logs, west.h5)
bash init.sh            # runs w_init with bstates/bstates.txt, 8 segs/state

# Submit production run (Notre Dame CRC, gpu queue)
qsub run.sh             # w_run --work-manager processes, job name: fRMSDMinDist_2KOC

# Check bin occupancy (only when simulation is NOT running)
w_bins info --detail --bins-from-system > bins.log

# Restart after crash (appends to existing west.h5)
source env.sh && w_run --work-manager processes
```

## Analysis Commands

```bash
source env.sh
mkdir -p ANALYSIS

# Probability distribution
w_pdist -W west.h5

# 2D average probability distribution
plothist average pdist.h5 0::'RMSD (Å)' 1::'MinDist (Å)' -o ANALYSIS/avg.pdf

# Per-dimension evolution plots
plothist evolution pdist.h5 0::'RMSD (Å)'    -o ANALYSIS/histRMSD.pdf
plothist evolution pdist.h5 1::'MinDist (Å)' -o ANALYSIS/histMinDist.pdf

# Interactive Python analysis
w_ipa
```

## Architecture

### Key Files
| File | Role |
|------|------|
| `west.cfg` | Master WESTPA config: propagator, data refs, analysis scheme (TEST), plugins |
| `system.py` | Python bin mapper — 2D RecursiveBinMapper with 4 quadrants, split at RMSD=10/MinDist=10 |
| `env.sh` | Environment setup (source before any WESTPA command) |
| `init.sh` | One-time initialization; deletes `traj_segs/`, `seg_logs/`, `west.h5` |
| `run.sh` | SGE job submission script (`-q gpu`, `-l gpu_card=1`, `-pe smp 8`) |

### WESTPA Scripts (`westpa_scripts/`)
| Script | Called by | Role |
|--------|-----------|------|
| `runseg.sh` | WESTPA per segment | Runs `pmemd.cuda`, then `cpptraj` to extract MinDist and RMSD (pasted as RMSD, MinDist) |
| `get_pcoord.sh` | WESTPA for bstates | Reads pcoord from bstate `pcoordreturn.dat` |
| `post_iter.sh` | WESTPA post-iteration | Backs up `west.h5` → `westBackup.h5`; manages `seg_logs/` overflow at >30,000 files |
| `get_pcoord.cpptraj` | `runseg.sh` | Calculates MinDist then RMSD for parent + segment frames; `runseg.sh` pastes as [RMSD, MinDist] |

### Binning Strategy (`system.py`)

4-quadrant `RecursiveBinMapper` split at RMSD=10 Å and MinDist=10 Å:

| Quadrant | Condition | Boundaries | Bins |
|----------|-----------|------------|------|
| Quad0 | RMSD 0–10, MinDist >10 | 7 RMSD × 3 MinDist | 21 |
| Quad1 | RMSD >10, MinDist >10 | 3 RMSD × 3 MinDist | 9 |
| **Quad2** | RMSD 0–10, MinDist 0–10 | 96 RMSD × 5 MinDist | **480** |
| Quad3 | RMSD >10, MinDist 0–10 | 3 RMSD × 2 MinDist | 6 |
| **Total** | | | **516** |

Quad0 RMSD boundaries: `[0, 2.5, 5, 6, 7, 8, 9, 10]`; MinDist: `[10, 15, 20, ∞]`
Quad1 RMSD: `[10, 11, 12, ∞]`; MinDist: `[10, 12.5, 15, ∞]`
**Quad2** RMSD: coarse 0–1.5 Å, then 0.05 Å steps 1.5–6.0 Å (81 values), then coarse 6.2–10 Å; MinDist: `[0, 2, 4, 6, 8, 10]`
Quad3 RMSD: `[10, 11, 12, ∞]`; MinDist: `[0, 5, 10]`

- **8 walkers per bin target**
- Phase II (`## PHASE II MAPPERS`) section is present in `system.py` but empty — no alternative mapper blocks defined yet.
- Commented-out Phase I and early alternative boundaries document the iteration history of the binning strategy.

### Data Files
- `west.h5` / `westBackup.h5` / `westBackup-backup.h5` — simulation data and rolling backups
- `bstates/bstates.txt` — 1 basis state: `StructureFiles/struct_0`
- `bstates/StructureFiles/struct_0/` — basis state structure + `pcoordreturn.dat`
- `bins.log` / `newbins.log` / `binviz.log` — bin occupancy snapshots
- `*.png` — bin visualization images (0–7 series documenting binning evolution)

### Molecular System
- **MD topology**: `struct.prmtop` (linked per segment)
- **RMSD reference topology**: `common_files/2KOCFolded_NMR.prmtop`
- **RMSD reference structure**: `common_files/2KOCFolded_NMR.rst7`
- **MD**: NVT, 300 K, Langevin thermostat (γ=1.0 ps⁻¹), 5000 steps × 2 fs = **10 ps per segment**
- **Pcoord length**: 2 frames (parent endpoint + segment endpoint)

### Cluster Details
- **HPC**: Notre Dame CRC (`scratch365`)
- **Scheduler**: SGE (`qsub`)
- **Queue**: `gpu`, 1 GPU card, 8 slots (`-pe smp 8`)
- **Modules**: `westpa/2022.10 mpich cuda/10.2`

## CAUTION: Do Not Traverse
- `seg_logs/` — thousands of per-segment log files; overflow archived automatically by `post_iter.sh`
- `traj_segs/` — raw trajectory data (large); use `traj_seg_example/` for structure reference if present
