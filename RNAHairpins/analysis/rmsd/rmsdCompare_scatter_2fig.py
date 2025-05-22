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
# Split the data into two figures, 7 panels each
# -----------------------------------------------

# Get unique frame1 values
unique_frame1 = np.unique(frame1)
num_panels_total = len(unique_frame1)

# Split frames into two groups
frames_group1 = unique_frame1[:7]  # First 7 frames
frames_group2 = unique_frame1[7:14]  # Next 7 frames (if available)

# Determine grid layout for each figure
num_cols = int(np.ceil(np.sqrt(7)))  # We want 7 panels per figure
num_rows = int(np.ceil(7 / num_cols))

# Color map for RMSD values (same for both figures)
cmap = plt.cm.viridis
norm = colors.Normalize(vmin=np.min(rmsd), vmax=np.max(rmsd))

# Calculate global axes limits for all subplots
x_min = np.min(frame2)
x_max = np.max(frame2)
y_min = np.min(rmsd)
y_max = np.max(rmsd)

# Add a small margin to the limits
x_margin = 0.05 * (x_max - x_min)
y_margin = 0.05 * (y_max - y_min)
x_limits = [x_min - x_margin, x_max + x_margin]
y_limits = [y_min - y_margin, y_max + y_margin]

# Function to create figure with panels
def create_figure(frame_group, group_num):
    # Create figure and subplots
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(4*num_cols, 3*num_rows), sharex=True, sharey=True)
    axes = axes.flatten()  # Ensure axes is always iterable
    
    # Plot each frame1 in its own panel
    for i, ref_frame in enumerate(frame_group):
        if i < len(axes):
            ax = axes[i]
            
            # Filter data for this reference frame
            mask = frame1 == ref_frame
            x = frame2[mask]
            y = rmsd[mask]
            
            # Create scatter plot
            scatter = ax.scatter(x, y, c=y, cmap=cmap, norm=norm, alpha=0.8, s=50)
            
            # Set consistent axes limits for all subplots
            ax.set_xlim(x_limits)
            ax.set_ylim(y_limits)
            
            # Add labels and title
            ax.set_title(f'Reference Frame: {ref_frame}')
            ax.set_xlabel('Frame')
            ax.set_ylabel('RMSD (Å)')
            
            # Add gridlines
            ax.grid(True, linestyle='--', alpha=0.7)
    
    # Hide any unused subplots
    for i in range(len(frame_group), len(axes)):
        axes[i].set_visible(False)
    
    # Adjust layout
    plt.suptitle(f'RMSD Comparison Across Frames (Group {group_num})', fontsize=16, y=1.02)
    plt.subplots_adjust(top=0.95)
    
    # Save plot
    plt.savefig(f'rmsd_comparison_group{group_num}.png', dpi=300, bbox_inches='tight')
    
    return fig

# Create first figure (frames group 1)
fig1 = create_figure(frames_group1, 1)
plt.show()
plt.close()

# Create second figure (frames group 2) if there are enough frames
if len(frames_group2) > 0:
    fig2 = create_figure(frames_group2, 2)
    plt.show()
    plt.close()