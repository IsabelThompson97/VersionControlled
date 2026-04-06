#!/bin/bash
# =============================================================================
# extract_bstate_frames.sh
#
# Extracts 10 random frames from folded and unfolded control MD trajectories,
# strips water and ions, and saves RNA-only PDBs for re-solvation in tleap.
#
# USAGE:
#   Edit the paths below, then run: bash extract_bstate_frames.sh
#
# REQUIRES: cpptraj, python3
# =============================================================================

# ---- EDIT THESE PATHS ----
FOLDED_PRMTOP="../folded/stripped_trajectories/2KOCFolded_HRM_stripped.prmtop"        # folded topology (post-HRM is fine, we just need coords)
FOLDED_TRAJ="../folded/stripped_trajectories/2KOCFolded_HRM_productionStripped.nc"    # folded production trajectory
FOLDED_TOTAL_FRAMES=1000000                                                       # total frames in folded trajectory

UNFOLDED_PRMTOP="../unfolded/production_retake/2KOCUnfolded_HRM_stripped.prmtop"     # unfolded topology
UNFOLDED_TRAJ="../unfolded/production_retake/2KOCUnfolded_HRM_production.nc"         # unfolded production trajectory  
UNFOLDED_TOTAL_FRAMES=1000000                                                       # total frames in unfolded trajectory

# ---- OUTPUT DIRECTORY ----
OUTDIR="bstate_pdbs"
mkdir -p ${OUTDIR}/folded
mkdir -p ${OUTDIR}/unfolded

# ---- RNA RESIDUE MASK ----
# 14 nucleotides, residues 1-14 (adjust if your numbering differs)
RNA_MASK=":1-14"

# =============================================================================
# Generate 10 random frame indices for each trajectory
# Skip the first 20% as equilibration buffer (adjust SKIP_FRAC if needed)
# =============================================================================
SKIP_FRAC=0.2

python3 << EOF
import random
import math

random.seed(42)  # reproducible; change or remove for true randomness

for label, total in [("folded", ${FOLDED_TOTAL_FRAMES}), ("unfolded", ${UNFOLDED_TOTAL_FRAMES})]:
    start = math.ceil(total * ${SKIP_FRAC})
    frames = sorted(random.sample(range(start, total + 1), 10))
    with open("${OUTDIR}/{}_frames.txt".format(label), "w") as f:
        for fr in frames:
            f.write("{}\n".format(fr))
    print(f"{label}: selected frames {frames}")
EOF

# =============================================================================
# Extract and strip FOLDED frames
# =============================================================================
echo ""
echo "=== Extracting folded frames ==="

# Read frame numbers into array
mapfile -t FOLDED_FRAMES < ${OUTDIR}/folded_frames.txt

# Build cpptraj input
CPPTRAJ_IN="${OUTDIR}/extract_folded.cpptraj"
cat > ${CPPTRAJ_IN} << CPPTRAJ_EOF
parm ${FOLDED_PRMTOP}
CPPTRAJ_EOF

for i in "${!FOLDED_FRAMES[@]}"; do
    FRAME=${FOLDED_FRAMES[$i]}
    IDX=$(printf "%02d" $((i+1)))
    cat >> ${CPPTRAJ_IN} << CPPTRAJ_EOF
trajin ${FOLDED_TRAJ} ${FRAME} ${FRAME}
CPPTRAJ_EOF
done

# Strip everything except RNA, write individual PDBs
cat >> ${CPPTRAJ_IN} << CPPTRAJ_EOF
strip !${RNA_MASK}
CPPTRAJ_EOF

for i in "${!FOLDED_FRAMES[@]}"; do
    IDX=$(printf "%02d" $((i+1)))
    FRAME=${FOLDED_FRAMES[$i]}
    # Each trajin loaded one frame, so frame indices in the combined set are 1, 2, ..., 10
    cat >> ${CPPTRAJ_IN} << CPPTRAJ_EOF
outtraj ${OUTDIR}/folded/folded_${IDX}_frame${FRAME}.pdb onlyframes $((i+1)) pdb
CPPTRAJ_EOF
done

cat >> ${CPPTRAJ_IN} << CPPTRAJ_EOF
run
quit
CPPTRAJ_EOF

echo "Running cpptraj for folded frames..."
cpptraj -i ${CPPTRAJ_IN}

# =============================================================================
# Extract and strip UNFOLDED frames
# =============================================================================
echo ""
echo "=== Extracting unfolded frames ==="

mapfile -t UNFOLDED_FRAMES < ${OUTDIR}/unfolded_frames.txt

CPPTRAJ_IN="${OUTDIR}/extract_unfolded.cpptraj"
cat > ${CPPTRAJ_IN} << CPPTRAJ_EOF
parm ${UNFOLDED_PRMTOP}
CPPTRAJ_EOF

for i in "${!UNFOLDED_FRAMES[@]}"; do
    FRAME=${UNFOLDED_FRAMES[$i]}
    cat >> ${CPPTRAJ_IN} << CPPTRAJ_EOF
trajin ${UNFOLDED_TRAJ} ${FRAME} ${FRAME}
CPPTRAJ_EOF
done

cat >> ${CPPTRAJ_IN} << CPPTRAJ_EOF
strip !${RNA_MASK}
CPPTRAJ_EOF

for i in "${!UNFOLDED_FRAMES[@]}"; do
    IDX=$(printf "%02d" $((i+1)))
    FRAME=${UNFOLDED_FRAMES[$i]}
    cat >> ${CPPTRAJ_IN} << CPPTRAJ_EOF
outtraj ${OUTDIR}/unfolded/unfolded_${IDX}_frame${FRAME}.pdb onlyframes $((i+1)) pdb
CPPTRAJ_EOF
done

cat >> ${CPPTRAJ_IN} << CPPTRAJ_EOF
run
quit
CPPTRAJ_EOF

echo "Running cpptraj for unfolded frames..."
cpptraj -i ${CPPTRAJ_IN}

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "=== Done ==="
echo "Folded PDBs:"
ls -1 ${OUTDIR}/folded/
echo ""
echo "Unfolded PDBs:"
ls -1 ${OUTDIR}/unfolded/
echo ""
echo "Next steps:"
echo "  1. Run pdb4amber on each PDB if needed (check for naming issues)"
echo "  2. Test one PDB in tleap to find the correct buffer for your target box size"
echo "  3. Edit leap_bstate.in with the correct buffer value"
echo "  4. Run run_all_tleap.sh"
