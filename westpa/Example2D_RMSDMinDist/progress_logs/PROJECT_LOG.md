# PROJECT LOG — Trial6_FoldingRMSDMinDist_2KOC

WESTPA weighted ensemble MD simulation of 2KOC RNA hairpin folding using a 2D (RMSD, MinDist) progress coordinate with a 4-quadrant recursive bin mapper. Pcoord dimension order is the reverse of Trial5 — here dim 0 = RMSD, dim 1 = MinDist.

---

## Simulation Parameters

| Parameter | Value |
|-----------|-------|
| System | 2KOC RNA hairpin, 14 residues |
| Method | WESTPA weighted ensemble MD |
| Propagator | AMBER pmemd.cuda (GPU) |
| MD ensemble | NVT, 300 K, Langevin (γ=1.0 ps⁻¹) |
| Segment length | 10 ps (5000 steps × 2 fs) |
| pcoord dim 0 | RMSD (Å) — heavy-atom RMSD to NMR folded structure (`:1-14&!@H=`) |
| pcoord dim 1 | MinDist (Å) — minimum distance between :1 and :14 |
| Walkers per bin | 8 |
| Max iterations | 60 |
| Basis state | 1 state (unfolded), high RMSD + high MinDist |
| Target state | folded @ RMSD≈0.5 Å, MinDist≈0.5 Å |
| Plugins | WEED (reweighting disabled), ConstantRatio (disabled) |

---

## Binning Strategy History

### Current (active)
**4-quadrant RecursiveBinMapper** split at RMSD=10 Å, MinDist=10 Å:

- **Quad0** (RMSD 0–10, MinDist >10): `[0,2.5,5,6,7,8,9,10]` × `[10,15,20,∞]` — **21 bins**
- **Quad1** (RMSD >10, MinDist >10): `[10,11,12,∞]` × `[10,12.5,15,∞]` — **9 bins** (unfolded/extended region)
- **Quad2** (RMSD 0–10, MinDist 0–10): 96 RMSD bins × `[0,2,4,6,8,10]` — **480 bins** (folded-approach region)
  - RMSD: 0–1 Å (1 bin), 1–1.5 Å (1 bin), 1.5–6.0 Å (0.05 Å steps, 81 vals), 6.2–10 Å (coarse, 13 vals)
- **Quad3** (RMSD >10, MinDist 0–10): `[10,11,12,∞]` × `[0,5,10]` — **6 bins**
- **Total bins: 516**

Phase I mapper blocks (commented out in `system.py`) used only Quad1 + Quad3 for initial high-RMSD stages; Phase I comments describe rationale (coarser bins at high RMSD, then add finer bins as RMSD decreases).

### Phase II (placeholder — not yet defined)
`## PHASE II MAPPERS` section exists in `system.py` but contains no mapper definitions yet.

---

## Run History

_(add entries as runs complete — job output: `fRMSDMinDist_2KOC.o468381`)_

---

## Progress Log

| Date | Iteration | Notes |
|------|-----------|-------|
| 2026-03-13 | — | Project docs generated; simulation appears in-progress (west.h5 + westBackup.h5 present) |
| 2026-03-13 | 60 | 1496 segs, 187/516 bins (36.24%), DR=76.68 kT (bin), wallclock 5:38:04 — run complete (max 60 iters reached) |
| 2026-03-17 | 63 | 968 segs, 121/277 bins (43.68%), DR=72.65 kT (bin), wallclock 3:37:10 — extended run (max 65); iter 64 in progress |
| _(update here)_ | | |

---

## Bin Occupancy Snapshots

_(run "update the log" after iterations complete — `bins.log`, `newbins.log`, and `binviz.log` are present)_

### Iteration 60 (2026-03-13)
- 1496 segments, 516 bins total, 187 occupied (36.24%)
- Dynamic range: 76.68 kT (bin), 76.77 kT (segment)
- Min seg weight: 5.22e-35, Max seg weight: 0.1146
- Iteration wallclock: 5:38:04
- **Note**: bins.log reflects iteration 61 (post-run resampled state after iter 60 — run ended at max_total_iterations=60). Frontier bins from that resampled state:
  - [(4.65, 4.70), (6.0, 8.0)]: 8 segs, weight 1.56e-27
  - [(4.70, 4.75), (6.0, 8.0)]: 8 segs, weight 8.87e-31
  - [(4.75, 4.80), (4.0, 6.0)]: 8 segs, weight 4.18e-31
  - [(4.75, 4.80), (6.0, 8.0)]: 8 segs, weight 1.67e-30
  - [(4.75, 4.80), (8.0, 10)]: 8 segs, weight 1.33e-30

### Iteration 63 (2026-03-17)
- 968 segments, 277 bins total, 121 occupied (43.68%)
- Dynamic range: 72.65 kT (bin), 72.80 kT (segment)
- Min seg weight: 2.77e-33, Max seg weight: 0.1146
- Iteration wallclock: 3:37:10
- **Note**: bins.log reflects iteration 63 (from westBackup.h5, simulation running on iter 64). Bin count is 277 (down from 516 at iter 60 — system.py updated). Frontier bins:
  - [(4.4, 4.5), (6.0, 8.0)]: 8 segs, weight 2.22e-32  ← RMSD frontier
  - [(4.5, 4.6), (6.0, 8.0)]: 8 segs, weight 8.13e-32
  - [(4.6, 4.7), (4.0, 6.0)]: 8 segs, weight 7.79e-28
  - [(4.6, 4.7), (2.0, 4.0)]: 8 segs, weight 2.67e-30
  - [(4.7, 4.8), (0.0, 2.0)]: 8 segs, weight 1.24e-29  ← MinDist<2 now at RMSD 4.7!

---

## Key Observations

- [ ] Basis state pcoord values verified in `pcoordreturn.dat` (order: RMSD, MinDist)
- [ ] Bin boundaries confirmed in `system.py`
- [ ] `init.sh` run successfully (`west.h5` present)
- [ ] Bin visualization images tracked (`0–7bins*.png`)

---

## Analysis Outputs (`analysis/`)

| File | Description | Generated |
|------|-------------|-----------|
| `pdist.h5` | Probability distribution data (from `westBackup.h5`, iter 63) | 2026-03-17 |
| `analysis/avg.pdf` | 2D average probability distribution (RMSD vs MinDist) | 2026-03-17 |
| `analysis/histRMSD.pdf` | RMSD (dim 0) evolution over iterations | 2026-03-17 |
| `analysis/histMinDist.pdf` | MinDist (dim 1) evolution over iterations | 2026-03-17 |

---

## Decision Points / TODO

- [ ] Monitor frontier progress toward folded state (RMSD→0.5 Å, MinDist→0.5 Å)
- [ ] Define Phase II mapper in `system.py` (currently a placeholder comment block)
- [ ] After 60 iterations, evaluate whether to extend `max_total_iterations`
- [ ] Compare Quad2 sampling efficiency vs Trial5 (which had MinDist as dim 0)
- [ ] Consider enabling WEED reweighting (`do_reweighting: true`) if populations become uneven

---

## File Reference

```
Trial6_FoldingRMSDMinDist_2KOC/
├── west.cfg                        # Master WESTPA config (TEST scheme, 60 iter max)
├── system.py                       # 4-quadrant RecursiveBinMapper (RMSD=dim0, MinDist=dim1)
├── env.sh                          # Environment setup
├── init.sh                         # Simulation initialization
├── run.sh                          # SGE job submission (fRMSDMinDist_2KOC)
├── west.h5                         # Live simulation data
├── westBackup.h5                   # Per-iteration backup
├── west.log                        # Current run log
├── bins.log / newbins.log          # Bin occupancy snapshots
├── binviz.log                      # Bin visualization log
├── *bins*.png                      # Bin visualization images (0–7 series)
├── fRMSDMinDist_2KOC.o468381       # SGE job output log
├── common_files/
│   ├── md.in / md0.in              # AMBER MD input (NVT 300K, 10 ps)
│   ├── 2KOCFolded_NMR.prmtop       # NMR reference topology (for RMSD)
│   ├── 2KOCFolded_NMR.rst7         # NMR reference structure (for RMSD)
│   └── struct.prmtop               # Simulation topology
├── westpa_scripts/
│   ├── runseg.sh                   # Per-segment MD + pcoord extraction
│   ├── get_pcoord.sh               # Basis state pcoord reader
│   ├── post_iter.sh                # Post-iteration backup + log management
│   └── get_pcoord.cpptraj          # MinDist then RMSD calculation; pasted as [RMSD, MinDist]
├── traj_segs/
│   └── 000000                      # Iteration folder
|       └── 0000000                 # Segment folder
│             ├── checkpcoord.dat   # pcoord return
│             ├── pcoord.dat        # cpptraj pcoord0 output
│             ├── pcoord1.dat       # cpptraj pcoord1 output
│             ├── seg.nc            # segment trajectory
│             ├── seg.out           # seg log
│             ├── seg.rst           # segment restart
│             └── struct.prmtop     # structure topology file
├── seg_logs/000000/                # iteration/segment log files
├── bstates/
│   ├── bstates.txt                 # 1 basis state
│   └── StructureFiles/struct_0/    # Basis state structure files
└── analysis/                       # Analysis outputs (w_pdist, plothist)
```

---

*Log initialized: 2026-03-13. Run "update the log" after iterations complete to populate the Progress Log.*
