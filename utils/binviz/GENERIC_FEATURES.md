# WESTPA Binning Visualizer - Quick Reference

## New Generic Features ✨

The visualizer is now **fully generic** and works with any 2D progress coordinates!

### Automatic Quadrant Detection

The visualizer automatically:
- ✅ Detects outer bin boundaries from your `system.py` file
- ✅ Draws quadrant dividing lines at the correct positions
- ✅ Labels the legend with actual boundary values
- ✅ Works with any outer mapper configuration

**No hardcoded values!** Whether your outer bins are at 5, 10, 20, or any other value, the visualizer will detect and display them correctly.

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

## Examples

### Example 1: Default Generic Labels

```bash
python westpa_visualizer.py system.py -o bins.png
```

**Result:**
- X-axis: "Progress Coordinate 0"
- Y-axis: "Progress Coordinate 1"  
- Quadrant lines: Automatically detected from outer mapper

### Example 2: RMSD/MinDist System

```bash
python westpa_visualizer.py system.py -o bins.png \
    --xlabel "RMSD (Å)" \
    --ylabel "MinDist (Å)"
```

**Result:**
- X-axis: "RMSD (Å)"
- Y-axis: "MinDist (Å)"
- Legend: "Quadrant boundaries (RMSD (Å)=[10.0], MinDist (Å)=[10.0])"

### Example 3: Distance/Angle System

```bash
python westpa_visualizer.py system.py -o bins.png \
    --xlabel "r (Å)" \
    --ylabel "θ (deg)" \
    --title "Polar Coordinate Binning"
```

**Result:**
- Custom title, labels, and automatic boundary detection

### Example 4: Multiple Outer Bins

If your outer mapper has multiple divisions:

```python
# system.py
outer_x = [0.0, 5.0, 10.0, 15.0, float("inf")]
outer_y = [0.0, 3.0, 6.0, float("inf")]
```

The visualizer will draw quadrant lines at:
- X: 5.0, 10.0, 15.0
- Y: 3.0, 6.0

**No manual specification needed!**

## How It Works

### 1. Outer Boundary Detection

When you run the visualizer, it:

```
1. Parses system.py
2. Finds variables like 'rmsd_outer', 'mindist_outer'
3. Stores boundaries: {'x': [0, 10, inf], 'y': [0, 10, inf]}
4. Draws lines at finite boundaries (skips 0 and inf)
```

### 2. Generic Labeling

```python
# In your code or notebook
from westpa_visualizer import BinSchemeParser, BinVisualizer

parser = BinSchemeParser('system.py')
bin_data = parser.parse()

# Option 1: No labels (uses defaults)
viz = BinVisualizer(bin_data)

# Option 2: Custom labels
viz = BinVisualizer(bin_data, pcoord_labels=['Distance', 'Angle'])

viz.generate_bins()
viz.plot(xlabel="Custom X", ylabel="Custom Y")
```

## Supported Outer Boundary Patterns

The visualizer automatically detects outer boundaries named:
- `rmsd_outer`, `mindist_outer` (explicit naming)
- `*_outer` containing `x`, `coord0`, `pcoord0` (for X)
- `*_outer` containing `y`, `coord1`, `pcoord1`, `dist` (for Y)

## What Gets Automatically Detected

From your `system.py`:

```python
# These are automatically found and used
rmsd_outer = [0.0, 10.0, float("inf")]
mindist_outer = [0.0, 10.0, float("inf")]
outer_mapper = RectilinearBinMapper([rmsd_outer, mindist_outer])
self.bin_mapper = RecursiveBinMapper(outer_mapper)
```

**Detected boundaries:**
- X boundaries: [0.0, 10.0, ∞]
- Y boundaries: [0.0, 10.0, ∞]
- Quadrant lines drawn at: X=10, Y=10

## Command-Line Options

```
usage: westpa_visualizer.py system.py [options]

Positional arguments:
  system_file          Path to system.py file

Optional arguments:
  -o, --output FILE    Output file (PNG, PDF, SVG, etc.)
  --figsize W H        Figure size in inches (default: 14 12)
  --no-labels          Hide bin index labels
  --no-grid            Hide grid lines
  --summary            Print text summary
  --title TEXT         Custom plot title
  --xlabel TEXT        Custom x-axis label  ← NEW!
  --ylabel TEXT        Custom y-axis label  ← NEW!
```

## Programmatic Usage

```python
from westpa_visualizer import BinSchemeParser, BinVisualizer

# Parse system file
parser = BinSchemeParser('system.py')
bin_data = parser.parse()

# Create visualizer with custom labels
viz = BinVisualizer(bin_data, pcoord_labels=['RMSD (Å)', 'MinDist (Å)'])

# Generate bins (automatically detects outer boundaries)
viz.generate_bins()

# Check what was detected
print(f"Outer X boundaries: {viz.outer_boundaries['x']}")
print(f"Outer Y boundaries: {viz.outer_boundaries['y']}")

# Plot with customization
viz.plot(
    output_file='bins.png',
    xlabel='Custom X',  # Overrides pcoord_labels
    ylabel='Custom Y',
    title='My Binning Scheme',
    figsize=(16, 14),
    show_labels=True
)
```

## Benefits

### ✅ Portability
Works with any WESTPA system, regardless of:
- Progress coordinate types
- Outer bin boundary values
- Number of quadrants

### ✅ No Manual Configuration
- Quadrant lines are placed automatically
- Legend shows actual boundary values
- No need to edit code for different systems

### ✅ Publication Ready
- Professional labels
- Clear quadrant boundaries
- Customizable for your needs

## Troubleshooting

### Outer boundaries not detected?

Make sure your system.py has:
```python
# Variable names containing 'outer' and coordinate indicators
something_outer = [0.0, 5.0, float("inf")]
```

### Want different quadrant line colors?

Edit `westpa_visualizer.py`:
```python
# Line ~550
ax.axvline(x=x_val, color='#8B0000', ...)  # Change color here
```

### Need more than 2 divisions?

The visualizer supports multiple outer boundaries:
```python
outer = [0, 5, 10, 15, 20, float("inf")]
# Will draw lines at: 5, 10, 15, 20
```

## Version History

**v2.0** - Generic Progress Coordinates
- ✨ Auto-detect outer bin boundaries
- ✨ Custom progress coordinate labels via --xlabel/--ylabel
- ✨ Dynamic quadrant boundary lines
- ✨ Generic axis labels (no RMSD/MinDist hardcoding)

**v1.0** - Initial Release
- Basic 2D visualization
- RMSD/MinDist labeling
- Fixed quadrant lines at 10,10

---

**Need help?** Check the main README.md or USER_GUIDE.md for complete documentation.
