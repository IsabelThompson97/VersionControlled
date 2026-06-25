"""
we_lib.py — shared, trial-agnostic helpers for the westpa-analyst tools.

Everything here reads the CURRENT trial directory at runtime (system.py,
west.cfg, west.log, progress_logs/bins.log, west.h5). Nothing about any
particular trial is hardcoded, so dropping these tools into a new trial
directory "just works" — pcoord labels, bin boundaries, and reference
points are all rediscovered from that trial's own files.

Source of truth precedence:
  - bin boundaries      <- progress_logs/bins.log labels (always match system.py,
                           because bins.log is generated FROM system.py)
  - per-iteration stats <- west.h5 'summary' table + per-iter pcoord/weights
  - pcoord axis labels  <- system.py docstring ("pcoord dimensions:" block),
                           used VERBATIM (name + any unit the author put in
                           parentheses); nothing about the coordinate or its
                           unit is hardcoded here
  - reference points    <- system.py docstring "pcoord references:" block
                           (preferred, dim-indexed; basin names read from the
                           file, e.g. PPII/aL), falling back to the older
                           "*Control Reference*" prose blocks, then to
                           west.cfg analysis_schemes states


REFERENCE-COORD FORMAT (put this in the FIRST / class docstring of system.py,
right under the "pcoord dimensions:" block — NOT in the initialize() docstring):

    pcoord dimensions:
      0: phi ϕ (°)
      1: psi ψ (°)

    pcoord references:
      0: PPII=-75 aL=55
      1: PPII=145 aL=40

The "pcoord dimensions:" block: one line per dim, `<index>: <label>`. The label
is taken VERBATIM as the axis label, so put the unit in parentheses right in the
label (e.g. `(°)`, `(Å)`, `(nm)`). No unit is ever assumed by the tooling.

Rules for the "pcoord references:" block:
  - One line per pcoord dimension, keyed by the SAME integer index used in the
    "pcoord dimensions:" block. This index-based mapping is what makes it work
    when two dims share a measure (e.g. rmsd_stem AND rmsd_loop, or here two
    dihedral angles) — labels are never keyword-matched, so there is no ambiguity.
  - Each line gives the basin reference VALUE for that dim: `<basin>=<value>` for
    EACH basin (whitespace around '=' optional; order on the line free). The basin
    NAMES are read from the file — here `PPII` and `aL`, the two ADP conformers —
    so no particular basin name is hardcoded by the parser.
  - Values are the mean / representative coordinate of each basin along that dim
    (for ADP, the central-alanine phi/psi of the basin, in degrees).
  - A blank line (or the "Notes:" line, or the closing triple-quote) terminates
    the block.
"""

import os
import re
import numpy as np


# --------------------------------------------------------------------------
# Locating the trial and reading files
# --------------------------------------------------------------------------
def sim_root():
    """Trial root, resolved in this order so the tools work no matter where they
    live (~/.claude, analysis/scripts/, an exported copy) or where they are run:
      1. $WEST_SIM_ROOT, if set and a real directory
      2. the nearest ancestor of the CURRENT directory that contains west.cfg
      3. the current directory (last resort)"""
    env = os.environ.get("WEST_SIM_ROOT")
    if env and os.path.isdir(env):
        return env
    d = os.getcwd()
    while True:
        if os.path.exists(os.path.join(d, "west.cfg")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return os.getcwd()
        d = parent


def _read(path):
    try:
        with open(path) as fh:
            return fh.read()
    except OSError:
        return ""


def paths():
    root = sim_root()
    return {
        "root": root,
        "system": os.path.join(root, "system.py"),
        "cfg": os.path.join(root, "west.cfg"),
        "log": os.path.join(root, "west.log"),
        "bins": os.path.join(root, "progress_logs", "bins.log"),
        "h5": os.path.join(root, "west.h5"),
        "h5_backup": os.path.join(root, "westBackup.h5"),
        "analysis": os.path.join(root, "analysis"),
        "progress": os.path.join(root, "progress_logs"),
    }


def _recently_modified(path, minutes=10):
    """True if `path` was modified within the last `minutes` — a running job keeps
    writing west.log. False if the file is missing."""
    import time
    try:
        return (time.time() - os.path.getmtime(path)) < minutes * 60
    except OSError:
        return False


def is_running():
    """Conservatively decide whether the simulation is LIVE. Returns True unless
    we can positively confirm it is not propagating, so analysis defaults to the
    safe (backup) file when in doubt.

      not running  <- west.log ends with 'WEST run complete'
      not running  <- last iteration block completed AND west.log is not fresh
      running      <- last 'Beginning iteration' block has no completion line
      running      <- west.log was modified within the last 10 minutes
    """
    p = paths()
    log = _read(p["log"])
    if not log:
        return False                       # no log -> fresh / idle directory
    tail = log[-3000:]
    if "WEST run complete" in tail:
        return False
    last_block = tail.split("Beginning iteration")[-1]
    incomplete = "Iteration completed successfully" not in last_block
    return incomplete or _recently_modified(p["log"], minutes=10)


def data_file(force=None):
    """Return (path, running) for the HDF5 file analysis should read.

    SAFETY: if the simulation looks live, this returns westBackup.h5 and NEVER the
    live west.h5. If the run is live and no backup exists, it RAISES rather than
    silently reading the file WESTPA is actively writing.

    `force` ('west.h5' | 'westBackup.h5') overrides the choice — use only when you
    are certain (e.g. re-analysing a finished run whose log was hand-edited)."""
    p = paths()
    if force:
        fp = p["h5_backup"] if "backup" in force.lower() else p["h5"]
        return fp, is_running()
    if is_running():
        if os.path.exists(p["h5_backup"]):
            return p["h5_backup"], True
        raise RuntimeError(
            "Simulation appears to be RUNNING but westBackup.h5 is missing — "
            "refusing to read the live west.h5 (it is being written). Wait until "
            "the job is idle, or analyse a backup copy.")
    return p["h5"], False


# --------------------------------------------------------------------------
# pcoord axis labels (from system.py docstring)
# --------------------------------------------------------------------------
def pcoord_labels():
    """{dim_index: 'human label'} parsed from the 'pcoord dimensions:' block.
    Falls back to pcoord_0/pcoord_1 ... if the block is absent."""
    txt = _read(paths()["system"])
    labels = {}
    m = re.search(r"pcoord dimensions:(.*?)(?:\n\s*\n|pcoord references:|Notes:|\"\"\")",
                  txt, re.S | re.I)
    block = m.group(1) if m else ""
    for ln in block.splitlines():
        mm = re.match(r"\s*(\d+)\s*:\s*(.+?)\s*$", ln)
        if mm:
            labels[int(mm.group(1))] = mm.group(2).strip()
    return labels


def axis_labels(ndim):
    """Per-dimension axis labels, taken VERBATIM from the system.py docstring
    'pcoord dimensions:' block.

    The label string is used exactly as the author wrote it — including whatever
    units they put in parentheses — so this tooling makes NO assumption about
    what each coordinate is or what unit it carries. Whatever the docstring says
    is the label. For this trial the block reads

        pcoord dimensions:
          0: phi ϕ (°)
          1: psi ψ (°)

    so the labels are 'phi ϕ (°)' / 'psi ψ (°)'. A distance pcoord would simply
    write e.g. '0: end-to-end distance (Å)' and that whole string becomes the
    label. Falls back to 'pcoord <i>' for any dim the block does not define;
    always returns ndim entries.

    plothist note: a comma inside a DIM::LABEL dimspec is read by plothist as an
    LB,UB bounds separator, so any comma in a label is converted to a space."""
    lab = pcoord_labels()
    return [lab.get(i, f"pcoord {i}").replace(",", " ").strip() for i in range(ndim)]


# --------------------------------------------------------------------------
# Bin boundaries + occupancy (from progress_logs/bins.log)
# --------------------------------------------------------------------------
_LABEL_RE = re.compile(r"\(\s*([-\d.eE+]+)\s*,\s*([-\d.eE+]+)\s*\)")


def parse_bins_log(path=None):
    """Parse bins.log → dict with:
        iteration, total_bins, occupied, pct, dynrange (header values, best-effort)
        edges: list of 1D numpy arrays of bin boundary edges, one per dim
        bins:  list of dicts {index, count, weight, ranges:[(lo,hi),...]}
    Boundaries are reconstructed from the per-bin label ranges, so they always
    match system.py regardless of how the mapper was written."""
    if path is None:
        path = paths()["bins"]
    txt = _read(path)
    header = {"iteration": None, "total_bins": None, "occupied": None,
              "pct": None, "dynrange": None}
    m = re.search(r"iteration\s+(\d+)", txt)
    if m:
        header["iteration"] = int(m.group(1))
    m = re.search(r"(\d+)\s+bins total.*?(\d+)\s+\(([\d.]+)%\)\s+occupied", txt, re.S)
    if m:
        header["total_bins"] = int(m.group(1))
        header["occupied"] = int(m.group(2))
        header["pct"] = float(m.group(3))
    m = re.search(r"Dynamic range \(by bin\):\s+([\d.]+)\s*kT", txt)
    if m:
        header["dynrange"] = float(m.group(1))

    bins = []
    edge_sets = None
    for ln in txt.splitlines():
        mm = re.match(r"\s*(\d+)\s+(\d+)\s+([-\d.eE+]+)", ln)
        if not mm or "[(" not in ln:
            continue
        ranges = [(float(a), float(b)) for a, b in _LABEL_RE.findall(ln)]
        if not ranges:
            continue
        if edge_sets is None:
            edge_sets = [set() for _ in ranges]
        for d, (lo, hi) in enumerate(ranges):
            edge_sets[d].add(round(lo, 6))
            edge_sets[d].add(round(hi, 6))
        bins.append({"index": int(mm.group(1)), "count": int(mm.group(2)),
                     "weight": float(mm.group(3)), "ranges": ranges})
    edges = [np.array(sorted(s)) for s in (edge_sets or [])]
    return {"header": header, "edges": edges, "bins": bins}


def occupied_extent(parsed=None):
    """Per-dimension (min_lo, max_hi) over occupied (count>0) bins."""
    if parsed is None:
        parsed = parse_bins_log()
    occ = [b for b in parsed["bins"] if b["count"] > 0]
    if not occ:
        return []
    ndim = len(occ[0]["ranges"])
    out = []
    for d in range(ndim):
        los = [b["ranges"][d][0] for b in occ]
        his = [b["ranges"][d][1] for b in occ]
        out.append((min(los), max(his)))
    return out


# --------------------------------------------------------------------------
# Reference points (the trial's named basins) for FES annotation
# --------------------------------------------------------------------------
_TOKEN_RE = re.compile(r"[a-z0-9][\w:\-.@]*")
# words too generic to help match a reference title to a specific pcoord dim
_STOP_TOKENS = {"to", "the", "of", "and", "res", "average", "median", "maximum",
                "minimum", "standard", "deviation", "control", "reference",
                "folded", "unfolded", "nmr", "frame"}


def _tokens(text):
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOP_TOKENS]


def reference_points():
    """Return {'points': {<basin>: [d0, d1, ...], ...}, 'source': str}.

    The basin NAMES are whatever the trial defines — they are read from the file,
    never hardcoded. For this ADP trial the basins are 'PPII' and 'aL'; for an
    RNA folding trial they might be 'folded' and 'unfolded'. Any number of basins
    is supported. A coordinate list contains one value per pcoord dimension (or
    None for a dim whose value the source did not supply).

    Source precedence:
      1. system.py docstring 'pcoord references:' block — dim-indexed, with one
         `<basin>=<value>` token per basin on each dim line
         (`0: PPII=-75 aL=55`). PREFERRED: keyed by dim index, so it is
         unambiguous even when two dims share a measure (two dihedrals here, or
         rmsd_stem AND rmsd_loop). See the module docstring for the exact format.
      2. system.py docstring '... Control Reference' prose blocks with
         'Average ...: <number>' lines (legacy RNA-style 'folded'/'unfolded'
         basins), mapped to pcoord dims by scoring word overlap between each
         block title and each dim's label.
      3. west.cfg analysis_schemes states' coords (each state's label becomes a
         basin name)."""
    labels = pcoord_labels()
    ndim = max(labels) + 1 if labels else 2
    txt = _read(paths()["system"])

    # --- 1. preferred: dim-indexed 'pcoord references:' block ----------------
    # Each dim line carries one `<name>=<value>` token per basin; the names are
    # collected from the file so no particular basin label is assumed.
    m = re.search(r"pcoord references:(.*?)(?:\n\s*\n|Notes:|\"\"\")",
                  txt, re.S | re.I)
    if m:
        pts = {}   # basin name -> [val per dim], filled as names are discovered
        for ln in m.group(1).splitlines():
            mm = re.match(r"\s*(\d+)\s*:\s*(.+?)\s*$", ln)
            if not mm:
                continue
            d = int(mm.group(1))
            if not (0 <= d < ndim):
                continue
            for nm, val in re.findall(r"([A-Za-z]\w*)\s*=\s*([-\d.eE+]+)", mm.group(2)):
                pts.setdefault(nm, [None] * ndim)[d] = float(val)
        # keep only basins whose coordinate is fully specified across all dims
        pts = {nm: v for nm, v in pts.items() if None not in v}
        if pts:
            return {"points": pts,
                    "source": "system.py 'pcoord references:' block"}

    # --- 2. fallback: prose 'Control Reference' blocks (legacy RNA style) -----
    def dim_for(title):
        # score each dim's label by shared significant tokens with the title;
        # break ties (and zero-overlap) by the RMSD-vs-Distance measure keyword.
        title_toks = set(_tokens(title))
        title_rmsd = "rmsd" in title.lower()
        best, best_score = None, -1
        for i in range(ndim):
            lab = labels.get(i, "")
            score = len(title_toks & set(_tokens(lab)))
            lab_rmsd = "rmsd" in lab.lower()
            lab_dist = "dist" in lab.lower()
            if (title_rmsd and lab_rmsd) or (not title_rmsd and lab_dist):
                score += 1  # measure-keyword agreement as a tie-breaker
            if score > best_score:
                best, best_score = i, score
        return best if best_score > 0 else None

    pts = {}
    # split the docstring on the dashed header lines that name a reference set
    headers = list(re.finditer(r"-{3,}(.*?Control Reference.*?)-{3,}", txt))
    for i, h in enumerate(headers):
        title = h.group(1)
        seg = txt[h.end(): headers[i + 1].start() if i + 1 < len(headers) else h.end() + 600]
        avg = re.search(r"Average[^\n:]*:\s*([-\d.eE+]+)", seg)
        if not avg:
            continue
        val = float(avg.group(1))
        which = "folded" if "unfold" not in title.lower() else "unfolded"
        d = dim_for(title)
        if d is None:
            continue
        pts.setdefault(which, [None] * ndim)[d] = val

    pts = {nm: v for nm, v in pts.items() if None not in v}
    if pts:
        return {"points": pts,
                "source": "system.py 'Control Reference' blocks"}

    # --- 3. fallback: west.cfg analysis_schemes states ---
    # Each state label becomes a basin name; works for any scheme (PPII/aL here).
    cfg = _read(paths()["cfg"])
    states = {}
    for sm in re.finditer(r"label:\s*(\w+).*?coords:\s*\n\s*-\s*\[([^\]]+)\]", cfg, re.S):
        states[sm.group(1)] = [float(x) for x in sm.group(2).split(",")]
    if states:
        return {"points": states,
                "source": "west.cfg analysis_schemes (approximate)"}
    return {"points": {}, "source": "not found"}


# --------------------------------------------------------------------------
# Per-iteration data from west.h5
# --------------------------------------------------------------------------
def iter_summary(h5path=None):
    """Read the 'summary' table → dict of arrays keyed by iteration (1..N).
    Returns dict with: iters, n_particles, walltime_h, dynrange_kT."""
    import h5py
    if h5path is None:
        h5path, _ = data_file()
    with h5py.File(h5path, "r") as f:
        s = f["summary"][:]
    n = s.shape[0]
    iters = np.arange(1, n + 1)
    npart = s["n_particles"].astype(float)
    wall = s["walltime"].astype(float) / 3600.0
    minb = s["min_bin_prob"].astype(float)
    maxb = s["max_bin_prob"].astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        dyn = np.where((minb > 0) & (maxb > 0), np.log(maxb / minb), np.nan)
    # the last summary row is often the not-yet-run next iteration (npart may be 0)
    keep = npart > 0
    return {"iters": iters[keep], "n_particles": npart[keep],
            "walltime_h": wall[keep], "dynrange_kT": dyn[keep]}


def iter_final_pcoord(n, h5path=None):
    """(pcoord_final[nsegs, ndim], weights[nsegs]) for iteration n."""
    import h5py
    if h5path is None:
        h5path, _ = data_file()
    with h5py.File(h5path, "r") as f:
        g = f["iterations"][f"iter_{n:08d}"]
        pc = g["pcoord"][:, -1, :]
        w = g["seg_index"]["weight"][:]
    return np.asarray(pc), np.asarray(w)


def n_iterations(h5path=None):
    import h5py
    if h5path is None:
        h5path, _ = data_file()
    with h5py.File(h5path, "r") as f:
        return len(f["iterations"])


def last_completed_iter(h5path=None):
    """Highest iteration whose FINAL pcoord is filled (propagated). WESTPA always
    pre-creates the next iteration's group with a zero final pcoord, so the raw
    group count overcounts by one once a run stops. Skip those unrun trailers."""
    import h5py
    if h5path is None:
        h5path, _ = data_file()
    with h5py.File(h5path, "r") as f:
        N = len(f["iterations"])
        for n in range(N, 0, -1):
            pc = f["iterations"][f"iter_{n:08d}"]["pcoord"][:, -1, :]
            if np.any(pc != 0):
                return n
    return 0


def occupied_per_iter(edges, h5path=None):
    """Occupied-bin count per iteration, computed by digitizing each iteration's
    final pcoord into the global edge grid (edges from parse_bins_log)."""
    counts, iters = [], []
    N = last_completed_iter(h5path)
    for n in range(1, N + 1):
        try:
            pc, w = iter_final_pcoord(n, h5path)
        except Exception:
            continue
        cells = set()
        for row in pc:
            key = tuple(int(np.digitize(row[d], edges[d])) for d in range(len(edges)))
            cells.add(key)
        counts.append(len(cells))
        iters.append(n)
    return np.array(iters), np.array(counts)
