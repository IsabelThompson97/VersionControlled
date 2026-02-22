#!/usr/bin/env python3
"""
WESTPA Binning Scheme Visualizer (Standalone)

This tool visualizes binning schemes defined in WESTPA system.py files
by parsing the file and extracting bin boundary definitions directly,
without requiring WESTPA to be installed.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import re
import ast
import argparse
from typing import List, Tuple, Optional, Dict


class BinSchemeParser:
    """Parse binning schemes from system.py files."""
    
    def __init__(self, system_file: str):
        """Initialize parser with system.py file."""
        self.system_file = system_file
        self.bin_data = {
            'outer_mapper': None,
            'nested_mappers': [],
            'pcoord_ndim': 2,
            'target_counts': 8
        }
        
    def parse(self):
        """Parse the system.py file to extract binning information."""
        with open(self.system_file, 'r') as f:
            content = f.read()
        
        # Extract pcoord dimension
        pcoord_match = re.search(r'self\.pcoord_ndim\s*=\s*(\d+)', content)
        if pcoord_match:
            self.bin_data['pcoord_ndim'] = int(pcoord_match.group(1))
        
        # Extract target counts
        target_match = re.search(r'bin_target_counts.*?(\d+)', content)
        if target_match:
            self.bin_data['target_counts'] = int(target_match.group(1))
        
        # Extract bin boundaries
        self._extract_boundaries(content)
        
        # Extract nested mappers
        self._extract_nested_mappers(content)
        
        return self.bin_data
    
    def _extract_boundaries(self, content: str):
        """Extract bin boundaries from variable definitions."""
        boundaries = {}
        
        # Find all lines that define boundary arrays
        # Match: var_name = [...] or var_name = [...] + [...] + [...]
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            
            # Look for variable assignments
            if '=' in line and any(kw in line.lower() for kw in ['rmsd', 'mindist', 'bins', 'spacing', 'quad', 'RMSD', 'MinDist','high','low']):
                # Extract variable name
                match = re.match(r'\s*(\w+)\s*=\s*(.+)', line)
                if not match:
                    continue
                
                var_name = match.group(1)
                expr = match.group(2)
                
                # Continue multiline expressions
                if '[' in expr and ']' not in expr:
                    j = i + 1
                    while j < len(lines) and ']' not in lines[j]:
                        expr += ' ' + lines[j].strip()
                        j += 1
                    if j < len(lines):
                        expr += ' ' + lines[j].strip()
                
                # Evaluate the expression
                try:
                    bounds = self._eval_boundary_expr(expr)
                    if bounds:
                        boundaries[var_name] = bounds
                except Exception as e:
                    pass
        
        self.bin_data['boundaries'] = boundaries
        
    def _eval_boundary_expr(self, expr: str) -> List[float]:
        """Evaluate a boundary expression that may contain additions and list comprehensions."""
        # Remove comments
        if '#' in expr:
            expr = expr[:expr.index('#')]
        
        expr = expr.strip()
        
        # Replace float("inf") with np.inf
        expr = re.sub(r'float\(["\']inf["\']\)', 'np.inf', expr)
        expr = re.sub(r'float\(["\']-inf["\']\)', '-np.inf', expr)
        expr = re.sub(r'float\(["\']infinity["\']\)', 'np.inf', expr)
        
        # Try to evaluate the expression
        try:
            result = eval(expr, {"__builtins__": {}}, {"range": range, "np": np, "float": float})
            
            # Convert to list of floats
            if isinstance(result, (list, tuple)):
                return [float(x) if not isinstance(x, (float, np.floating)) or 
                       (not np.isinf(x)) else (np.inf if x > 0 else -np.inf) for x in result]
            elif isinstance(result, (int, float)):
                return [float(result)]
        except:
            pass
        
        return []
    
    def _eval_boundary_list(self, expr: str) -> List[float]:
        """Safely evaluate a boundary list expression."""
        # Replace common patterns
        expr = expr.replace('float("inf")', 'np.inf')
        expr = expr.replace('float("-inf")', '-np.inf')
        expr = expr.replace('float(\'inf\')', 'np.inf')
        expr = expr.replace('float(\'-inf\')', '-np.inf')
        expr = expr.replace('inf', 'np.inf')
        
        # Handle list comprehensions
        if 'for i in' in expr or 'for i in range' in expr:
            try:
                result = eval(expr, {"__builtins__": {}}, {"range": range, "np": np})
                return result if isinstance(result, list) else [result]
            except:
                return []
        
        # Try to parse as literal
        try:
            # Clean the expression
            expr = expr.strip()
            result = ast.literal_eval(expr)
            if isinstance(result, (int, float)):
                return [float(result)]
            elif isinstance(result, (list, tuple)):
                return [float(x) if x not in [float('inf'), float('-inf')] else x 
                       for x in result]
        except:
            # Try eval with limited namespace
            try:
                result = eval(expr, {"__builtins__": {}}, {"np": np, "range": range})
                if isinstance(result, (list, tuple)):
                    return list(result)
                return [float(result)]
            except:
                pass
        
        return []
    
    def _extract_nested_mappers(self, content: str):
        """Extract information about nested mappers and their boundary variables."""
        # First, map mapper names to their boundary variable names
        mapper_to_bounds = {}
        mapper_pattern = r'(\w+)\s*=\s*RectilinearBinMapper\(\[([^\]]+)\]\)'
        
        for match in re.finditer(mapper_pattern, content):
            mapper_name = match.group(1)
            args_str = match.group(2)
            
            # Parse the arguments (should be two variable names)
            args = [arg.strip() for arg in args_str.split(',')]
            if len(args) >= 2:
                mapper_to_bounds[mapper_name] = {
                    'rmsd_var': args[0],
                    'mindist_var': args[1]
                }
        
        self.bin_data['mapper_to_bounds'] = mapper_to_bounds
        
        # Find RecursiveBinMapper and add_mapper calls
        add_mapper_pattern = r'add_mapper\s*\(\s*(\w+)\s*,\s*\[([\d\.,\s]+)\]\s*\)'
        
        mappers = []
        matches = re.finditer(add_mapper_pattern, content)
        
        for match in matches:
            mapper_name = match.group(1)
            coords_str = match.group(2)
            
            try:
                coords = [float(x.strip()) for x in coords_str.split(',')]
                
                # Get the boundary variables for this mapper
                if mapper_name in mapper_to_bounds:
                    bound_vars = mapper_to_bounds[mapper_name]
                    mappers.append({
                        'mapper_name': mapper_name,
                        'replaces_at': coords,
                        'rmsd_var': bound_vars['rmsd_var'],
                        'mindist_var': bound_vars['mindist_var']
                    })
                else:
                    mappers.append({
                        'mapper_name': mapper_name,
                        'replaces_at': coords
                    })
            except:
                pass
        
        self.bin_data['nested_mappers'] = mappers


class BinVisualizer:
    """Visualize WESTPA binning schemes."""
    
    def __init__(self, bin_data: Dict, pcoord_labels: Optional[List[str]] = None):
        """
        Initialize visualizer with parsed bin data.
        
        Parameters
        ----------
        bin_data : dict
            Parsed binning data from BinSchemeParser
        pcoord_labels : list of str, optional
            Custom labels for progress coordinates [x_label, y_label]
            If None, will attempt to extract from system.py or use defaults
        """
        self.bin_data = bin_data
        self.bins = []
        self.pcoord_labels = pcoord_labels
        self.outer_boundaries = None  # Will store outer mapper boundaries
        
    def generate_bins(self):
        """Generate bin rectangles from parsed data."""
        boundaries = self.bin_data.get('boundaries', {})
        nested_mappers = self.bin_data.get('nested_mappers', [])
        
        print(f"Found {len(boundaries)} boundary definitions")
        print(f"Found {len(nested_mappers)} nested mappers")
        
        # First, find and create outer mapper bins
        outer_rmsd = boundaries.get('rmsd_outer')
        outer_mindist = boundaries.get('mindist_outer')
        
        # Try alternate naming patterns for outer boundaries
        if not outer_rmsd:
            for key in boundaries.keys():
                if 'outer' in key.lower() and any(term in key.lower() for term in ['x', 'rmsd', 'coord0', 'pcoord0']):
                    outer_rmsd = boundaries[key]
                    break
        
        if not outer_mindist:
            for key in boundaries.keys():
                if 'outer' in key.lower() and any(term in key.lower() for term in ['y', 'mindist', 'dist', 'coord1', 'pcoord1']):
                    outer_mindist = boundaries[key]
                    break
        
        if outer_rmsd and outer_mindist:
            print(f"Creating outer bins: X={outer_rmsd}, Y={outer_mindist}")
            # Store the outer boundaries for later use in plotting
            self.outer_boundaries = {
                'x': outer_rmsd,
                'y': outer_mindist
            }
            self._create_rectilinear_bins(outer_rmsd, outer_mindist, level=0)
        else:
            print("Warning: Could not find outer mapper boundaries")
        
        # Now process nested mappers
        for mapper_info in nested_mappers:
            mapper_name = mapper_info['mapper_name']
            coords = mapper_info['replaces_at']
            
            print(f"\nProcessing nested mapper: {mapper_name} at {coords}")
            
            # Get the boundary variable names for this mapper
            rmsd_var = mapper_info.get('rmsd_var')
            mindist_var = mapper_info.get('mindist_var')
            
            if rmsd_var and mindist_var:
                mapper_rmsd = boundaries.get(rmsd_var)
                mapper_mindist = boundaries.get(mindist_var)
                
                print(f"  X variable: {rmsd_var} = {mapper_rmsd}")
                print(f"  Y variable: {mindist_var} = {mapper_mindist}")
                
                if mapper_rmsd and mapper_mindist:
                    # Find parent bin that contains these coordinates
                    parent_bin = self._find_parent_bin(coords)
                    
                    if parent_bin:
                        print(f"  Replacing parent bin at ({parent_bin['x_min']}, {parent_bin['x_max']}) x ({parent_bin['y_min']}, {parent_bin['y_max']})")
                        # Create nested bins
                        self._create_nested_bins(
                            mapper_rmsd, mapper_mindist,
                            parent_bin, level=1
                        )
                    else:
                        print(f"  Warning: No parent bin found for {coords}")
                else:
                    print(f"  Warning: Could not find boundaries for variables {rmsd_var}, {mindist_var}")
            else:
                print(f"  Warning: No boundary variables found for {mapper_name}")
        
        print(f"\nTotal bins created: {len(self.bins)}")
    
    def _create_rectilinear_bins(self, x_bounds: List[float], 
                                  y_bounds: List[float], level: int = 0):
        """Create bins from rectilinear boundaries."""
        for i in range(len(x_bounds) - 1):
            x_min = x_bounds[i]
            x_max = x_bounds[i + 1]
            
            # Handle -inf for min
            if x_min == float('-inf') or x_min == -np.inf:
                x_min = 0 if len([b for b in x_bounds if b not in [float('inf'), float('-inf'), np.inf, -np.inf]]) == 0 else \
                        min(b for b in x_bounds if b not in [float('inf'), float('-inf'), np.inf, -np.inf])
            
            # Keep +inf as is for max
            if x_max == float('inf') or x_max == np.inf:
                x_max = np.inf
            
            for j in range(len(y_bounds) - 1):
                y_min = y_bounds[j]
                y_max = y_bounds[j + 1]
                
                # Handle -inf for min
                if y_min == float('-inf') or y_min == -np.inf:
                    y_min = 0 if len([b for b in y_bounds if b not in [float('inf'), float('-inf'), np.inf, -np.inf]]) == 0 else \
                            min(b for b in y_bounds if b not in [float('inf'), float('-inf'), np.inf, -np.inf])
                
                # Keep +inf as is for max
                if y_max == float('inf') or y_max == np.inf:
                    y_max = np.inf
                
                self.bins.append({
                    'x_min': x_min,
                    'x_max': x_max,
                    'y_min': y_min,
                    'y_max': y_max,
                    'level': level
                })
    
    def _create_nested_bins(self, x_bounds: List[float], y_bounds: List[float],
                           parent_bin: Dict, level: int = 1):
        """Create nested bins within a parent bin."""
        parent_x_min = parent_bin['x_min']
        parent_x_max = parent_bin['x_max']
        parent_y_min = parent_bin['y_min']
        parent_y_max = parent_bin['y_max']
        
        # Remove parent bin from list
        if parent_bin in self.bins:
            self.bins.remove(parent_bin)
        
        # Create nested bins
        for i in range(len(x_bounds) - 1):
            x_min = max(x_bounds[i], parent_x_min)
            x_max = min(x_bounds[i + 1], parent_x_max)
            
            # Handle infinity relative to parent
            if x_bounds[i] == float('-inf') or x_bounds[i] == -np.inf:
                x_min = parent_x_min
            if x_bounds[i + 1] == float('inf') or x_bounds[i + 1] == np.inf:
                x_max = parent_x_max
            
            for j in range(len(y_bounds) - 1):
                y_min = max(y_bounds[j], parent_y_min)
                y_max = min(y_bounds[j + 1], parent_y_max)
                
                # Handle infinity relative to parent
                if y_bounds[j] == float('-inf') or y_bounds[j] == -np.inf:
                    y_min = parent_y_min
                if y_bounds[j + 1] == float('inf') or y_bounds[j + 1] == np.inf:
                    y_max = parent_y_max
                
                self.bins.append({
                    'x_min': x_min,
                    'x_max': x_max,
                    'y_min': y_min,
                    'y_max': y_max,
                    'level': level
                })
    
    def _find_parent_bin(self, coords: List[float]) -> Optional[Dict]:
        """Find the bin containing given coordinates."""
        if len(coords) < 2:
            coords = coords + [0] * (2 - len(coords))
        
        x, y = coords[0], coords[1]
        
        for bin_info in self.bins:
            if bin_info['level'] != 0:
                continue
                
            x_min = bin_info['x_min']
            x_max = bin_info['x_max']
            y_min = bin_info['y_min']
            y_max = bin_info['y_max']
            
            # Handle infinity: if max is infinity, any coordinate >= min is valid
            x_in_range = (x_min <= x < x_max) if x_max != np.inf and not np.isinf(x_max) else (x >= x_min)
            y_in_range = (y_min <= y < y_max) if y_max != np.inf and not np.isinf(y_max) else (y >= y_min)
            
            if x_in_range and y_in_range:
                return bin_info
        
        return None
    
    def plot(self, output_file: Optional[str] = None,
             figsize: Tuple[int, int] = (14, 12),
             show_labels: bool = False,
             show_grid: bool = True,
             title: Optional[str] = None,
             xlabel: Optional[str] = None,
             ylabel: Optional[str] = None):
        """
        Create visualization of the binning scheme.
        
        Parameters
        ----------
        output_file : str, optional
            File path to save the figure
        figsize : tuple, optional
            Figure size (width, height)
        show_labels : bool, optional
            Whether to show bin index labels
        show_grid : bool, optional
            Whether to show grid lines
        title : str, optional
            Custom plot title
        xlabel : str, optional
            Custom x-axis label (overrides auto-detection)
        ylabel : str, optional
            Custom y-axis label (overrides auto-detection)
        """
        if not self.bins:
            self.generate_bins()
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Color schemes for different levels
        level_colors = {
            0: {'face': '#E8F4F8', 'edge': '#000000', 'width': 5.0},  # Outer: black, very thick
            1: {'face': '#B3D9E6', 'edge': '#1E4D66', 'width': 1.2},  # Inner: dark blue, thin
            2: {'face': '#7EB8D4', 'edge': '#0F3A50', 'width': 1.0}
        }
        
        # Sort bins by level (draw outer bins first)
        sorted_bins = sorted(self.bins, key=lambda b: b['level'])
        
        # Find plotting limits - need to handle infinity
        finite_x = []
        finite_y = []
        for bin_info in self.bins:
            if not np.isinf(bin_info['x_min']):
                finite_x.append(bin_info['x_min'])
            if not np.isinf(bin_info['x_max']):
                finite_x.append(bin_info['x_max'])
            if not np.isinf(bin_info['y_min']):
                finite_y.append(bin_info['y_min'])
            if not np.isinf(bin_info['y_max']):
                finite_y.append(bin_info['y_max'])
        
        # Set plot limits: max_finite + 10 for bins extending to infinity
        max_finite_x = max(finite_x) if finite_x else 10
        max_finite_y = max(finite_y) if finite_y else 10
        plot_limit_x = max_finite_x + 5
        plot_limit_y = max_finite_y + 5
        
        # Plot each bin
        for idx, bin_info in enumerate(sorted_bins):
            x_min = bin_info['x_min']
            x_max = bin_info['x_max']
            y_min = bin_info['y_min']
            y_max = bin_info['y_max']
            level = bin_info['level']
            
            # Replace infinity with plot limits for drawing
            if np.isinf(x_max):
                x_max = plot_limit_x
            if np.isinf(y_max):
                y_max = plot_limit_y
            if np.isinf(x_min):
                x_min = 0
            if np.isinf(y_min):
                y_min = 0
            
            width = x_max - x_min
            height = y_max - y_min
            
            # Get color scheme for this level
            color_scheme = level_colors.get(level, level_colors[0])
            
            # Create rectangle
            rect = Rectangle(
                (x_min, y_min), width, height,
                linewidth=color_scheme['width'],
                edgecolor=color_scheme['edge'],
                facecolor=color_scheme['face'],
                alpha=0.5 if level == 0 else 0.7,
                zorder=level + 1 if level == 0 else level
            )
            ax.add_patch(rect)
            
            # Add bin label - only for reasonably sized bins
            if show_labels and width > 0.5 and height > 0.5 and width < (plot_limit_x * 0.3) and height < (plot_limit_y * 0.3):
                center_x = x_min + width / 2
                center_y = y_min + height / 2
                ax.text(
                    center_x, center_y, str(idx),
                    ha='center', va='center',
                    fontsize=8, fontweight='bold',
                    color='#0F3A50',
                    bbox=dict(boxstyle='round,pad=0.3', 
                             facecolor='white', alpha=0.8, edgecolor='none'),
                    zorder=100
                )
        
        # Determine axis labels
        if xlabel is None:
            xlabel = self._get_pcoord_label(0)
        if ylabel is None:
            ylabel = self._get_pcoord_label(1)
        
        # Formatting
        ax.set_xlabel(xlabel, fontsize=13, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=13, fontweight='bold')
        
        if title is None:
            title = f'WESTPA Binning Scheme\n{len(self.bins)} bins total'
        ax.set_title(title, fontsize=15, fontweight='bold', pad=20)
        
        # Set limits with small padding
        ax.set_xlim(-0.5, plot_limit_x + 0.5)
        ax.set_ylim(-0.5, plot_limit_y + 0.5)
        
        # Grid
        if show_grid:
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5, zorder=0)
        
        # Add quadrant dividing lines based on detected outer boundaries
        if self.outer_boundaries:
            x_bounds = self.outer_boundaries['x']
            y_bounds = self.outer_boundaries['y']
            
            # Draw lines at each finite boundary (excluding 0 and inf)
            for x_val in x_bounds[1:-1]:  # Skip first (0) and last (inf)
                if not np.isinf(x_val):
                    ax.axvline(x=x_val, color='#8B0000', linewidth=4, linestyle='-', 
                              zorder=200, alpha=0.8)
            
            for y_val in y_bounds[1:-1]:  # Skip first (0) and last (inf)
                if not np.isinf(y_val):
                    ax.axhline(y=y_val, color='#8B0000', linewidth=4, linestyle='-', 
                              zorder=200, alpha=0.8)
            
            # Create legend label describing the quadrant boundaries
            x_finite = [x for x in x_bounds if not np.isinf(x) and x > 0]
            y_finite = [y for y in y_bounds if not np.isinf(y) and y > 0]
            
            if x_finite and y_finite:
                boundary_label = f'Quadrant boundaries ({xlabel}={x_finite}, {ylabel}={y_finite})'
            else:
                boundary_label = 'Quadrant boundaries'
        else:
            boundary_label = 'Quadrant boundaries'
        
        # Legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='#8B0000', linewidth=4, 
                  label=boundary_label),
            mpatches.Patch(facecolor=level_colors[1]['face'], 
                          edgecolor=level_colors[1]['edge'],
                          linewidth=1.5,
                          label='Nested bins', alpha=0.7)
        ]
        ax.legend(handles=legend_elements, loc='upper right', 
                 fontsize=11, framealpha=0.95)
        
        # Info box
        target = self.bin_data.get('target_counts', 'N/A')
        info_text = f"Total bins: {len(self.bins)}\nWalkers/bin: {target}"
        ax.text(
            0.02, 0.98, info_text,
            transform=ax.transAxes,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='#FFF8DC', 
                     alpha=0.9, edgecolor='#8B7355', linewidth=1.5),
            fontsize=10,
            fontfamily='monospace'
        )
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✓ Saved visualization to: {output_file}")
        
        return fig, ax
    
    
    def _get_pcoord_label(self, index: int) -> str:
        """
        Get the label for a progress coordinate dimension.
        
        Parameters
        ----------
        index : int
            Progress coordinate index (0 or 1)
            
        Returns
        -------
        str
            Label for the progress coordinate
        """
        # Use custom labels if provided
        if self.pcoord_labels and len(self.pcoord_labels) > index:
            return self.pcoord_labels[index]
        
        # Default labels based on common patterns
        default_labels = ['Progress Coordinate 0', 'Progress Coordinate 1']
        return default_labels[index] if index < len(default_labels) else f'pcoord{index}'
    
    def print_summary(self):
        """Print a text summary of the binning scheme."""
        if not self.bins:
            self.generate_bins()
        
        # Get labels
        xlabel = self._get_pcoord_label(0)
        ylabel = self._get_pcoord_label(1)
        
        print("\n" + "="*75)
        print("WESTPA BINNING SCHEME SUMMARY".center(75))
        print("="*75)
        print(f"Progress coordinate dimensions: {self.bin_data['pcoord_ndim']}")
        print(f"Total number of bins: {len(self.bins)}")
        print(f"Target walkers per bin: {self.bin_data.get('target_counts', 'N/A')}")
        print("\nBin definitions:")
        print("-"*75)
        print(f"{'Bin':>5} {'Level':>6} {xlabel + ' Range':>25} {ylabel + ' Range':>25}")
        print("-"*75)
        
        for i, bin_info in enumerate(self.bins):
            x_range = f"[{bin_info['x_min']:6.2f}, {bin_info['x_max']:6.2f})"
            y_range = f"[{bin_info['y_min']:6.2f}, {bin_info['y_max']:6.2f})"
            print(f"{i:5d} {bin_info['level']:6d} {x_range:>25} {y_range:>25}")
        
        print("="*75)
        
        # Level statistics
        level_counts = {}
        for bin_info in self.bins:
            level = bin_info['level']
            level_counts[level] = level_counts.get(level, 0) + 1
        
        print("\nBins by nesting level:")
        for level in sorted(level_counts.keys()):
            print(f"  Level {level}: {level_counts[level]} bins")
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Visualize WESTPA binning schemes from system.py files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s system.py                          # Interactive plot
  %(prog)s system.py -o binning_scheme.png    # Save to PNG
  %(prog)s system.py --summary                # Print text summary
  %(prog)s system.py -o scheme.pdf --no-labels --figsize 10 8
        """
    )
    
    parser.add_argument(
        'system_file',
        help='Path to system.py file'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file (PNG, PDF, SVG, etc.)'
    )
    
    parser.add_argument(
        '--figsize',
        nargs=2,
        type=float,
        default=[14, 12],
        metavar=('WIDTH', 'HEIGHT'),
        help='Figure size in inches (default: 14 12)'
    )
    
    parser.add_argument(
        '--show-labels',
        action='store_true',
        help='Show bin index labels'
    )
    
    parser.add_argument(
        '--no-grid',
        action='store_true',
        help='Hide grid lines'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Print text summary'
    )
    
    parser.add_argument(
        '--title',
        help='Custom plot title'
    )
    
    parser.add_argument(
        '--xlabel',
        help='Custom x-axis label (e.g., "Distance (Å)", "Angle (deg)")'
    )
    
    parser.add_argument(
        '--ylabel',
        help='Custom y-axis label (e.g., "RMSD (Å)", "Dihedral (deg)")'
    )
    
    args = parser.parse_args()
    
    # Parse system file
    print(f"Parsing {args.system_file}...")
    parser = BinSchemeParser(args.system_file)
    bin_data = parser.parse()
    
    # Create visualizer
    pcoord_labels = None
    if args.xlabel or args.ylabel:
        pcoord_labels = [
            args.xlabel if args.xlabel else 'Progress Coordinate 0',
            args.ylabel if args.ylabel else 'Progress Coordinate 1'
        ]
    
    visualizer = BinVisualizer(bin_data, pcoord_labels=pcoord_labels)
    
    # Print summary if requested
    if args.summary:
        visualizer.print_summary()
    
    # Create plot
    visualizer.plot(
        output_file=args.output,
        figsize=tuple(args.figsize),
        show_labels=args.show_labels,
        show_grid=not args.no_grid,
        title=args.title,
        xlabel=args.xlabel,
        ylabel=args.ylabel
    )
    
    if not args.output:
        plt.show()


if __name__ == '__main__':
    main()
