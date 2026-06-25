#!/bin/bash
# run_all.sh — generate the full westpa-analyst plot + data set for the CURRENT
# trial directory. Self-contained: the E1-E7 tools live alongside this script,
# and the trial root is discovered at runtime, so it works unchanged in any trial
# and on machines without ~/.claude.
#
# Usage (from anywhere inside the trial tree):
#     source env.sh                       # optional but recommended
#     bash <this_dir>/run_all.sh [west.h5|westBackup.h5]
#
# Outputs land in <trial>/analysis/ (plots) and <trial>/progress_logs/.

set -u
TOOLS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#ITER=$2


# Resolve the trial root: $WEST_SIM_ROOT, else walk up from CWD (then from this
# script's location) to the nearest directory containing west.cfg.
find_root() {
    local d="$1"
    while [ "$d" != "/" ]; do
        [ -f "$d/west.cfg" ] && { echo "$d"; return 0; }
        d="$(dirname "$d")"
    done
    return 1
}
ROOT="${WEST_SIM_ROOT:-}"
if [ -z "$ROOT" ] || [ ! -f "$ROOT/west.cfg" ]; then
    ROOT="$(find_root "$PWD")" || ROOT="$(find_root "$TOOLS")" || ROOT="$PWD"
fi
DATA_ARG="${2:-}"
DATE="$(date +%F)"
mkdir -p "$ROOT/analysis" "$ROOT/progress_logs"
LOG="$ROOT/progress_logs/analyst_tools_${DATE}.log"
: > "$LOG"

run() { echo -e "\n##### $* #####" | tee -a "$LOG"; "$@" 2>&1 | tee -a "$LOG"; }

cd "$ROOT" || exit 1
export WEST_SIM_ROOT="$ROOT"   # so the child python tools resolve the same root

# ---- SAFETY GATE: never read the live west.h5 while a job is running --------
# Ask we_lib (single source of truth for the running check) which file is safe.
RUNNING=$(python3 -c "import sys; sys.path.insert(0,'$TOOLS'); import we_lib; print(1 if we_lib.is_running() else 0)" 2>>"$LOG")
if [ "$RUNNING" = "1" ]; then
    if [ ! -f "$ROOT/westBackup.h5" ]; then
        echo "SAFETY ABORT: simulation appears to be RUNNING and westBackup.h5 is missing — refusing to touch the live west.h5." | tee -a "$LOG"
        exit 2
    fi
    if [ -n "$DATA_ARG" ] && [ "$DATA_ARG" != "westBackup.h5" ]; then
        echo "SAFETY: simulation RUNNING — overriding requested '$DATA_ARG' with westBackup.h5." | tee -a "$LOG"
    fi
    DATA="westBackup.h5"
else
    DATA="${DATA_ARG:-west.h5}"
fi

echo "westpa-analyst tools | $(basename "$ROOT") | data=$DATA | running=$RUNNING | $DATE" | tee -a "$LOG"

# 1. probability distribution + plothist plots. Axis labels come from system.py
#    via we_lib as DIM::LABEL dimspecs; they are comma-free (plothist treats a
#    comma in a dimspec as a bounds separator) and re-derive per trial.
mapfile -t _LBL < <(python3 -c "import sys; sys.path.insert(0,'$TOOLS'); import we_lib as L; [print(s) for s in L.axis_labels(2)]")
LBL0="${_LBL[0]:-pcoord 0}"; LBL1="${_LBL[1]:-pcoord 1}"
# plothist reads a comma in a dimspec as a lb,ub bounds separator -> strip from
# labels (e.g. a multi-range mask like ':1-5,10-14'). Colons are fine.
LBL0="${LBL0//,/ }"; LBL1="${LBL1//,/ }"
# filesystem-safe short name (text before the first '(') for the per-dim plots,
# so output filenames track the actual coordinate in any trial.
slug() { local s="${1%%(*}"; s="$(printf '%s' "$s" | tr -cs 'A-Za-z0-9' '_')"; s="${s#_}"; printf '%s' "${s%_}"; }
NAME0="$(slug "$LBL0")"; NAME1="$(slug "$LBL1")"
run w_pdist -W "$DATA" -o analysis/pdist.h5
run plothist average   analysis/pdist.h5 "0::$LBL0" "1::$LBL1" -o analysis/avg.pdf
run plothist average   analysis/pdist.h5 "0::$LBL0" "1::$LBL1" -o analysis/avg_contour.pdf --plot-contour
run plothist evolution analysis/pdist.h5 "0::$LBL0" -o "analysis/hist_${NAME0}.pdf"
run plothist instant analysis/pdist.h5 "0::$LBL0" -o "analysis/instant_${NAME0}.pdf"
run plothist evolution analysis/pdist.h5 "1::$LBL1" -o "analysis/hist_${NAME1}.pdf"
run plothist instant analysis/pdist.h5 "1::$LBL1" -o "analysis/instant_${NAME1}.pdf"
# average over the LAST completed iteration only. we_lib finds the highest
# propagated iteration in $DATA (skips the unrun trailer WESTPA pre-creates).
ITER=$(python3 -c "import sys; sys.path.insert(0,'$TOOLS'); import we_lib as L; print(L.last_completed_iter('$ROOT/$DATA'))" 2>>"$LOG")
if [ -n "$ITER" ] && [ "$ITER" -gt 0 ] 2>/dev/null; then
    run plothist average analysis/pdist.h5 "0::$LBL0" "1::$LBL1" -o analysis/avg_last.pdf --first-iter "$ITER" --last-iter "$ITER"
else
    echo "skipping avg_last.pdf: could not determine last completed iteration (got '$ITER')" | tee -a "$LOG"
fi

# 2. bin occupancy snapshot (only against west.h5 when the run is NOT live;
#    pass westBackup.h5 as $2 if the simulation is running).
#    NOTE: -W is a GLOBAL flag and must precede the `info` subcommand, and this
#    must NOT go through run() (its output is the file, not tee fodder).
echo -e "\n##### w_bins -W $DATA info > progress_logs/bins.log #####" | tee -a "$LOG"
w_bins -W "$DATA" info --detail --bins-from-system > "$ROOT/progress_logs/bins.log" 2>>"$LOG"
echo "wrote progress_logs/bins.log ($(wc -l < "$ROOT/progress_logs/bins.log") lines)" | tee -a "$LOG"

# 3. the E1-E7 diagnostic tools
run python3 "$TOOLS/we_trends.py"
run python3 "$TOOLS/we_frontier_flux.py"
run python3 "$TOOLS/fes_with_bins.py"
run python3 "$TOOLS/we_kinetics.py"
run python3 "$TOOLS/pdist_plotbins.py"
run python3 "$TOOLS/pdist_gif.py"

echo -e "\nDONE. Plots in analysis/, tool log at $LOG" | tee -a "$LOG"
