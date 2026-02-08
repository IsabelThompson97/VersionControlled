# WESTPA Binning Scheme Visualizer

A standalone Python tool for visualizing WESTPA (Weighted Ensemble Simulation Toolkit Accelerating) binning schemes from `system.py` files.

## Features

- ✅ **No WESTPA installation required** - Parses system.py files directly
- ✅ **2D binning visualization** - Creates clear, publication-quality plots
- ✅ **Nested bin support** - Handles RecursiveBinMapper with multiple levels
- ✅ **Text summaries** - Generates detailed bin statistics
- ✅ **Multiple output formats** - PNG, PDF, SVG, etc.
- ✅ **Customizable** - Adjustable figure size, labels, and styling

## Requirements

```bash
pip install numpy matplotlib
```

## Usage

On CRC with following alias in .bashrc
```bash
alias binviz="python3 /users/ithomps3/VersionControlled/utils/binviz/binning_vizualizer.py"
```
USAGE:
```bash
binviz system.py -o binning.png --xlabel "RMSD (Å)" --ylabel "MinDist (Å)" --summary
```

### Basic Usage

```bash
# Interactive plot
python westpa_visualizer.py system.py

# Save to file
python westpa_visualizer.py system.py -o binning_scheme.png

# Print text summary
python westpa_visualizer.py system.py --summary
```

### Advanced Options

```bash
# Custom figure size and PDF output
python westpa_visualizer.py system.py -o scheme.pdf --figsize 16 14

# Hide bin labels and grid
python westpa_visualizer.py system.py -o clean.png --no-labels --no-grid

# Custom title
python westpa_visualizer.py system.py -o plot.png --title "My Binning Scheme"

# Combined: summary + visualization
python westpa_visualizer.py system.py --summary -o output.png

```

### Custom Progress Coordinate Labels

Use `--xlabel` and `--ylabel` to specify your progress coordinates:

```bash
# Default (generic labels)
python westpa_visualizer.py system.py -o output.png

# Custom labels
python westpa_visualizer.py system.py -o output.png \
    --xlabel "RMSD (Å)" \
    --ylabel "MinDist (Å)"

# Different progress coordinates
python westpa_visualizer.py system.py -o output.png \
    --xlabel "Distance (nm)" \
    --ylabel "Angle (degrees)"

# Anything you want!
python westpa_visualizer.py system.py -o output.png \
    --xlabel "Reaction Coordinate" \
    --ylabel "SASA (Å²)"
```

## How It Works

The visualizer parses your `system.py` file to extract:

1. **Progress coordinate dimensions** (`pcoord_ndim`)
2. **Bin boundary definitions** (arrays like `rmsd_outer`, `mindist_low_fine`)
3. **Mapper definitions** (RectilinearBinMapper instances)
4. **Nested mapper structure** (RecursiveBinMapper.add_mapper calls)
5. **Target walker counts** (`bin_target_counts`)

It then reconstructs the complete binning scheme and creates a visual representation.

## Understanding the Visualization

### Color Coding

- **Light blue** (#E8F4F8): Outer/coarse bins (Level 0)
- **Medium blue** (#B3D9E6): Nested/fine bins (Level 1)
- **Darker blue** (if present): Deeper nesting levels

### Bin Labels

Each bin is labeled with its index number, making it easy to reference specific bins in your simulation setup.

### Legend

The plot includes:
- Number of bins at each nesting level
- Total walker count per bin
- Grid lines for easy coordinate reading

## Example Output

For a typical 2D WESTPA system with RMSD and MinDist progress coordinates:

```
===========================================================================
                       WESTPA BINNING SCHEME SUMMARY                       
===========================================================================
Progress coordinate dimensions: 2
Total number of bins: 445
Target walkers per bin: 8

Bin definitions:
---------------------------------------------------------------------------
  Bin  Level       RMSD Range (Å)         MinDist Range (Å)
---------------------------------------------------------------------------
    0      1     [  0.00,   1.30)          [  0.00,   1.80)
    1      1     [  0.00,   1.30)          [  1.80,   2.00)
  ...
  445      1     [  4.75,   5.00)          [  4.80,   5.00)
===========================================================================

Bins by nesting level:
  Level 0: 0 bins
  Level 1: 445 bins
```

## Supported Binning Features

### RectilinearBinMapper

The tool handles various bin boundary definitions:

```python
# Simple boundaries
rmsd_outer = [0.0, 5.0, float("inf")]

# List comprehensions
rmsd_fine = [0.0, 1.3] + [1.4 + 0.1 * i for i in range(16)] + [3, 3.25, 3.50]

# Mixed definitions
mindist_low = [0.0, 1.8, 2.0, 2.2, 2.4, 2.6, ..., 5.0]
```

### RecursiveBinMapper

Nested bin structures are fully supported:

```python
outer_mapper = RectilinearBinMapper([rmsd_outer, mindist_outer])
self.bin_mapper = RecursiveBinMapper(outer_mapper)

# Fine bins in low RMSD/MinDist region
self.bin_mapper.add_mapper(fine_mapper, [2.5, 2.5])

# Coarse bins in other quadrants
self.bin_mapper.add_mapper(quad1_mapper, [7.5, 7.5])
```

## File Format

Your `system.py` should follow the standard WESTPA format:

```python
from westpa.core.systems import WESTSystem
from westpa.core.binning import RectilinearBinMapper, RecursiveBinMapper

class System(WESTSystem):
    def initialize(self):
        self.pcoord_ndim = 2
        self.pcoord_len = 2
        
        # Define boundaries
        rmsd_bounds = [0.0, 5.0, float("inf")]
        mindist_bounds = [0.0, 5.0, float("inf")]
        
        # Create mappers
        outer_mapper = RectilinearBinMapper([rmsd_bounds, mindist_bounds])
        self.bin_mapper = RecursiveBinMapper(outer_mapper)
        
        # Set target counts
        self.bin_target_counts = np.full((self.bin_mapper.nbins,), 8)
```

## Limitations

- Currently optimized for 2D progress coordinates
- Displays warnings for 1D or >2D systems but still attempts visualization
- Requires boundary variables to be defined before mapper creation
- Some advanced mapper types may not be fully supported

## Troubleshooting

### "No bins created"

Check that your `system.py`:
1. Defines boundary arrays with names containing 'rmsd', 'mindist', or 'bins'
2. Creates RectilinearBinMapper instances
3. Uses `add_mapper()` for nested structures

### "Boundaries not found"

Ensure boundary variables are defined before they're referenced in mapper creation:

```python
# ✓ Good
rmsd_outer = [0.0, 5.0, float("inf")]
mapper = RectilinearBinMapper([rmsd_outer, mindist_outer])

# ✗ Bad - variables undefined
mapper = RectilinearBinMapper([rmsd_outer, mindist_outer])
rmsd_outer = [0.0, 5.0, float("inf")]  # Too late!
```

## Contributing

This tool was designed to work standalone without WESTPA installation. If you encounter parsing issues with your `system.py` file, please provide:

1. A minimal example of your system.py
2. The expected number of bins
3. Any error messages

## References

- [WESTPA Documentation](https://westpa.readthedocs.io/)
- [WESTPA GitHub](https://github.com/westpa/westpa)
- [Binning Guide](https://westpa.readthedocs.io/en/latest/users_guide/west/setup.html#binning)

## License

This visualization tool is provided as-is for use with WESTPA simulations.

## Author

Created for WESTPA users who need to visualize and understand their binning schemes.
