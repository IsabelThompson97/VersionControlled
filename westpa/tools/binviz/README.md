# WESTPA Binning Scheme Visualizer

A standalone Python tool for visualizing WESTPA (Weighted Ensemble Simulation Toolkit Accelerating) binning schemes from `system.py` files. **Now fully generic** — works with any 2D progress coordinates, automatically detects bin boundaries, and provides customizable axis labeling.

## Features

### Core Capabilities

- ✅ **No WESTPA installation required** - Parses system.py files directly without dependencies
- ✅ **Fully generic 2D binning** - Works with ANY progress coordinate pair (RMSD/MinDist, distances, angles, reaction coordinates, etc.)
- ✅ **Automatic boundary detection** - Intelligently finds and displays outer bin boundaries from your configuration
- ✅ **Customizable labels** - Specify your own axis labels via `--xlabel` and `--ylabel`
- ✅ **Nested bin support** - Handles RecursiveBinMapper with multiple nesting levels
- ✅ **Publication-quality plots** - Professional visualization with automatic quadrant lines
- ✅ **Text summaries** - Generates detailed bin statistics and configuration reports
- ✅ **Multiple output formats** - PNG, PDF, SVG, and more

### New in Version 2.0

- 🆕 **Generic progress coordinates** - No hardcoded RMSD/MinDist assumptions
- 🆕 **Auto-detect quadrant boundaries** - Automatically finds and draws outer bin divisions
- 🆕 **Custom axis labeling** - `--xlabel` and `--ylabel` command-line options
- 🆕 **Dynamic legend generation** - Shows actual boundary values from your system
- 🆕 **Portable across systems** - Same tool works for all 2D WESTPA configurations

## Requirements

```bash
pip install numpy matplotlib
```

**Python 3.6+** recommended.

## Quick Start

### Installation

No installation needed — just download `westpa_visualizer.py` to your working directory.

**Optional:** Add an alias to your `.bashrc` for convenience:

```bash
alias binviz="python3 /path/to/westpa_visualizer.py"
```

Then reload: `source ~/.bashrc`

### Basic Usage

```bash
# Interactive plot with default labels
python westpa_visualizer.py system.py

# Save to file with custom labels
python westpa_visualizer.py system.py -o binning.png \
    --xlabel "RMSD (Å)" --ylabel "MinDist (Å)"

# Print text summary only
python westpa_visualizer.py system.py --summary

# Combined: visualization + summary
python westpa_visualizer.py system.py -o plot.png --summary

# Custom figure size and PDF output
python westpa_visualizer.py system.py -o scheme.pdf --figsize 16 14

# Hide bin labels and grid
python westpa_visualizer.py system.py -o clean.png --no-labels --no-grid

# Custom title
python westpa_visualizer.py system.py -o plot.png --title "My Binning Scheme"

# Combined: summary + visualization
python westpa_visualizer.py system.py --summary -o output.png

```

## Usage Examples

### Example 1: Default Generic Labels

For a quick visualization without specifying coordinate types:

```bash
python westpa_visualizer.py system.py -o bins.png
```

**Output:**
- X-axis: "Progress Coordinate 0"
- Y-axis: "Progress Coordinate 1"
- Quadrant lines automatically detected and drawn
- Legend shows actual boundary values from your system.py

### Example 2: RMSD and MinDist System

The classic protein folding setup:

```bash
python westpa_visualizer.py system.py -o binning.png \
    --xlabel "RMSD (Å)" \
    --ylabel "MinDist (Å)" \
    --summary
```

**Output:**
- Professional labels: "RMSD (Å)" and "MinDist (Å)"
- Quadrant boundaries automatically detected (e.g., at 10.0, 10.0)
- Text summary with bin ranges and statistics

### Example 3: Distance and Angle Coordinates

For ligand binding or conformational analysis:

```bash
python westpa_visualizer.py system.py -o scheme.png \
    --xlabel "Center-of-mass Distance (Å)" \
    --ylabel "Binding Angle (degrees)" \
    --title "Ligand Binding Pathway" \
    --figsize 16 12
```

**Output:**
- Custom title and labels
- Larger figure size for presentations
- Automatic boundary detection works regardless of your specific values

### Example 4: Reaction Coordinates

For chemical reactions or folding pathways:

```bash
python westpa_visualizer.py system.py -o reaction.pdf \
    --xlabel "Reaction Coordinate ξ" \
    --ylabel "SASA (Å²)"
```

**Output:**
- PDF format for publication
- Scientific notation and special characters supported
- Works with any physically meaningful coordinate pair

### Example 5: Multiple Outer Boundaries

If your system has multiple divisions (not just a single quadrant split):

```python
# In your system.py
outer_x = [0.0, 5.0, 10.0, 15.0, float("inf")]
outer_y = [0.0, 3.0, 6.0, 9.0, float("inf")]
```

```bash
python westpa_visualizer.py system.py -o multi_quadrant.png \
    --xlabel "Distance (nm)" --ylabel "Height (nm)"
```

**Output:**
- Quadrant lines drawn at X: 5, 10, 15 and Y: 3, 6, 9
- All finite boundaries automatically detected
- No manual configuration needed

## Command-Line Options

```
usage: westpa_visualizer.py system_file [options]

Positional Arguments:
  system_file              Path to WESTPA system.py file

Output Options:
  -o, --output FILE        Save plot to file (PNG, PDF, SVG, etc.)
                           If not specified, displays interactive plot

Customization Options:
  --xlabel TEXT            Custom label for x-axis (progress coordinate 0)
  --ylabel TEXT            Custom label for y-axis (progress coordinate 1)
  --title TEXT             Custom plot title
  --figsize WIDTH HEIGHT   Figure dimensions in inches (default: 14 12)

Display Options:
  --no-labels              Hide bin index labels
  --no-grid                Hide grid lines
  --summary                Print detailed text summary to console and save as binviz.log

Examples:
  python westpa_visualizer.py system.py
  python westpa_visualizer.py system.py -o plot.png --xlabel "RMSD" --ylabel "Distance"
  python westpa_visualizer.py system.py --summary -o binning.pdf --figsize 16 14
```

## How It Works

### Parsing Strategy

The visualizer uses a custom parser that extracts information from your `system.py` file without requiring WESTPA installation:

1. **Progress coordinate dimensions** - Reads `pcoord_ndim` to confirm 2D system
2. **Bin boundary arrays** - Finds variables containing boundary definitions
3. **Outer bin detection** - Automatically locates variables named `*_outer` or similar patterns
4. **Mapper reconstruction** - Parses RectilinearBinMapper and RecursiveBinMapper definitions
5. **Nested structure** - Tracks `add_mapper()` calls to understand bin hierarchy
6. **Target counts** - Reads `bin_target_counts` for walker distribution

### Automatic Boundary Detection

The tool searches for outer boundary arrays using intelligent pattern matching:

- **Explicit patterns**: `rmsd_outer`, `mindist_outer`, `coord_outer`
- **Generic patterns**: Variables named `*_outer` containing keywords like `x`, `y`, `coord0`, `coord1`, `pcoord0`, `pcoord1`, `dist`
- **Flexible matching**: Works regardless of your variable naming conventions

**Detected boundaries are used to:**
- Draw quadrant dividing lines at appropriate positions
- Label the legend with actual boundary values
- Provide visual reference for nested bin regions

### Visualization Design

**Color Coding:**
- **Light blue** (#E8F4F8): Outer/coarse bins (Level 0)
- **Medium blue** (#B3D9E6): First level nested bins
- **Darker blue**: Deeper nesting levels (if present)

**Quadrant Lines:**
- **Dark red** (#8B0000): Vertical lines for X-coordinate boundaries
- **Dark blue** (#00008B): Horizontal lines for Y-coordinate boundaries
- Automatic placement based on detected outer boundaries
- Only finite values displayed (skips 0.0 and ∞)

**Legend Information:**
- Number of bins at each nesting level
- Total walker count per bin
- Detected quadrant boundary values

## Understanding Your System.py

### Minimal Required Structure

Your `system.py` should follow standard WESTPA format:

```python
from westpa.core.systems import WESTSystem
from westpa.core.binning import RectilinearBinMapper, RecursiveBinMapper
import numpy as np

class System(WESTSystem):
    def initialize(self):
        # Define progress coordinate dimensions
        self.pcoord_ndim = 2
        self.pcoord_len = 2
        
        # Define outer boundaries (these will be auto-detected)
        coord0_outer = [0.0, 10.0, float("inf")]
        coord1_outer = [0.0, 10.0, float("inf")]
        
        # Create outer mapper
        outer_mapper = RectilinearBinMapper([coord0_outer, coord1_outer])
        
        # Initialize recursive mapper
        self.bin_mapper = RecursiveBinMapper(outer_mapper)
        
        # Define fine bins in specific regions
        coord0_fine = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
        coord1_fine = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
        fine_mapper = RectilinearBinMapper([coord0_fine, coord1_fine])
        
        # Add nested bins to quadrant [0-10, 0-10]
        self.bin_mapper.add_mapper(fine_mapper, [5.0, 5.0])
        
        # Set target walker counts
        self.bin_target_counts = np.full((self.bin_mapper.nbins,), 8)
```

### Supported Boundary Definitions

The parser handles various Python expressions for boundaries:

```python
# Simple list
boundaries = [0.0, 5.0, 10.0, float("inf")]

# List comprehension
fine_bins = [0.0, 1.3] + [1.4 + 0.1 * i for i in range(16)] + [3.0, 3.5, 4.0]

# Numpy arrays
import numpy as np
boundaries = np.linspace(0.0, 5.0, 11)

# Mixed definitions
custom = [0.0, 1.8, 2.0] + [2.2 + 0.2 * i for i in range(10)] + [5.0]
```

### Nested Binning Example

```python
# Outer mapper covers entire space
outer_mapper = RectilinearBinMapper([rmsd_outer, mindist_outer])
self.bin_mapper = RecursiveBinMapper(outer_mapper)

# Fine bins in bound state (low RMSD, low MinDist)
bound_fine = RectilinearBinMapper([rmsd_bound_fine, mindist_bound_fine])
self.bin_mapper.add_mapper(bound_fine, [2.5, 2.5])  # Center of quadrant

# Medium bins in unbound state (high RMSD, high MinDist)
unbound_medium = RectilinearBinMapper([rmsd_unbound, mindist_unbound])
self.bin_mapper.add_mapper(unbound_medium, [12.5, 12.5])

# Different resolutions for different quadrants
quadrant2 = RectilinearBinMapper([rmsd_q2, mindist_q2])
self.bin_mapper.add_mapper(quadrant2, [2.5, 12.5])
```

## Example Output

### Visual Output

The tool generates a comprehensive 2D plot showing:
- All bins colored by nesting level
- Quadrant boundary lines (automatically positioned)
- Bin index labels for easy reference
- Grid lines at regular intervals
- Custom axis labels (if specified)
- Professional legend with bin counts and boundary values

### Text Summary

When using `--summary`, you get a detailed statistics log saved as binviz.log:

```
======================================================================
WESTPA BINNING SCHEME ANALYSIS
======================================================================

Parsed arrays: 10
  mindist_highQ0
  ...
  rmsd_lowQ2
  rmsd_outer

Defined mappers: 5
  outer_mapper: [rmsd_outer, mindist_outer]
  mapperQuad0: [rmsd_lowQ0, mindist_highQ0]
  

Active nested mappers: 4
  mapperQuad0 at [5.0, 15.0]
  ...
  mapperQuad3 at [15.0, 5.0]

----------------------------------------------------------------------
BIN GENERATION
----------------------------------------------------------------------

OUTER MAPPER: outer_mapper
  Variables: [rmsd_outer, mindist_outer]
  Dim 0 (rmsd_outer): [0.0, 10.0, inf]
  Dim 1 (mindist_outer): [0.0, 10.0, inf]
  Creates: 4 outer bins

NESTED MAPPER: mapperQuad0
  Replaces bin at: [5.0, 15.0]
  Variables: [rmsd_lowQ0, mindist_highQ0]
  Dim 0 (rmsd_lowQ0): [0.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.5, 9.0, 9.5, 10.0]
  Dim 1 (mindist_highQ0): [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 20.0, inf]
  Creates: 77 bins

======================================================================
TOTAL BINS: 1008
TARGET WALKERS PER BIN: 8
TOTAL WALKERS: 8064
======================================================================

======================================================================
BIN LIST
======================================================================
  Bin			 Dim0        	 Dim1        	 
----------------------------------------------------------------------
    0	 (0.0, 2.0)			 (10.0, 11.0) 
    1	 (0.0, 2.0)			 (11.0, 12.0) 
    2	 (0.0, 2.0)			 (12.0, 13.0) 
    3	 (0.0, 2.0)			 (13.0, 14.0) 
    
```

## Programmatic Usage

For integration into analysis scripts or notebooks:

```python
from westpa_visualizer import BinSchemeParser, BinVisualizer

# Parse system configuration
parser = BinSchemeParser('system.py')
bin_data = parser.parse()

# Create visualizer with custom labels
viz = BinVisualizer(
    bin_data, 
    pcoord_labels=['RMSD (Å)', 'MinDist (Å)']
)

# Generate bin structure (auto-detects outer boundaries)
viz.generate_bins()

# Check what was detected
print(f"Outer X boundaries: {viz.outer_boundaries['x']}")
print(f"Outer Y boundaries: {viz.outer_boundaries['y']}")
print(f"Total bins created: {len(viz.bins)}")

# Create plot with full customization
viz.plot(
    output_file='publication_figure.pdf',
    xlabel='RMSD from Native (Å)',
    ylabel='Minimum Distance to Target (Å)',
    title='Protein Folding Binning Scheme',
    figsize=(16, 14),
    show_labels=True,
    show_grid=True
)

# Get text summary
viz.print_summary()
```

## Troubleshooting

### "No bins created" or "Boundaries not found"

**Problem:** The parser couldn't find boundary definitions in your system.py.

**Solutions:**
1. Ensure boundary arrays are defined **before** they're used in mapper creation:
   ```python
   # ✓ Correct order
   rmsd_outer = [0.0, 5.0, float("inf")]
   mapper = RectilinearBinMapper([rmsd_outer, mindist_outer])
   
   # ✗ Wrong order
   mapper = RectilinearBinMapper([rmsd_outer, mindist_outer])
   rmsd_outer = [0.0, 5.0, float("inf")]  # Too late!
   ```

2. Use recognizable variable names containing keywords like: `outer`, `fine`, `bins`, `boundaries`, `rmsd`, `dist`, `coord`

3. Check that RectilinearBinMapper and RecursiveBinMapper are properly imported

### "Quadrant lines not appearing"

**Problem:** Outer boundary detection failed.

**Solutions:**
1. Ensure outer boundary variables contain `_outer` in their names
2. Use standard patterns: `coord0_outer`, `coord1_outer`, `x_outer`, `y_outer`
3. Check the console output — the tool prints what it detects
4. Verify outer boundaries contain more than just `[0.0, float("inf")]`

### "Wrong axis labels" or "Generic labels when I want specific ones"

**Problem:** You need custom labels but didn't specify them.

**Solution:**
Use `--xlabel` and `--ylabel` flags:
```bash
python westpa_visualizer.py system.py -o plot.png \
    --xlabel "Your X Label" --ylabel "Your Y Label"
```

### Visualization looks different than expected

**Problem:** Bin structure doesn't match your understanding.

**Solutions:**
1. Use `--summary` to see the actual bin boundaries
2. Check your system.py for correct `add_mapper()` calls
3. Verify quadrant centers in `add_mapper()` match your outer boundaries
4. Remember: quadrant centers should be inside the corresponding outer bin

## Supported WESTPA Configurations

### Mappers

- ✅ **RectilinearBinMapper** - Standard rectangular bins
- ✅ **RecursiveBinMapper** - Nested multi-resolution binning
- ⚠️ **Other mapper types** - May have limited support

### Progress Coordinates

- ✅ **2D systems** - Full support with automatic detection
- ⚠️ **1D systems** - Displays warning but attempts visualization
- ⚠️ **3D+ systems** - Displays warning, partial support

### Best Practices

1. **Naming conventions**: Use descriptive variable names (`rmsd_outer`, not `x1`)
2. **Order matters**: Define boundaries before using them in mappers
3. **Comments**: Add comments in system.py for complex setups
4. **Testing**: Verify bin counts match `--summary` output
5. **Quadrant centers**: Choose centers that clearly fall within intended bins

## Performance

- **Small systems** (<100 bins): Instant
- **Medium systems** (100-1000 bins): <1 second
- **Large systems** (>1000 bins): 1-3 seconds
- **Memory usage**: Minimal (<50MB for most systems)

## Limitations and Future Work

### Current Limitations

- Optimized for 2D progress coordinates (1D and 3D+ partially supported)
- Some advanced mapper types not fully supported
- Requires standard WESTPA system.py structure
- Cannot visualize bins created entirely programmatically without file definition

### Planned Features

- 3D bin visualization (isosurface or slice-based)
- Interactive HTML output with bin information on hover
- Comparison mode for multiple system.py files
- Validation against actual WESTPA simulation data
- Direct integration with WESTPA's west.h5 files

## Contributing

Found a bug or have a feature request? This tool is designed to be standalone and portable. If you encounter issues:

**Please provide:**
1. Minimal reproducible system.py example
2. Expected vs. actual output
3. Full error message (if any)
4. Python version and matplotlib version

**Common contributions:**
- Support for additional mapper types
- Enhanced boundary detection patterns
- Additional output formats
- Performance optimizations for large systems

## References and Resources

- [WESTPA Documentation](https://westpa.readthedocs.io/)
- [WESTPA GitHub Repository](https://github.com/westpa/westpa)
- [Binning Guide](https://westpa.readthedocs.io/en/latest/users_guide/west/setup.html#binning)
- [RecursiveBinMapper Tutorial](https://westpa.readthedocs.io/en/latest/tutorials.html)

## Citation

If this tool helps your research, please cite WESTPA:

```
Zwier, M. C.; Adelman, J. L.; Kaus, J. W.; Pratt, A. J.; Wong, K. F.; 
Rego, N. B.; Suárez, E.; Lettieri, S.; Wang, D. W.; Grabe, M.; et al. 
WESTPA: An Interoperable, Highly Scalable Software Package for Weighted 
Ensemble Simulation and Analysis. J. Chem. Theory Comput. 2015, 11, 800–809.
```

## License

This visualization tool is provided as-is for use with WESTPA simulations. Free for academic and commercial use.

## Version History

**v2.0** (Current) - Generic Progress Coordinates
- ✨ Fully generic 2D coordinate support
- ✨ Automatic outer boundary detection
- ✨ Custom axis labels (--xlabel, --ylabel)
- ✨ Dynamic quadrant line placement
- ✨ Improved legend with actual boundary values
- 🔧 Enhanced parser robustness
- 🔧 Better error messages and validation

**v1.0** - Initial Release
- Basic 2D visualization for RMSD/MinDist systems
- RecursiveBinMapper support
- Text summary generation
- Fixed quadrant lines

## Author and Acknowledgments

Created for the WESTPA community to visualize and validate complex binning schemes. Special thanks to users who provided feedback and system.py examples for testing.

---

**Questions or feedback?** See the USER_GUIDE.md for detailed examples and advanced usage patterns.
