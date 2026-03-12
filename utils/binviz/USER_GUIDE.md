# WESTPA Binning Visualizer - User Guide

A comprehensive guide to using the WESTPA binning scheme visualizer for any 2D progress coordinate system.

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start Guide](#quick-start-guide)
3. [Generic Progress Coordinate Support](#generic-progress-coordinate-support)
4. [Automatic Boundary Detection](#automatic-boundary-detection)
5. [Common Use Cases](#common-use-cases)
6. [Advanced Usage](#advanced-usage)
7. [Customization Options](#customization-options)
8. [Understanding the Output](#understanding-the-output)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)
11. [API Reference](#api-reference)

---

## Introduction

### What This Tool Does

The WESTPA Binning Visualizer is a **standalone analysis tool** that:

- Parses your WESTPA `system.py` file without requiring a full WESTPA installation
- Automatically detects your binning scheme structure and boundaries
- Creates publication-quality visualizations of your 2D bin layout
- Generates detailed statistical summaries of bin configuration
- Works with **any pair of progress coordinates** — not just RMSD/MinDist

### Why Use This Tool?

**Before running simulations:**
- Validate your binning scheme visually before committing computational resources
- Ensure bins cover the regions of interest
- Check that quadrant assignments are correct
- Verify nested bin placement

**During analysis:**
- Understand which bins are being sampled
- Identify potential issues with bin coverage
- Create figures for presentations and publications
- Document your simulation setup

### Key Philosophy: Generic by Design

Redesigned to be **completely agnostic** to progress coordinate types. Whether you're studying:

- Protein folding (RMSD, radius of gyration, contacts)
- Ligand binding (distances, angles, dihedrals)
- Membrane permeation (Z-position, orientation)
- Chemical reactions (reaction coordinates, bond lengths)
- Conformational transitions (principal components, collective variables)

**The same tool works for all of them.** No hardcoded assumptions, no special cases for RMSD/MinDist.

---

## Quick Start Guide

### Installation

**Step 1:** Ensure you have Python 3.6+ with numpy and matplotlib:

```bash
pip install numpy matplotlib
```

**Step 2:** Download `westpa_visualizer.py` to your analysis directory.

**Step 3 (Optional):** Create an alias for convenience:

```bash
# Add to ~/.bashrc or ~/.bash_profile
alias binviz="python3 /full/path/to/westpa_visualizer.py"

# Reload shell configuration
source ~/.bashrc
```

### Your First Visualization

Navigate to a directory containing a WESTPA `system.py` file:

```bash
# Basic visualization with default labels
python westpa_visualizer.py system.py

# Save to file with custom labels
python westpa_visualizer.py system.py -o binning.png \
    --xlabel "RMSD (Å)" --ylabel "MinDist (Å)"
```

**That's it!** The tool will:
1. Parse your system.py
2. Detect outer bin boundaries automatically
3. Generate all bins according to your RecursiveBinMapper setup
4. Create a color-coded visualization
5. Draw quadrant lines at detected boundaries
6. Display or save the result

---

## Generic Progress Coordinate Support

### Philosophy

**The visualizer makes zero assumptions about what your progress coordinates represent.** It treats them as abstract numerical dimensions (`pcoord[0]` and `pcoord[1]`) and visualizes the binning scheme in that 2D space.

### Default Behavior

Without specifying labels, the tool uses generic identifiers:

```bash
python westpa_visualizer.py system.py -o output.png
```

**Result:**
- X-axis: "Progress Coordinate 0"
- Y-axis: "Progress Coordinate 1"
- Quadrant boundaries: Automatically detected from outer mapper
- Legend: "Quadrant boundaries (Progress Coordinate 0=[...], Progress Coordinate 1=[...])"

This ensures the visualization is always correct regardless of your specific system.

### Custom Labeling

Use `--xlabel` and `--ylabel` to provide semantic meaning:

```bash
python westpa_visualizer.py system.py -o output.png \
    --xlabel "Your X Coordinate Name" \
    --ylabel "Your Y Coordinate Name"
```

**The labels are purely cosmetic** — they don't affect parsing or boundary detection. This means:
- You can label coordinates whatever makes sense for your system
- Labels support special characters, Greek letters, units
- You can use LaTeX-like notation (e.g., "θ", "ξ", "Å", "°")

### Examples Across Different Systems

#### Protein Folding: RMSD and MinDist

```bash
python westpa_visualizer.py system.py -o protein_fold.png \
    --xlabel "RMSD from Native State (Å)" \
    --ylabel "Minimum Distance to Target (Å)"
```

#### Ligand Binding: Distance and Angle

```bash
python westpa_visualizer.py system.py -o ligand_bind.png \
    --xlabel "Center-of-Mass Distance (Å)" \
    --ylabel "Binding Angle θ (degrees)"
```

#### Membrane Permeation: Position and Tilt

```bash
python westpa_visualizer.py system.py -o membrane_perm.png \
    --xlabel "Z Position Relative to Bilayer (Å)" \
    --ylabel "Molecular Tilt Angle (degrees)"
```

#### Chemical Reaction: Bond Lengths

```bash
python westpa_visualizer.py system.py -o reaction.png \
    --xlabel "C-O Bond Length (Å)" \
    --ylabel "N-H Bond Length (Å)"
```

#### Protein Dynamics: Principal Components

```bash
python westpa_visualizer.py system.py -o pca.png \
    --xlabel "Principal Component 1" \
    --ylabel "Principal Component 2"
```

#### Collective Variables: Custom Reaction Coordinates

```bash
python westpa_visualizer.py system.py -o custom_rc.png \
    --xlabel "Reaction Coordinate ξ₁" \
    --ylabel "Reaction Coordinate ξ₂"
```

---

## Automatic Boundary Detection

### How It Works

The visualizer automatically searches your `system.py` for variables defining outer bin boundaries:

**Detection Strategy:**

1. **Name pattern matching:** Looks for variables containing:
   - `_outer` suffix (e.g., `rmsd_outer`, `coord0_outer`)
   - Keywords: `x`, `y`, `coord`, `pcoord`, `dist`, `bins`

2. **Coordinate assignment:** Intelligently assigns to X or Y based on:
   - Position in RectilinearBinMapper argument list
   - Variable name hints (x/coord0/pcoord0 → X axis, y/coord1/pcoord1/dist → Y axis)

3. **Boundary extraction:** Extracts finite boundary values:
   - Includes: Numerical values like `5.0`, `10.0`, `15.0`
   - Excludes: `0.0` (assumed origin) and `float("inf")` (unbounded)

### Supported Patterns

The tool recognizes various naming conventions:

```python
# Explicit X/Y naming
x_outer = [0.0, 10.0, float("inf")]
y_outer = [0.0, 10.0, float("inf")]

# Coordinate numbering
coord0_outer = [0.0, 5.0, 10.0, float("inf")]
coord1_outer = [0.0, 5.0, 10.0, float("inf")]

# Progress coordinate notation
pcoord0_outer = [0.0, 8.0, float("inf")]
pcoord1_outer = [0.0, 8.0, float("inf")]

# Domain-specific naming
rmsd_outer = [0.0, 10.0, float("inf")]
mindist_outer = [0.0, 10.0, float("inf")]

# Generic naming
distance_outer = [0.0, 12.0, float("inf")]
angle_outer = [0.0, 90.0, 180.0, float("inf")]
```

**All of these work automatically!** The tool adapts to your naming convention.

### What Happens With Detected Boundaries

Once boundaries are detected, the visualizer:

1. **Draws quadrant lines:**
   - Vertical red lines at X boundaries (excluding 0 and ∞)
   - Horizontal blue lines at Y boundaries (excluding 0 and ∞)

2. **Updates legend:**
   - Shows actual boundary values from your system
   - Example: "Quadrant boundaries (RMSD=[10.0], MinDist=[10.0])"

3. **Validates nested bins:**
   - Checks that quadrant centers in `add_mapper()` calls fall within appropriate outer bins
   - Warns if centers appear outside expected ranges

### Multiple Outer Boundaries

The tool fully supports systems with more than one division per axis:

```python
# Three divisions on X-axis
rmsd_outer = [0.0, 5.0, 10.0, 15.0, float("inf")]

# Two divisions on Y-axis
mindist_outer = [0.0, 10.0, 20.0, float("inf")]
```

**Visualization:**
- Vertical lines at X = 5.0, 10.0, 15.0
- Horizontal lines at Y = 10.0, 20.0
- Creates a grid with 4 × 2 = 8 outer quadrants

### Manual Override (Programmatic API)

If automatic detection fails, you can specify boundaries manually:

```python
from westpa_visualizer import BinSchemeParser, BinVisualizer

parser = BinSchemeParser('system.py')
bin_data = parser.parse()

viz = BinVisualizer(bin_data)
viz.generate_bins()

# Manually set boundaries
viz.outer_boundaries = {
    'x': [0.0, 5.0, 10.0, float('inf')],
    'y': [0.0, 8.0, 16.0, float('inf')]
}

viz.plot(output_file='manual_bounds.png')
```

---

## Common Use Cases

### Use Case 1: Validating a New Binning Scheme

**Scenario:** You've designed a complex nested binning scheme and want to verify it before running expensive simulations.

**Workflow:**

```bash
# Step 1: Create visualization with summary
python westpa_visualizer.py system.py --summary -o validation.png \
    --xlabel "RMSD (Å)" --ylabel "MinDist (Å)"

# Step 2: Check the output
# - Do bins cover the regions you care about?
# - Are quadrant boundaries correct?
# - Is the resolution appropriate for each region?
# - Does the total bin count match expectations?
```

**What to look for:**
- Fine bins in regions of interest (e.g., bound state)
- Coarser bins in less interesting regions (e.g., unbound state)
- No gaps or overlaps in coverage
- Reasonable total number of bins for your computational budget

### Use Case 2: Documenting Your Simulation Setup

**Scenario:** Writing a paper or grant proposal and need a clear figure showing your binning scheme.

**Workflow:**

```bash
# Create publication-quality figure
python westpa_visualizer.py system.py -o Figure_S1_binning.pdf \
    --xlabel "RMSD from Native Structure (Å)" \
    --ylabel "Minimum Distance to Binding Site (Å)" \
    --title "Hierarchical Binning Scheme for Protein-Ligand Association" \
    --figsize 16 14 \
    --no-grid
```

**Tips:**
- Use PDF format for scalable vector graphics
- Larger figure size (16×14 or bigger) for clarity
- Consider `--no-grid` for cleaner appearance
- Keep `--no-labels` off so readers can reference specific bins

### Use Case 3: Comparing Different Binning Strategies

**Scenario:** You're testing different bin resolutions and want to compare them visually.

**Workflow:**

```bash
# Strategy A: Uniform fine bins everywhere
python westpa_visualizer.py system_uniform.py -o strategy_A.png \
    --xlabel "RMSD (Å)" --ylabel "MinDist (Å)" \
    --title "Strategy A: Uniform Fine Resolution"

# Strategy B: Adaptive resolution (fine where it matters)
python westpa_visualizer.py system_adaptive.py -o strategy_B.png \
    --xlabel "RMSD (Å)" --ylabel "MinDist (Å)" \
    --title "Strategy B: Adaptive Resolution"

# Strategy C: Very coarse for initial exploration
python westpa_visualizer.py system_coarse.py -o strategy_C.png \
    --xlabel "RMSD (Å)" --ylabel "MinDist (Å)" \
    --title "Strategy C: Coarse Exploration"
```

**Compare:**
- Total number of bins (from `--summary`)
- Coverage of important regions
- Computational cost estimates (bins × walkers × iterations)

### Use Case 4: Non-Standard Progress Coordinates

**Scenario:** Using unconventional progress coordinates like principal components or custom collective variables.

**Workflow:**

```bash
# Example: First two principal components from PCA
python westpa_visualizer.py system.py -o pca_binning.png \
    --xlabel "PC1 (Å)" \
    --ylabel "PC2 (Å)" \
    --title "PCA-based Progress Coordinates"

# Example: Reaction coordinates from string method
python westpa_visualizer.py system.py -o reaction_coords.png \
    --xlabel "ξ₁ (transition coordinate)" \
    --ylabel "ξ₂ (orthogonal coordinate)"
```

**Advantage:** The tool doesn't care what your coordinates represent — it just visualizes the binning structure in that 2D space.

### Use Case 5: Integration with Analysis Scripts

**Scenario:** Automating visualization as part of your analysis pipeline.

**Workflow:**

```python
#!/usr/bin/env python
"""
Automated binning scheme analysis and visualization
"""
from westpa_visualizer import BinSchemeParser, BinVisualizer
import sys

def analyze_binning(system_file):
    # Parse system
    parser = BinSchemeParser(system_file)
    bin_data = parser.parse()
    
    # Create visualizer
    viz = BinVisualizer(bin_data, pcoord_labels=['RMSD (Å)', 'MinDist (Å)'])
    viz.generate_bins()
    
    # Check for issues
    total_bins = len(viz.bins)
    print(f"Total bins: {total_bins}")
    
    if total_bins > 1000:
        print("WARNING: Very large number of bins may be computationally expensive")
    
    if total_bins < 20:
        print("WARNING: Very few bins may provide insufficient resolution")
    
    # Generate output
    viz.plot(
        output_file='auto_binning.png',
        title=f'Binning Scheme Analysis ({total_bins} bins)',
        figsize=(14, 12)
    )
    viz.print_summary()
    
    return total_bins

if __name__ == '__main__':
    analyze_binning(sys.argv[1])
```

### Use Case 6: Troubleshooting Simulation Issues

**Scenario:** Your simulation isn't behaving as expected, and you suspect binning problems.

**Workflow:**

```bash
# Visualize current setup
python westpa_visualizer.py system.py --summary -o current_bins.png \
    --xlabel "RMSD (Å)" --ylabel "MinDist (Å)"

# Check summary for:
# 1. Are there bins in regions you expect to be sampled?
# 2. Is the resolution too coarse in important regions?
# 3. Are quadrant centers placed correctly?
# 4. Does the bin count match what you specified?
```

**Common Issues Revealed:**
- Missing fine bins in regions of interest
- Incorrect quadrant center placement
- Bins extending beyond physically reasonable ranges
- Unintended gaps in coverage

---

## Advanced Usage

### Programmatic API

For advanced users who want to integrate the visualizer into custom workflows:

```python
from westpa_visualizer import BinSchemeParser, BinVisualizer
import numpy as np

# Parse system file
parser = BinSchemeParser('system.py')
bin_data = parser.parse()

# Access parsed data
print(f"Progress coordinates: {bin_data['pcoord_ndim']}")
print(f"Variables found: {list(bin_data['variables'].keys())}")
print(f"Mappers created: {len(bin_data['mappers'])}")

# Create visualizer
viz = BinVisualizer(
    bin_data,
    pcoord_labels=['Custom X', 'Custom Y']
)

# Generate bins
viz.generate_bins()

# Access bin information
for i, bin_info in enumerate(viz.bins[:5]):  # First 5 bins
    level = bin_info['level']
    x_range = bin_info['bounds'][0]
    y_range = bin_info['bounds'][1]
    print(f"Bin {i}: Level {level}, X=[{x_range[0]:.2f}, {x_range[1]:.2f}), "
          f"Y=[{y_range[0]:.2f}, {y_range[1]:.2f})")

# Get statistics
total_bins = len(viz.bins)
bins_per_level = {}
for b in viz.bins:
    level = b['level']
    bins_per_level[level] = bins_per_level.get(level, 0) + 1

print(f"Bins per level: {bins_per_level}")

# Customize visualization
viz.plot(
    output_file='custom_viz.png',
    xlabel='My X Axis',
    ylabel='My Y Axis',
    title='Custom Title',
    figsize=(20, 16),
    show_labels=True,
    show_grid=True
)
```

### Batch Processing Multiple Systems

Process multiple system files at once:

```python
#!/usr/bin/env python
"""
Batch visualizer for multiple WESTPA systems
"""
from westpa_visualizer import BinSchemeParser, BinVisualizer
import os
import sys

def batch_visualize(system_files, output_dir='visualizations'):
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    for sys_file in system_files:
        print(f"Processing {sys_file}...")
        
        try:
            # Parse
            parser = BinSchemeParser(sys_file)
            bin_data = parser.parse()
            
            # Visualize
            viz = BinVisualizer(bin_data)
            viz.generate_bins()
            
            # Output filename
            base_name = os.path.splitext(os.path.basename(sys_file))[0]
            out_file = os.path.join(output_dir, f'{base_name}_bins.png')
            
            # Plot
            viz.plot(output_file=out_file, figsize=(14, 12))
            
            # Collect stats
            results.append({
                'file': sys_file,
                'total_bins': len(viz.bins),
                'output': out_file
            })
            
        except Exception as e:
            print(f"Error processing {sys_file}: {e}")
            results.append({
                'file': sys_file,
                'error': str(e)
            })
    
    # Summary report
    print("\n" + "="*60)
    print("BATCH PROCESSING SUMMARY")
    print("="*60)
    for r in results:
        if 'error' in r:
            print(f"{r['file']}: ERROR - {r['error']}")
        else:
            print(f"{r['file']}: {r['total_bins']} bins → {r['output']}")
    
    return results

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: batch_viz.py system1.py system2.py ...")
        sys.exit(1)
    
    batch_visualize(sys.argv[1:])
```

### Custom Styling

Modify colors and styles by editing the source or creating a wrapper:

```python
from westpa_visualizer import BinVisualizer
import matplotlib.pyplot as plt

# ... parse and generate bins as usual ...

# Get the figure and axes before finalizing
fig, ax = plt.subplots(figsize=(16, 14))

# Manually draw bins with custom colors
for i, bin_info in enumerate(viz.bins):
    level = bin_info['level']
    bounds = bin_info['bounds']
    
    # Custom color scheme
    if level == 0:
        color = '#FFE6E6'  # Light red for outer
    elif level == 1:
        color = '#E6F2FF'  # Light blue for fine
    else:
        color = '#E6FFE6'  # Light green for deeper
    
    # Draw rectangle
    from matplotlib.patches import Rectangle
    rect = Rectangle(
        (bounds[0][0], bounds[1][0]),
        bounds[0][1] - bounds[0][0],
        bounds[1][1] - bounds[1][0],
        facecolor=color,
        edgecolor='black',
        linewidth=0.5
    )
    ax.add_patch(rect)
    
    # Add label
    center_x = (bounds[0][0] + bounds[0][1]) / 2
    center_y = (bounds[1][0] + bounds[1][1]) / 2
    ax.text(center_x, center_y, str(i), ha='center', va='center', fontsize=8)

# Finish plot
ax.set_xlabel('Custom X')
ax.set_ylabel('Custom Y')
plt.savefig('custom_styled.png', dpi=300, bbox_inches='tight')
```

---

## Customization Options

### Figure Size and DPI

Control the physical dimensions and resolution:

```bash
# Small figure for quick checks (default: 14×12 inches)
python westpa_visualizer.py system.py -o quick.png --figsize 10 8

# Large figure for presentations
python westpa_visualizer.py system.py -o presentation.png --figsize 20 16

# Programmatic control of DPI
```

```python
viz.plot(
    output_file='high_res.png',
    figsize=(16, 14),
    dpi=300  # High resolution for publication
)
```

### Labels and Titles

Full control over all text elements:

```bash
# Complete labeling
python westpa_visualizer.py system.py -o labeled.png \
    --xlabel "Reaction Coordinate ξ₁ (Å)" \
    --ylabel "Reaction Coordinate ξ₂ (Å)" \
    --title "Two-Dimensional Binning Scheme for Folding Pathway"
```

**Tips:**
- Use Unicode for special characters: `ξ`, `Å`, `°`, `θ`, `ϕ`
- Include units in parentheses: `(Å)`, `(nm)`, `(degrees)`
- Keep titles concise but descriptive

### Grid and Label Display

Control visual elements:

```bash
# Hide bin index labels for cleaner look
python westpa_visualizer.py system.py -o clean.png --no-labels

# Hide grid lines
python westpa_visualizer.py system.py -o nogrid.png --no-grid

# Both
python westpa_visualizer.py system.py -o minimal.png --no-labels --no-grid
```

**When to use:**
- `--no-labels`: For publication figures where specific bin indices aren't needed
- `--no-grid`: For cleaner appearance, especially with many small bins
- Both: For schematic representations

### Output Formats

Matplotlib supports many formats:

```bash
# Raster formats
python westpa_visualizer.py system.py -o output.png   # PNG (default)
python westpa_visualizer.py system.py -o output.jpg   # JPEG

# Vector formats (best for publication)
python westpa_visualizer.py system.py -o output.pdf   # PDF (recommended)
python westpa_visualizer.py system.py -o output.svg   # SVG
python westpa_visualizer.py system.py -o output.eps   # EPS

# Interactive formats
python westpa_visualizer.py system.py -o output.html  # HTML (if mpld3 installed)
```

**Recommendations:**
- **PNG**: General use, sharing, presentations
- **PDF**: Publications, scalable vector graphics
- **SVG**: Web use, further editing in Inkscape/Illustrator
- **EPS**: Legacy publication systems

---

## Understanding the Output

### Visual Elements

#### Bin Rectangles

Each rectangle represents one bin in your system:

- **Position**: Center corresponds to bin center
- **Size**: Dimensions show the bin's X and Y extent
- **Color**: Indicates nesting level (lighter = outer, darker = nested)
- **Border**: Black lines delineate bin boundaries

#### Color Coding by Nesting Level

```
Level 0 (Outer):    #E8F4F8  (Very light blue)
Level 1 (Nested):   #B3D9E6  (Medium blue)
Level 2 (Deeper):   #7FB3D5  (Darker blue)
Level 3+:           Progressive darkening
```

This makes it easy to see which regions have fine resolution (darker) vs. coarse resolution (lighter).

#### Quadrant Lines

Red (vertical) and blue (horizontal) lines show outer bin boundaries:

- **Vertical red lines**: X-axis divisions from outer mapper
- **Horizontal blue lines**: Y-axis divisions from outer mapper
- **Thickness**: Slightly thicker than grid lines for visibility
- **Style**: Solid lines to distinguish from grid

These lines indicate where nested bins are added via `add_mapper()`.

#### Bin Labels

Numbers inside each bin:

- **Content**: Sequential bin index (0, 1, 2, ...)
- **Position**: Centered in each bin
- **Font size**: Automatically scaled based on bin size
- **Color**: Black for contrast

Use these indices to reference specific bins in your simulation configuration.

#### Grid Lines

Subtle gray lines for coordinate reading:

- **Purpose**: Help read approximate bin positions
- **Spacing**: Automatic based on axis ranges
- **Style**: Light gray, thin, semi-transparent
- **Control**: Can be hidden with `--no-grid`

#### Legend

Shows important metadata:

- **Bin counts**: Number of bins at each nesting level
- **Walker distribution**: Total walkers per bin (if uniform)
- **Quadrant boundaries**: Actual detected boundary values
- **Position**: Top-right corner, adjustable

### Text Summary

When using `--summary`, you get detailed statistics:

```
===========================================================================
                       WESTPA BINNING SCHEME SUMMARY                       
===========================================================================
Progress coordinate dimensions: 2
Total number of bins: 445
Target walkers per bin: 8

Outer boundaries detected:
  X boundaries: [0.0, 10.0, inf]
  Y boundaries: [0.0, 10.0, inf]

Bin definitions:
---------------------------------------------------------------------------
  Bin  Level    pcoord[0] Range      pcoord[1] Range
---------------------------------------------------------------------------
    0      1     [  0.00,   1.30)     [  0.00,   1.80)
    1      1     [  0.00,   1.30)     [  1.80,   2.00)
    2      1     [  0.00,   1.30)     [  2.00,   2.20)
  ...
```

**Interpretation:**

- **Bin number**: Sequential index used in WESTPA
- **Level**: Nesting depth (0 = outer, 1 = first nested, etc.)
- **Ranges**: `[lower, upper)` — includes lower bound, excludes upper bound
- **Total walkers**: Bins × walkers/bin

---

## Troubleshooting

### Problem: "No bins created"

**Symptoms:**
- Empty visualization
- Error message about missing bins
- Zero bins reported in summary

**Causes:**
1. Boundary arrays defined after mapper creation
2. Variable names not recognized by parser
3. Syntax errors in system.py

**Solutions:**

```python
# ✓ CORRECT: Define before use
rmsd_outer = [0.0, 10.0, float("inf")]
mindist_outer = [0.0, 10.0, float("inf")]
outer_mapper = RectilinearBinMapper([rmsd_outer, mindist_outer])

# ✗ WRONG: Define after use
outer_mapper = RectilinearBinMapper([rmsd_outer, mindist_outer])
rmsd_outer = [0.0, 10.0, float("inf")]  # Too late!
```

**Debugging steps:**
1. Check system.py has proper variable definitions
2. Verify variables are named with recognizable patterns (e.g., `*_outer`, `*_bins`)
3. Run with `--summary` to see what the parser found
4. Look for Python syntax errors

### Problem: "Quadrant lines missing or incorrect"

**Symptoms:**
- No red/blue quadrant lines drawn
- Lines appear at wrong positions
- Lines don't match your expectations

**Causes:**
1. Outer boundaries not detected
2. Variable naming doesn't match expected patterns
3. Boundaries are all 0 and infinity

**Solutions:**

```python
# Ensure outer variables follow conventions
# Pattern 1: Explicit _outer suffix
coord0_outer = [0.0, 10.0, float("inf")]
coord1_outer = [0.0, 10.0, float("inf")]

# Pattern 2: Domain-specific with _outer
rmsd_outer = [0.0, 5.0, 10.0, float("inf")]
distance_outer = [0.0, 8.0, float("inf")]

# Pattern 3: X/Y naming
x_outer = [0.0, 12.0, float("inf")]
y_outer = [0.0, 12.0, float("inf")]
```

**Verification:**
```bash
# Run with summary to see detected boundaries
python westpa_visualizer.py system.py --summary | grep "boundaries"
```

### Problem: "Wrong axis labels" or "Labels don't match my system"

**Symptoms:**
- Axes labeled "Progress Coordinate 0/1" when you want specific names
- Labels from previous run seem cached

**Cause:**
Not specifying `--xlabel` and `--ylabel`

**Solution:**

```bash
# Always specify labels for your specific system
python westpa_visualizer.py system.py -o output.png \
    --xlabel "Your X Coordinate (units)" \
    --ylabel "Your Y Coordinate (units)"
```

### Problem: "Too many bins, visualization is cluttered"

**Symptoms:**
- Bin labels overlap and are unreadable
- Plot is too dense to interpret
- File size is very large

**Solutions:**

```bash
# Option 1: Hide labels
python westpa_visualizer.py system.py -o clean.png --no-labels --figsize 20 16

# Option 2: Increase figure size
python westpa_visualizer.py system.py -o large.png --figsize 24 20

# Option 3: Use programmatic API to filter
```

```python
# Show only certain nesting levels
viz.generate_bins()
viz.bins = [b for b in viz.bins if b['level'] == 1]  # Only level 1 bins
viz.plot(output_file='filtered.png')
```

### Problem: "Parser fails on my system.py"

**Symptoms:**
- Python exceptions during parsing
- Variables not found
- Mapper construction fails

**Common issues:**

1. **Complex Python expressions:**
   ```python
   # May not parse correctly
   boundaries = some_function_call()
   
   # Use simple expressions
   boundaries = [0.0, 5.0, 10.0, float("inf")]
   ```

2. **Imports from other files:**
   ```python
   # May fail if module not available
   from my_module import boundaries
   
   # Define directly in system.py
   boundaries = [...]
   ```

3. **Dynamic construction:**
   ```python
   # Hard to parse
   for i in range(num_bins):
       mappers.append(...)
   
   # Use explicit definitions
   ```

**Workaround:**
Create a simplified `system_minimal.py` for visualization:

```python
# system_minimal.py - simplified for visualization only
from westpa.core.binning import RectilinearBinMapper, RecursiveBinMapper
import numpy as np

class System:
    def __init__(self):
        self.pcoord_ndim = 2
        
        # Copy only the bin boundary definitions
        rmsd_outer = [0.0, 10.0, float("inf")]
        mindist_outer = [0.0, 10.0, float("inf")]
        
        rmsd_fine = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
        mindist_fine = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
        
        outer_mapper = RectilinearBinMapper([rmsd_outer, mindist_outer])
        self.bin_mapper = RecursiveBinMapper(outer_mapper)
        
        fine_mapper = RectilinearBinMapper([rmsd_fine, mindist_fine])
        self.bin_mapper.add_mapper(fine_mapper, [2.5, 2.5])
        
        self.bin_target_counts = np.full((self.bin_mapper.nbins,), 8)
```

### Problem: "Different systems look the same"

**Symptom:**
Visualizations of different system files appear identical

**Cause:**
You have the same outer bin structure even though nested bins differ

**Solution:**
- Use `--title` to distinguish: `--title "System A: Fine Resolution"`
- Check `--summary` output for actual bin counts
- Look at nesting levels in the legend
- Inspect text summary for detailed differences

---

## Best Practices

### 1. Always Validate Before Running Simulations

```bash
# Standard validation workflow
python westpa_visualizer.py system.py --summary -o bins_validation.png \
    --xlabel "RMSD (Å)" --ylabel "MinDist (Å)"
```

**Check:**
- Total bin count is reasonable for your computational budget
- Fine bins cover regions of interest
- No unexpected gaps or overlaps
- Quadrant centers are correct

### 2. Use Descriptive File Names

```bash
# Bad
python westpa_visualizer.py system.py -o out.png

# Good
python westpa_visualizer.py system.py -o protein_X_folding_bins_v2.png \
    --title "Protein X Folding - Binning v2"
```

### 3. Document Your Binning Choices

Create a README alongside visualizations:

```markdown
# Binning Scheme for Protein X Folding

- **System:** Protein X folding from unfolded to native state
- **Progress coordinates:** RMSD to native, minimum distance to binding site
- **Total bins:** 445
- **Resolution:** Fine (0.1 Å) in bound region, coarse (1.0 Å) elsewhere
- **Justification:** High resolution needed to capture binding mechanism
- **File:** protein_X_bins.png
```

### 3. Use Version Control for system.py

Track changes to binning schemes:

```bash
git commit system.py -m "Increased resolution in bound state (100→200 bins)"
python westpa_visualizer.py system.py -o bins_v3.png
```

### 4. Compare Before and After

When modifying binning:

```bash
# Before
python westpa_visualizer.py system_old.py -o before.png --title "Before"

# After
python westpa_visualizer.py system_new.py -o after.png --title "After"

# Side-by-side comparison reveals impacts
```

### 5. Standardize Labels Across Projects

For consistency in publications:

```bash
# Create alias with standard labels for your research group
alias binviz_protein="python3 /path/to/westpa_visualizer.py --xlabel 'RMSD (Å)' --ylabel 'MinDist (Å)'"

# Use consistently
binviz_protein system.py -o protein_A.png
binviz_protein system_B.py -o protein_B.png
```

### 6. Archive Visualizations With Simulation Data

```
project/
├── system.py
├── west.cfg
├── binning_scheme.png          # Include in repo
├── binning_summary.txt         # Save --summary output
└── simulations/
    └── iter_000001/
```

### 7. Test Edge Cases

Verify the tool handles your specific setup:

```bash
# Test with minimal system
python westpa_visualizer.py minimal_system.py

# Test with maximal complexity
python westpa_visualizer.py complex_nested_system.py

# Test with unusual coordinates
python westpa_visualizer.py angle_distance_system.py
```

---

## API Reference

### BinSchemeParser

Parses WESTPA system.py files to extract binning information.

```python
class BinSchemeParser:
    def __init__(self, filename):
        """
        Initialize parser with system file.
        
        Parameters:
        -----------
        filename : str
            Path to system.py file
        """
    
    def parse(self):
        """
        Parse system file and extract binning information.
        
        Returns:
        --------
        dict
            Dictionary containing:
            - 'pcoord_ndim': Number of progress coordinates
            - 'variables': Dictionary of defined variables
            - 'mappers': List of created mappers
            - 'bin_target_counts': Target walkers per bin
        """
```

**Example:**

```python
parser = BinSchemeParser('system.py')
data = parser.parse()

print(f"Dimensions: {data['pcoord_ndim']}")
print(f"Found variables: {list(data['variables'].keys())}")
```

### BinVisualizer

Creates visualizations from parsed bin data.

```python
class BinVisualizer:
    def __init__(self, bin_data, pcoord_labels=None):
        """
        Initialize visualizer.
        
        Parameters:
        -----------
        bin_data : dict
            Output from BinSchemeParser.parse()
        pcoord_labels : list of str, optional
            Custom labels for progress coordinates
            Default: ['Progress Coordinate 0', 'Progress Coordinate 1']
        """
    
    def generate_bins(self):
        """
        Generate bin structure from parsed data.
        Automatically detects outer boundaries.
        """
    
    def plot(self, output_file=None, xlabel=None, ylabel=None, 
             title=None, figsize=(14, 12), show_labels=True,
             show_grid=True, dpi=300):
        """
        Create visualization.
        
        Parameters:
        -----------
        output_file : str, optional
            Save to file (if None, displays interactively)
        xlabel : str, optional
            X-axis label (overrides pcoord_labels[0])
        ylabel : str, optional
            Y-axis label (overrides pcoord_labels[1])
        title : str, optional
            Plot title
        figsize : tuple, optional
            Figure size (width, height) in inches
        show_labels : bool, optional
            Show bin index labels
        show_grid : bool, optional
            Show grid lines
        dpi : int, optional
            Resolution for saved files
        """
    
    def print_summary(self):
        """
        Print detailed text summary of binning scheme.
        """
```

**Example:**

```python
from westpa_visualizer import BinSchemeParser, BinVisualizer

parser = BinSchemeParser('system.py')
data = parser.parse()

viz = BinVisualizer(data, pcoord_labels=['RMSD', 'Distance'])
viz.generate_bins()

# Create plot
viz.plot(
    output_file='bins.pdf',
    title='My Binning Scheme',
    figsize=(16, 14),
    dpi=300
)

# Print summary
viz.print_summary()
```

### Attributes

**BinVisualizer.bins**
```python
List[dict]
    Each dict contains:
    - 'index': bin number
    - 'level': nesting level
    - 'bounds': [(x_min, x_max), (y_min, y_max)]
```

**BinVisualizer.outer_boundaries**
```python
dict
    Detected outer boundaries:
    - 'x': [list of X boundaries]
    - 'y': [list of Y boundaries]
```

---

## Additional Resources

### Example System Files

See the WESTPA tutorials for example system.py files:
- [Protein folding tutorial](https://westpa.readthedocs.io/en/latest/tutorials/ala/tutorial.html)
- [Ligand binding tutorial](https://westpa.readthedocs.io/en/latest/tutorials/nacl/tutorial.html)

### Related Tools

- **WESTPA Analysis Tools:** `w_assign`, `w_trace`, `w_postanalysis`
- **Trajectory Visualization:** VMD, PyMOL with WESTPA plugin
- **Data Analysis:** `westpa_analysis` Python package

### Getting Help

**Common resources:**
1. WESTPA documentation: https://westpa.readthedocs.io/
2. WESTPA forum: https://groups.google.com/forum/#!forum/westpa-users
3. GitHub issues: https://github.com/westpa/westpa/issues

**For this tool specifically:**
- Provide minimal system.py example that reproduces the issue
- Include error messages and Python version
- Describe expected vs. actual behavior

---

## Appendix: Command-Line Quick Reference

```bash
# Basic visualization
python westpa_visualizer.py system.py

# With custom labels
python westpa_visualizer.py system.py --xlabel "X Label" --ylabel "Y Label"

# Save to file
python westpa_visualizer.py system.py -o output.png

# Text summary only
python westpa_visualizer.py system.py --summary

# Combined visualization and summary
python westpa_visualizer.py system.py --summary -o plot.png

# Custom size and title
python westpa_visualizer.py system.py -o plot.pdf \
    --figsize 16 14 \
    --title "My Title"

# Clean visualization (no labels or grid)
python westpa_visualizer.py system.py -o clean.png --no-labels --no-grid

# Complete example
python westpa_visualizer.py system.py \
    --summary \
    -o publication_figure.pdf \
    --xlabel "RMSD from Native (Å)" \
    --ylabel "Minimum Distance to Active Site (Å)" \
    --title "Adaptive Binning Scheme for Protein-Ligand Association" \
    --figsize 16 14
```

---

**Version:** 2.0  
**Last Updated:** 2024  
**For questions or issues:** See README.md

---
