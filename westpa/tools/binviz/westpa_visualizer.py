#!/usr/bin/env python3
"""
WESTPA Binning Visualizer - COMPLETELY AGNOSTIC

Works with ANY WESTPA system.py file:
- Finds ALL RectilinearBinMapper calls
- Uses dimension INDICES (0, 1, 2...) internally
- No assumptions about variable names or types
- Supports both 1D and 2D progress coordinates
- User provides labels if desired
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import re
import argparse
from typing import List, Tuple, Optional, Dict


class AgnosticBinParser:
    """Parse WESTPA bins using only structure, not names."""

    def __init__(self, system_file: str):
        self.system_file = system_file
        self.arrays = {}  # All list variables
        self.mappers = {}  # mapper_name -> [var0, var1, ...]
        self.outer_mapper = None
        self.nested_mappers = []
        self.pcoord_ndim = 2
        self.target_counts = 8

    def parse(self):
        """Parse system.py."""
        with open(self.system_file, 'r') as f:
            content = f.read()

        # Get dimensions
        m = re.search(r'self\.pcoord_ndim\s*=\s*(\d+)', content)
        if m:
            self.pcoord_ndim = int(m.group(1))

        # Get target
        m = re.search(r'bin_target_counts.*?(\d+)', content)
        if m:
            self.target_counts = int(m.group(1))

        # Extract ALL arrays
        self._extract_arrays(content)

        # Extract ALL mappers
        self._extract_mappers(content)

        # Find outer mapper
        self._find_outer_mapper(content)

        # Find nested mappers
        self._find_nested_mappers(content)

        return {
            'pcoord_ndim': self.pcoord_ndim,
            'target_counts': self.target_counts,
            'arrays': self.arrays,
            'mappers': self.mappers,
            'outer_mapper': self.outer_mapper,
            'nested_mappers': self.nested_mappers
        }

    def _extract_arrays(self, content: str):
        """Extract ALL list/array variables."""
        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i]

            # Match: name = [...]
            m = re.match(r'\s*(\w+)\s*=\s*(.+)', line)
            if m and '[' in m.group(2):
                name = m.group(1)
                expr = m.group(2)

                # Handle multi-line
                brackets = expr.count('[') - expr.count(']')
                while brackets > 0 and i + 1 < len(lines):
                    i += 1
                    expr += ' ' + lines[i]
                    brackets = expr.count('[') - expr.count(']')

                # Evaluate
                try:
                    value = self._eval(expr)
                    if isinstance(value, (list, tuple)) and value:
                        self.arrays[name] = [float(v) for v in value]
                except:
                    pass

            i += 1

    def _extract_mappers(self, content: str):
        """Extract ALL RectilinearBinMapper definitions."""
        # Pattern: name = RectilinearBinMapper([...])
        pattern = r'(\w+)\s*=\s*RectilinearBinMapper\s*\(\s*\[([^\]]+)\]\s*\)'

        lines = content.split('\n')
        for line in lines:
            # Skip commented lines
            stripped = line.strip()
            if stripped.startswith('#'):
                continue

            m = re.search(pattern, line)
            if m:
                name = m.group(1)
                args = m.group(2)

                # Get variable names
                vars_list = [v.strip() for v in args.split(',')]
                self.mappers[name] = vars_list

    def _find_outer_mapper(self, content: str):
        """Find RecursiveBinMapper(mapper_name)."""
        m = re.search(r'RecursiveBinMapper\s*\(\s*(\w+)\s*\)', content)
        if m:
            outer_name = m.group(1)
            if outer_name in self.mappers:
                vars_list = self.mappers[outer_name]

                # Get actual arrays
                bounds = []
                for var in vars_list:
                    bounds.append(self.arrays.get(var))

                self.outer_mapper = {
                    'name': outer_name,
                    'vars': vars_list,
                    'bounds': bounds  # Index 0=dim0, 1=dim1, etc.
                }

    def _find_nested_mappers(self, content: str):
        """Find all add_mapper calls - skip commented lines."""
        lines = content.split('\n')

        for line in lines:
            # Skip commented lines
            stripped = line.strip()
            if stripped.startswith('#'):
                continue

            # Look for add_mapper
            m = re.search(r'add_mapper\s*\(\s*(\w+)\s*,\s*\[([^\]]+)\]\s*\)', line)
            if m:
                name = m.group(1)
                coords_str = m.group(2)

                try:
                    coords = [float(x.strip()) for x in coords_str.split(',')]

                    # Get bounds for this mapper
                    vars_list = self.mappers.get(name, [])
                    bounds = [self.arrays.get(v) for v in vars_list]

                    self.nested_mappers.append({
                        'name': name,
                        'coords': coords,
                        'vars': vars_list,
                        'bounds': bounds  # Index 0=dim0, 1=dim1, etc.
                    })
                except:
                    pass

    def _eval(self, expr: str):
        """Evaluate Python expression - handles common variations."""
        # Remove comments
        if '#' in expr:
            expr = expr[:expr.index('#')]

        expr = expr.strip()
        expr = re.sub(r'float\s*\(\s*["\']inf["\']\s*\)', 'float("inf")', expr)

        # Try direct eval first
        try:
            return eval(expr, {'__builtins__': {}, 'range': range, 'float': float, 'np': np, 'int': int})
        except SyntaxError:
            # Common issue: [a, b for i in range(n)] should be [a] + [b for i in range(n)]
            # Try to fix: look for comma before 'for' keyword inside brackets
            # Pattern: [values, expr for ... ] -> [values] + [expr for ...]
            if 'for' in expr and ',' in expr:
                # Simple heuristic fix
                parts = expr.split(',', 1)
                if 'for' in parts[1] and ']' in parts[1]:
                    # Try: [first_part] + [second_part
                    try:
                        fixed = parts[0] + '] + [' + parts[1]
                        return eval(fixed, {'__builtins__': {}, 'range': range, 'float': float, 'np': np, 'int': int})
                    except:
                        pass
            raise


class AgnosticBinVisualizer:
    """Visualize bins using dimension indices only."""

    def __init__(self, data: Dict, dim0_label: str = None, dim1_label: str = None):
        self.data = data
        self.dim0_label = dim0_label
        self.dim1_label = dim1_label
        self.bins = []
        self.outer_bounds = None
        self.ndim = data.get('pcoord_ndim', 2)

    def generate_bins(self):
        """Generate bins from parsed data."""
        outer = self.data.get('outer_mapper')
        nested = self.data.get('nested_mappers', [])

        # Build comprehensive output
        output_lines = []

        output_lines.append("\n" + "="*70)
        output_lines.append("WESTPA BINNING SCHEME ANALYSIS")
        output_lines.append("="*70)
        output_lines.append(f"Progress coordinate dimensions: {self.ndim}")

        # Summary of what was found
        output_lines.append(f"\nParsed arrays: {len(self.data['arrays'])}")
        for name in sorted(self.data['arrays'].keys()):
            output_lines.append(f"  {name}")

        output_lines.append(f"\nDefined mappers: {len(self.data['mappers'])}")
        for name, vars_list in self.data['mappers'].items():
            output_lines.append(f"  {name}: [{', '.join(vars_list)}]")

        output_lines.append(f"\nActive nested mappers: {len(nested)}")
        for nest in nested:
            output_lines.append(f"  {nest['name']} at {nest['coords']}")

        output_lines.append("\n" + "-"*70)
        output_lines.append("BIN GENERATION")
        output_lines.append("-"*70)

        # Create outer bins
        if outer and outer['bounds']:
            if self.ndim == 1:
                dim0_bounds = outer['bounds'][0]

                if dim0_bounds:
                    output_lines.append(f"\nOUTER MAPPER: {outer['name']}")
                    output_lines.append(f"  Variables: [{', '.join(outer['vars'])}]")
                    output_lines.append(f"  Dim 0 ({outer['vars'][0]}): {dim0_bounds}")
                    output_lines.append(f"  Creates: {len(dim0_bounds) - 1} outer bins")

                    self.outer_bounds = (dim0_bounds,)
                    self._create_bins_1d(dim0_bounds, level=0)
            else:
                # 2D path
                dim0_bounds = outer['bounds'][0]
                dim1_bounds = outer['bounds'][1] if len(outer['bounds']) > 1 else None

                if dim0_bounds and dim1_bounds:
                    output_lines.append(f"\nOUTER MAPPER: {outer['name']}")
                    output_lines.append(f"  Variables: [{', '.join(outer['vars'])}]")
                    output_lines.append(f"  Dim 0 ({outer['vars'][0]}): {dim0_bounds}")
                    output_lines.append(f"  Dim 1 ({outer['vars'][1]}): {dim1_bounds}")
                    output_lines.append(f"  Creates: {(len(dim0_bounds)-1) * (len(dim1_bounds)-1)} outer bins")

                    self.outer_bounds = (dim0_bounds, dim1_bounds)
                    self._create_bins(dim0_bounds, dim1_bounds, level=0)

        # Add nested bins
        for nest in nested:
            output_lines.append(f"\nNESTED MAPPER: {nest['name']}")
            output_lines.append(f"  Replaces bin at: {nest['coords']}")

            if nest['vars']:
                output_lines.append(f"  Variables: [{', '.join(nest['vars'])}]")

            if self.ndim == 1:
                if nest['bounds'] and nest['bounds'][0]:
                    dim0_bounds = nest['bounds'][0]
                    output_lines.append(f"  Dim 0 ({nest['vars'][0] if nest['vars'] else 'dim0'}): {dim0_bounds}")
                    output_lines.append(f"  Creates: {len(dim0_bounds) - 1} bins")

                    parent = self._find_parent(nest['coords'])
                    if parent:
                        self._replace_with_nested_1d(parent, dim0_bounds)
                    else:
                        output_lines.append(f"  WARNING: No parent bin found at {nest['coords']}")
                else:
                    output_lines.append(f"  WARNING: Missing boundary array")
            else:
                if nest['bounds'] and len(nest['bounds']) >= 2:
                    dim0_bounds = nest['bounds'][0]
                    dim1_bounds = nest['bounds'][1]

                    if dim0_bounds and dim1_bounds:
                        output_lines.append(f"  Dim 0 ({nest['vars'][0]}): {dim0_bounds}")
                        output_lines.append(f"  Dim 1 ({nest['vars'][1]}): {dim1_bounds}")

                        num_bins = (len(dim0_bounds)-1) * (len(dim1_bounds)-1)
                        output_lines.append(f"  Creates: {num_bins} bins")

                        parent = self._find_parent(nest['coords'])
                        if parent:
                            self._replace_with_nested(parent, dim0_bounds, dim1_bounds)
                        else:
                            output_lines.append(f"  WARNING: No parent bin found at {nest['coords']}")
                    else:
                        output_lines.append(f"  WARNING: Missing boundary arrays")
                else:
                    output_lines.append(f"  WARNING: Mapper not defined or missing boundaries")

        output_lines.append("\n" + "="*70)
        output_lines.append(f"TOTAL BINS: {len(self.bins)}")
        output_lines.append(f"TARGET WALKERS PER BIN: {self.data['target_counts']}")
        output_lines.append(f"TOTAL WALKERS: {len(self.bins) * self.data['target_counts']}")
        output_lines.append("="*70 + "\n")

        # Store output for potential logging
        self.output_text = '\n'.join(output_lines)

        # Print to terminal
        print(self.output_text)

    # ------------------------------------------------------------------
    # Bin creation
    # ------------------------------------------------------------------

    def _create_bins_1d(self, dim0: List, level: int = 0):
        """Create 1D bins from a single boundary list."""
        for i in range(len(dim0) - 1):
            self.bins.append({
                'dim0_min': dim0[i],
                'dim0_max': dim0[i + 1],
                'level': level
            })

    def _create_bins(self, dim0: List, dim1: List, level: int = 0):
        """Create 2D bins from two dimension boundary lists."""
        for i in range(len(dim0) - 1):
            for j in range(len(dim1) - 1):
                self.bins.append({
                    'dim0_min': dim0[i],
                    'dim0_max': dim0[i + 1],
                    'dim1_min': dim1[j],
                    'dim1_max': dim1[j + 1],
                    'level': level
                })

    # ------------------------------------------------------------------
    # Parent finding / nested replacement
    # ------------------------------------------------------------------

    def _find_parent(self, coords: List) -> Optional[Dict]:
        """Find level-0 parent bin containing coordinates (1D or 2D)."""
        if self.ndim == 1:
            if len(coords) < 1:
                return None
            c0 = coords[0]
            for b in self.bins:
                if b['level'] != 0:
                    continue
                d0_ok = (b['dim0_min'] <= c0 < b['dim0_max']) if not np.isinf(b['dim0_max']) else (c0 >= b['dim0_min'])
                if d0_ok:
                    return b
        else:
            if len(coords) < 2:
                return None
            c0, c1 = coords[0], coords[1]
            for b in self.bins:
                if b['level'] != 0:
                    continue
                d0_ok = (b['dim0_min'] <= c0 < b['dim0_max']) if not np.isinf(b['dim0_max']) else (c0 >= b['dim0_min'])
                d1_ok = (b['dim1_min'] <= c1 < b['dim1_max']) if not np.isinf(b['dim1_max']) else (c1 >= b['dim1_min'])
                if d0_ok and d1_ok:
                    return b
        return None

    def _replace_with_nested_1d(self, parent: Dict, dim0: List):
        """Replace a 1D parent bin with nested bins."""
        if parent in self.bins:
            self.bins.remove(parent)

        p0_min, p0_max = parent['dim0_min'], parent['dim0_max']

        for i in range(len(dim0) - 1):
            d0_min = max(dim0[i], p0_min)
            d0_max = dim0[i + 1]

            if not np.isinf(p0_max):
                d0_max = min(d0_max, p0_max)
            elif np.isinf(dim0[i + 1]):
                d0_max = p0_max

            self.bins.append({
                'dim0_min': d0_min,
                'dim0_max': d0_max,
                'level': 1
            })

    def _replace_with_nested(self, parent: Dict, dim0: List, dim1: List):
        """Replace a 2D parent bin with nested bins."""
        if parent in self.bins:
            self.bins.remove(parent)

        p0_min, p0_max = parent['dim0_min'], parent['dim0_max']
        p1_min, p1_max = parent['dim1_min'], parent['dim1_max']

        for i in range(len(dim0) - 1):
            d0_min = max(dim0[i], p0_min)
            d0_max = dim0[i + 1]

            if not np.isinf(p0_max):
                d0_max = min(d0_max, p0_max)
            elif np.isinf(dim0[i + 1]):
                d0_max = p0_max

            for j in range(len(dim1) - 1):
                d1_min = max(dim1[j], p1_min)
                d1_max = dim1[j + 1]

                if not np.isinf(p1_max):
                    d1_max = min(d1_max, p1_max)
                elif np.isinf(dim1[j + 1]):
                    d1_max = p1_max

                self.bins.append({
                    'dim0_min': d0_min,
                    'dim0_max': d0_max,
                    'dim1_min': d1_min,
                    'dim1_max': d1_max,
                    'level': 1
                })

    # ------------------------------------------------------------------
    # Text output
    # ------------------------------------------------------------------

    def print_summary(self, save_file: str = None):
        """Generate text summary - only save to file if requested."""
        if not self.bins:
            self.generate_bins()

        if not save_file:
            return  # Don't print bin list to terminal

        output = []
        output.append("\n" + "="*75)
        output.append("WESTPA BINNING SCHEME SUMMARY".center(75))
        output.append("="*75)
        output.append(f"Progress coordinate dimensions: {self.data['pcoord_ndim']}")
        output.append(f"Total number of bins: {len(self.bins)}")
        output.append(f"Target walkers per bin: {self.data['target_counts']}")
        output.append("\nBin definitions:")
        output.append("-"*75)

        if self.ndim == 1:
            lbl0 = self.dim0_label or 'Dim0'
            output.append(f"{'Bin':>5} {'Level':>6} {lbl0 + ' Range':>30}")
            output.append("-"*75)
            for i, b in enumerate(self.bins):
                d0_range = f"[{b['dim0_min']:8.4f}, {b['dim0_max']:8.4f})"
                output.append(f"{i:5d} {b['level']:6d} {d0_range:>30}")
        else:
            lbl0 = self.dim0_label or 'Dim0'
            lbl1 = self.dim1_label or 'Dim1'
            output.append(f"{'Bin':>5} {'Level':>6} {lbl0 + ' Range':>25} {lbl1 + ' Range':>25}")
            output.append("-"*75)
            for i, b in enumerate(self.bins):
                d0_range = f"[{b['dim0_min']:6.2f}, {b['dim0_max']:6.2f})"
                d1_range = f"[{b['dim1_min']:6.2f}, {b['dim1_max']:6.2f})"
                output.append(f"{i:5d} {b['level']:6d} {d0_range:>25} {d1_range:>25}")

        output.append("="*75 + "\n")

        with open(save_file, 'w') as f:
            f.write('\n'.join(output))
        print(f"✓ Summary saved to: {save_file}")

    def save_log(self, filename: str = 'binviz.log'):
        """Save analysis and bin list to log file."""
        with open(filename, 'w') as f:
            f.write(self.output_text)

            f.write("\n" + "="*70 + "\n")
            f.write("BIN LIST\n")
            f.write("="*70 + "\n")

            if self.ndim == 1:
                f.write(f"{'Bin':>5}\t {'Dim0 Range':30}\n")
                f.write("-"*70 + "\n")
                for idx, b in enumerate(self.bins):
                    f.write(f"{idx:5d}\t ({b['dim0_min']}, {b['dim0_max']})\n")
            else:
                f.write(f"{'Bin':>5}\t\t\t {'Dim0':12}\t {'Dim1':12}\t \n")
                f.write("-"*70 + "\n")
                for idx, b in enumerate(self.bins):
                    f.write(f"{idx:5d}\t ({b['dim0_min']}, {b['dim0_max']})\t\t\t "
                           f"({b['dim1_min']}, {b['dim1_max']}) \n")

            f.write("="*70 + "\n")

        print(f"✓ Saved log to: {filename}")

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------

    def plot(self, output: str = None, figsize: Tuple = (14, 12),
             show_labels: bool = False, grid: bool = True, title: str = None):
        """Plot bins - routes to 1D or 2D based on pcoord_ndim."""
        if not self.bins:
            self.generate_bins()

        if self.ndim == 1:
            return self._plot_1d(output=output, figsize=figsize,
                                 show_labels=show_labels, grid=grid, title=title)
        else:
            return self._plot_2d(output=output, figsize=figsize,
                                 show_labels=show_labels, grid=grid, title=title)

    def _plot_1d(self, output: str = None, figsize: Tuple = (16, 5),
                 show_labels: bool = False, grid: bool = True, title: str = None):
        """Plot 1D bins as a horizontal strip with a density inset."""
        finite_vals = [v for b in self.bins for v in [b['dim0_min'], b['dim0_max']] if not np.isinf(v)]
        max_finite = max(finite_vals) if finite_vals else 10
        plot_max = max_finite * 1.15

        has_inf = any(np.isinf(b['dim0_max']) for b in self.bins)

        fig, (ax_main, ax_dens) = plt.subplots(
            2, 1, figsize=figsize,
            gridspec_kw={'height_ratios': [3, 1]},
            constrained_layout=True
        )

        # --- alternating colors: level-0 outer bins vs level-1 nested ---
        palette = {
            (0, 0): '#B3D9E6',  # outer, even
            (0, 1): '#7EB8D4',  # outer, odd
            (1, 0): '#A8D5A2',  # nested, even
            (1, 1): '#6DBF67',  # nested, odd
        }
        edge_colors = {0: '#1E4D66', 1: '#2A6B24'}

        strip_h = 1.0   # height of the bin strip
        dens_h  = 1.0   # height of the boundary density row

        level1_idx = 0
        for idx, b in enumerate(self.bins):
            x_min = b['dim0_min'] if not np.isinf(b['dim0_min']) else 0.0
            x_max = b['dim0_max'] if not np.isinf(b['dim0_max']) else plot_max

            lvl = b['level']
            parity = (level1_idx if lvl == 1 else idx) % 2
            if lvl == 1:
                level1_idx += 1

            fc = palette.get((lvl, parity), '#B3D9E6')
            ec = edge_colors.get(lvl, '#1E4D66')
            lw = 0.8 if lvl == 1 else 1.0

            rect = Rectangle((x_min, 0), x_max - x_min, strip_h,
                              facecolor=fc, edgecolor=ec,
                              linewidth=lw, alpha=0.85, zorder=2)
            ax_main.add_patch(rect)

            # Bin index label (only if bin is wide enough to be legible)
            if show_labels:
                width_frac = (x_max - x_min) / plot_max
                if width_frac > 0.01:
                    ax_main.text((x_min + x_max) / 2, strip_h / 2, str(idx),
                                 ha='center', va='center', fontsize=7,
                                 fontweight='bold', zorder=5,
                                 bbox=dict(boxstyle='round,pad=0.15',
                                           facecolor='white', alpha=0.7, lw=0))

            # Infinity annotation on last bin
            if np.isinf(b['dim0_max']):
                ax_main.annotate('', xy=(plot_max * 0.99, strip_h / 2),
                                 xytext=(plot_max * 0.93, strip_h / 2),
                                 arrowprops=dict(arrowstyle='->', color='#8B0000',
                                                 lw=2), zorder=10)
                ax_main.text(plot_max * 0.995, strip_h / 2, '∞',
                             va='center', ha='left', fontsize=14,
                             color='#8B0000', fontweight='bold', zorder=10)

        # Outer boundary lines on main strip
        if self.outer_bounds:
            for v in self.outer_bounds[0][1:-1]:
                if not np.isinf(v):
                    ax_main.axvline(v, color='#8B0000', linewidth=3,
                                    alpha=0.9, zorder=10)
                    ax_main.text(v, strip_h + 0.04, f'{v:g}',
                                 ha='center', va='bottom', fontsize=9,
                                 color='#8B0000', fontweight='bold',
                                 transform=ax_main.get_xaxis_transform())

        ax_main.set_xlim(0, plot_max)
        ax_main.set_ylim(-0.05, strip_h + 0.15)
        ax_main.set_yticks([])
        ax_main.set_xlabel(self.dim0_label or 'Progress Coordinate', fontsize=12, fontweight='bold')
        ax_main.set_title(
            title or f'WESTPA 1D Binning Scheme — {len(self.bins)} bins',
            fontsize=14, fontweight='bold', pad=10
        )
        if grid:
            ax_main.grid(True, axis='x', alpha=0.3, linestyle='--', linewidth=0.5, zorder=0)

        # Info box
        ax_main.text(0.01, 0.97,
                     f"Bins: {len(self.bins)}\nWalkers/bin: {self.data['target_counts']}\n"
                     f"Total walkers: {len(self.bins) * self.data['target_counts']}",
                     transform=ax_main.transAxes, va='top', fontsize=9,
                     fontfamily='monospace',
                     bbox=dict(boxstyle='round', facecolor='#FFF8DC', alpha=0.9))

        # Legend
        legend_handles = [
            mpatches.Patch(facecolor=palette[(0, 0)], edgecolor=edge_colors[0],
                           label='Outer bins', alpha=0.85),
            mpatches.Patch(facecolor=palette[(1, 0)], edgecolor=edge_colors[1],
                           label='Nested bins', alpha=0.85),
            Line2D([0], [0], color='#8B0000', linewidth=3,
                   label='Outer boundary'),
        ]
        ax_main.legend(handles=legend_handles, loc='upper right',
                       fontsize=10, framealpha=0.95)

        # --- density row: boundary positions as a rug/tick plot ---
        boundaries = sorted({
            v for b in self.bins
            for v in [b['dim0_min'], b['dim0_max']]
            if not np.isinf(v)
        })
        ax_dens.eventplot(boundaries, orientation='horizontal',
                          lineoffsets=0.5, linelengths=0.8,
                          linewidths=0.6, color='#1E4D66', alpha=0.6)

        if self.outer_bounds:
            outer_boundaries = [v for v in self.outer_bounds[0][1:-1] if not np.isinf(v)]
            if outer_boundaries:
                ax_dens.eventplot(outer_boundaries, orientation='horizontal',
                                  lineoffsets=0.5, linelengths=0.8,
                                  linewidths=2.5, color='#8B0000', alpha=0.9)

        ax_dens.set_xlim(0, plot_max)
        ax_dens.set_ylim(0, 1)
        ax_dens.set_yticks([])
        ax_dens.set_xlabel(self.dim0_label or 'Progress Coordinate', fontsize=10)
        ax_dens.set_title('Bin boundary density', fontsize=9, pad=4)
        if grid:
            ax_dens.grid(True, axis='x', alpha=0.3, linestyle='--', linewidth=0.5)

        if output:
            plt.savefig(output, dpi=300, bbox_inches='tight')
            print(f"\n✓ Saved: {output}")

        return fig, (ax_main, ax_dens)

    def _plot_2d(self, output: str = None, figsize: Tuple = (14, 12),
                 show_labels: bool = False, grid: bool = True, title: str = None):
        """Plot 2D bins as rectangles."""
        fig, ax = plt.subplots(figsize=figsize)

        # Get plot limits
        finite_0 = [v for b in self.bins for v in [b['dim0_min'], b['dim0_max']] if not np.isinf(v)]
        finite_1 = [v for b in self.bins for v in [b['dim1_min'], b['dim1_max']] if not np.isinf(v)]

        max_0 = max(finite_0) if finite_0 else 10
        max_1 = max(finite_1) if finite_1 else 10

        plot_0 = max_0 + 5
        plot_1 = max_1 + 5

        # Colors - uniform for all bins
        color = {'face': '#B3D9E6', 'edge': '#1E4D66', 'width': 1.2, 'alpha': 0.7}

        # Draw bins
        for idx, b in enumerate(self.bins):
            # Handle inf
            d0_min = b['dim0_min'] if not np.isinf(b['dim0_min']) else 0
            d0_max = b['dim0_max'] if not np.isinf(b['dim0_max']) else plot_0
            d1_min = b['dim1_min'] if not np.isinf(b['dim1_min']) else 0
            d1_max = b['dim1_max'] if not np.isinf(b['dim1_max']) else plot_1

            rect = Rectangle(
                (d0_min, d1_min), d0_max - d0_min, d1_max - d1_min,
                linewidth=color['width'], edgecolor=color['edge'],
                facecolor=color['face'], alpha=color['alpha'],
                zorder=2
            )
            ax.add_patch(rect)

            # Optional labels
            if show_labels:
                w, h = d0_max - d0_min, d1_max - d1_min
                if w > 0.5 and h > 0.5 and w < plot_0 * 0.3 and h < plot_1 * 0.3:
                    ax.text(d0_min + w/2, d1_min + h/2, str(idx),
                           ha='center', va='center', fontsize=8, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                           zorder=100)

        # Outer boundary lines
        if self.outer_bounds:
            dim0_bounds, dim1_bounds = self.outer_bounds

            for v in dim0_bounds[1:-1]:
                if not np.isinf(v):
                    ax.axvline(v, color='#8B0000', linewidth=4, alpha=0.8, zorder=200)

            for v in dim1_bounds[1:-1]:
                if not np.isinf(v):
                    ax.axhline(v, color='#8B0000', linewidth=4, alpha=0.8, zorder=200)

        # Labels
        ax.set_xlabel(self.dim0_label or 'Dimension 0', fontsize=13, fontweight='bold')
        ax.set_ylabel(self.dim1_label or 'Dimension 1', fontsize=13, fontweight='bold')
        ax.set_title(title or f'WESTPA Binning Scheme\n{len(self.bins)} bins',
                    fontsize=15, fontweight='bold', pad=20)

        ax.set_xlim(-0.5, plot_0 + 0.5)
        ax.set_ylim(-0.5, plot_1 + 0.5)

        if grid:
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, zorder=0)

        # Legend
        legend = [
            Line2D([0], [0], color='#8B0000', linewidth=4, label='Outer boundaries'),
            mpatches.Patch(facecolor='#B3D9E6', edgecolor='#1E4D66', label='Bins', alpha=0.7)
        ]
        ax.legend(handles=legend, loc='upper right', fontsize=11, framealpha=0.95)

        # Info
        ax.text(0.02, 0.98, f"Bins: {len(self.bins)}\nWalkers/bin: {self.data['target_counts']}",
               transform=ax.transAxes, va='top',
               bbox=dict(boxstyle='round', facecolor='#FFF8DC', alpha=0.9),
               fontsize=10, fontfamily='monospace')

        plt.tight_layout()

        if output:
            plt.savefig(output, dpi=300, bbox_inches='tight')
            print(f"\n✓ Saved: {output}")

        return fig, ax


def main():
    parser = argparse.ArgumentParser(
        description='WESTPA Binning Visualizer - Works with ANY system.py'
    )

    parser.add_argument('system', help='system.py file')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('--log', help='Save analysis and bin list to log file (default: binviz.log)',
                       nargs='?', const='binviz.log', default=None)
    parser.add_argument('--figsize', nargs=2, type=float, default=None,
                       help='Figure size (width height). Defaults: 16 5 for 1D, 14 12 for 2D')
    parser.add_argument('--show-labels', action='store_true', help='Show bin numbers')
    parser.add_argument('--no-grid', action='store_true', help='Hide grid')
    parser.add_argument('--title', help='Custom title')
    parser.add_argument('--xlabel', help='Dimension 0 label')
    parser.add_argument('--ylabel', help='Dimension 1 label (2D only)')

    args = parser.parse_args()

    print(f"Parsing {args.system}...")
    p = AgnosticBinParser(args.system)
    data = p.parse()

    viz = AgnosticBinVisualizer(data, dim0_label=args.xlabel, dim1_label=args.ylabel)

    # Default figsize depends on dimensionality
    if args.figsize:
        figsize = tuple(args.figsize)
    else:
        figsize = (16, 5) if data['pcoord_ndim'] == 1 else (14, 12)

    viz.plot(
        output=args.output,
        figsize=figsize,
        show_labels=args.show_labels,
        grid=not args.no_grid,
        title=args.title
    )

    # Save log if requested
    if args.log:
        viz.save_log(args.log)

    if not args.output:
        plt.show()


if __name__ == '__main__':
    main()
