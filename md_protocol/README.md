# MD Protocol

Complete AMBER simulation protocol for RNA/DNA systems — from system parameterization through production and analysis. Copy and customize for new projects; adapt residue masks, force field, box size, and temperature to your system.

Protocol reference: `00_rnaHairpinsProtocol.pdf`

---

## Stage 0 — System Parameterization

**`0_leap.in`** — tLeap template for building a solvated, neutralized RNA/DNA system.

For systems with small molecule ligands, use `antechamber` first to generate GAFF2 parameters:

```bash
# 1. Clean PDB
pdb4amber -i orig.pdb -o new.pdb --reduce --dry

# 2. Generate RESP charges (requires Gaussian)
antechamber -i file.pdb -fi pdb -o file.com -fo gcrt -gv 1 -ge file.gesp -nc <charge>
# run Gaussian → .gesp
antechamber -i file.gesp -fi gesp -o file.mol2 -fo mol2 -c resp -eq 2

# 3. Generate FF parameters
parmchk2 -i file.mol2 -f mol2 -o file.frcmod
```

See `x_OriginalFilesNell/New_Biological_Molecule_DNA_INC_Protocol.pdf` for complete tLeap scripts.

---

## Stage 1 — Minimization & Equilibration (`01_min_eq/`)

| Stage | Duration | Ensemble | Purpose |
|-------|----------|----------|---------|
| min1 | 1000 steps | — | Restrained minimization — relax solvent around fixed solute (500 kcal/mol·Å²) |
| min2 | 2500 steps | — | Unrestrained minimization |
| md1 | 100 ps | NVT | Heat 0 → 300 K with 25 kcal/mol·Å² restraints |
| md2a–e | 250 ps total | NPT | Density equilibration, stepwise restraint release (25→5 kcal/mol·Å²) |
| md3 | 200 ps | NPT | Unrestrained NPT; collect volume for box rescaling (`ntxo=1`) |
| md4 | 1 ns | NVT | Final equilibration with rescaled isotropic box |

GPU variants available for md1–md4 (`*GPU.sh`).

**After md3:** Run `postmd3_calcboxlength.py` to compute the new box length from average NPT volume, then update the restart file before launching md4.

See `min_eq_annotated.txt` for flags explained.

---

## Stage 2 — Production (`02_production/`)

10 sequential 100 ns NVT blocks (`md_final.in` through `md_final_10.in`), each continuing from the previous restart. Launch via `production.sh`.

Settings: NVT 300 K, Langevin thermostat (γ = 1.0 ps⁻¹), SHAKE on H-bonds, `ig=-1`, 2 fs timestep, 50 M steps/block.

See `productionannotated.in` for a fully commented input file.

---

## Stage 3 — Analysis (`03_analysis/`)

| Subdirectory | Contents |
|--------------|---------|
| `claude_cpptraj_pipeline/` | **Primary analysis tool** — 4-stage automated pipeline (cpptraj → process → eRMSD → 2D plots) |
| `cpptraj/` | Project-configured analysis scripts with actual trajectory outputs (CSV, PNG, DAT organized by observable) |
| `get_avg_struct/` | Compute ensemble-average structure and find the closest real trajectory frame |
| `depricated/` | Older analysis notebooks and scripts (barnaba plotting, RMSD variants) |

### Running the pipeline

```bash
cd 03_analysis/claude_cpptraj_pipeline
# Edit full_pipeline.py: TOTAL_NS, topology/trajectory paths, CPPTRAJ_JOBS, METRICS
python full_pipeline.py
# or on cluster: qsub submit_pipeline.sh
```

### Average structure workflow

```bash
cd 03_analysis/get_avg_struct
# Edit .in files: set prmtop and trajin paths
cpptraj -i a_average.in        # compute average coordinates
cpptraj -i b_rmsdfromAvg.in    # RMSD of every frame from average
python c_average.py            # identify frame with minimum RMSD
cpptraj -i d_getClosestAvg.in  # extract that frame as PDB
```

---

## Utilities (`utils/`)

Lightweight cpptraj scripts for common trajectory operations:

| File | Purpose |
|------|---------|
| `makePDB.in` / `makePDB.sh` | Extract PDB frames from a trajectory |
| `strip.in` | Remove water/ions from topology (create stripped prmtop) |
| `cpptraj_process.sh` | Batch cpptraj runner |

---

## Original Protocol Archive (`x_OriginalFilesNell/`)

- `New_Biological_Molecule_DNA_INC_Protocol.pdf` — complete DNA/ligand simulation protocol
- `notesfromnell.txt` — suggestions from collaborator Dr. Nelleri
- `xNew_DNA_RNA_Protocol_Scripts_NellORIGINAL.zip` — original script archive

---

## Notes

- Restraint masks (e.g., `restraintmask=':1'`) must be updated to match your system's residue numbering
- All `.sh` scripts assume AMBER is loaded via `module load amber/24.0`
