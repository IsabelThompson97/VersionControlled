import matplotlib.pyplot as plt
from matplotlib import colors
import pandas as pd
import numpy as np

# -----------------------------------------------
# -----------------------------------------------

# If you have a header-less CSV with tab-separated values
data = pd.read_csv("rmsdCompare.csv", sep='\t', header=None, names=['frame1', 'frame2', 'rmsd'])

# Alternatively, if your data is already in CSV format with comma separators
# data = pd.read_csv("rmsdCompare.csv", header=None, names=['frame1', 'frame2', 'rmsd'])

# Extract values
frame1 = data['frame1'].values
frame2 = data['frame2'].values
rmsd = data['rmsd'].values

# -----------------------------------------------
# Create scatter plot with panels for each frame1
# -----------------------------------------------

# Get unique frame1 values
unique_frame1 = np.unique(frame1)
num_panels = len(unique_frame1)

# Determine grid layout (try to make it square-ish)
num_cols = int(np.ceil(np.sqrt(num_panels)))
num_rows = int(np.ceil(num_panels / num_cols))

# Create figure and subplots
fig, axes = plt.subplots(num_rows, num_cols, figsize=(4*num_cols, 3*num_rows), sharex=True, sharey=True)
axes = axes.flatten() if num_panels > 1 else [axes]  # Ensure axes is always iterable

# Color map for RMSD values
cmap = plt.cm.viridis
norm = colors.Normalize(vmin=np.min(rmsd), vmax=np.max(rmsd))

# Plot each frame1 in its own panel
for i, ref_frame in enumerate(unique_frame1):
    if i < len(axes):
        ax = axes[i]
        
        # Filter data for this reference frame
        mask = frame1 == ref_frame
        x = frame2[mask]
        y = rmsd[mask]
        
        # Create scatter plot
        scatter = ax.scatter(x, y, c=y, cmap=cmap, norm=norm, alpha=0.8, s=50)
        
        # Add labels and title
        ax.set_title(f'Reference Frame: {ref_frame}')
        ax.set_xlabel('Frame')
        ax.set_ylabel('RMSD (Å)')
        
        # Add gridlines
        ax.grid(True, linestyle='--', alpha=0.7)

# Hide any unused subplots
for i in range(num_panels, len(axes)):
    axes[i].set_visible(False)

# # Add a colorbar
# cbar = fig.colorbar(scatter, ax=axes, pad=0.01, aspect=30)
# cbar.set_label('RMSD (Å)')

# Adjust layout
# plt.tight_layout()
plt.suptitle('RMSD Comparison Across Frames', fontsize=16, y=1.02)
plt.subplots_adjust(top=0.95)

# Save plot
plt.savefig('rmsd_comparison.png', dpi=300, bbox_inches='tight')

# Show plot
plt.show()
plt.close()