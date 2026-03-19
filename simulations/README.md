# Simulations

Active AMBER MD simulation systems. Equilibration and production protocol templates live in `md_protocol/`; the analysis pipeline lives in `md_protocol/03_analysis/claude_cpptraj_pipeline/`.

---

## Systems

### `1hs3_DEShaw/`
- **Force field:** DE Shaw RNA (`leaprc.RNA.Shaw`)
- **Water model:** TIP4P-D
- **Box:** Truncated octahedron, 12 Å buffer; 0.1 M NaCl
- **Contents:** `system_setup/` — tLeap inputs, solvated PDB, prmtop, rst7, leap logs, visualizations

Parameters: `hairpinsDES_parameters.txt`

### `1hs3_OL3/`
- **Force field:** Amber f99 + bsc0 + χOL3 (`leaprc.RNA.OL3`)
- **Water model:** TIP3P
- **Box/ions:** Same as DEShaw

Directory layout:
```
1hs3_OL3/
├── system_setup/    tLeap inputs, solvated PDB, prmtop, rst7, ResID.txt
├── min_eq/          Minimization & equilibration scripts + postmd3_calcboxlength.py
└── production/      10 × sequential NVT production blocks (md_final.in – md_final_10.in)
```

Parameters: `hairpinsOL3_parameters.txt`

### `2KOC_OL3_HRM/`
- **System:** 14-residue UUCG tetraloop RNA hairpin (PDB: 2KOC)
- **Force field:** Amber f99 + bsc0 + χOL3
- Separate folded and unfolded state setups; each with their own structure files and system preparation

Directory layout:
```
2KOC_OL3_HRM/
├── UUCG_ProjectSummary.pdf
├── folded_structure_files/
├── unfolded_structure_files/
├── folded_x_system_setup/
└── unfolded_system_setup/
```

---

## Equilibration Protocol

Run in order within `min_eq/` (or `md_protocol/01_min_eq/` for the template versions):

| Stage | Duration | Ensemble | Purpose |
|-------|----------|----------|---------|
| min1 | 1000 steps | — | Restrained minimization — relax solvent around fixed solute (500 kcal/mol·Å²) |
| min2 | 2500 steps | — | Unrestrained minimization |
| md1 | 100 ps | NVT | Heat 0 → 300 K with 25 kcal/mol·Å² restraints |
| md2a–e | 250 ps total | NPT | Density equilibration, stepwise restraint release (25→5 kcal/mol·Å²) |
| md3 | 200 ps | NPT | Unrestrained; collect volume for isotropic box rescaling (`ntxo=1`) |
| md4 | 1 ns | NVT | Final equilibration with rescaled box |

After md3: run `postmd3_calcboxlength.py` to compute the new box length from average volume, then update the restart file before launching md4.

---

## Production Runs

```bash
bash production.sh    # runs md_final.in through md_final_10.in sequentially
```

Each `md_final_N.in` continues from the previous restart. NVT 300 K, Langevin thermostat (γ = 1.0 ps⁻¹), SHAKE on H-bonds, `ig=-1`, 2 fs timestep, 50 M steps per block (100 ns).
