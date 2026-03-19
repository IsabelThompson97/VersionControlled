#!/bin/bash
#$ -M ithomps3@nd.edu        # email address for notifications
#$ -m abe                    # email on abort, begin, and end
#$ -pe smp 8                 # 8 CPU threads (barnaba is multi-threaded)
#$ -q gpu                    # queue (same nodes used for production runs)
#$ -l gpu_card=1             # request one GPU card (needed for this queue)
#$ -N uHRM_analysis          # job name shown in qstat
#$ -o pipeline.log           # stdout → this file
#$ -e pipeline.err           # stderr → this file

# ── Environment ───────────────────────────────────────────────────────────────
# Load AMBER (provides cpptraj, called by full_pipeline.py via subprocess)
module load amber/24.0

# Activate the conda environment that has barnaba, numpy, pandas, matplotlib
# (Python 3.12, located at /users/ithomps3/.conda/envs/rna)
source /afs/crc.nd.edu/x86_64_linux/c/conda/24.7.1/etc/profile.d/conda.sh
conda activate rna

# ── Run ───────────────────────────────────────────────────────────────────────
# Change to the analysis directory so all relative paths in the .in files
# and full_pipeline.py resolve correctly
cd /scratch365/ithomps3/rnaHairpins/2KOC_OL3_HRM/unfolded/production_retake/analysis/cpptraj

echo "Job started:  $(date)"
echo "Node:         $(hostname)"
echo "Working dir:  $(pwd)"
echo ""

python3 full_pipeline.py

echo ""
echo "Job finished: $(date)"
