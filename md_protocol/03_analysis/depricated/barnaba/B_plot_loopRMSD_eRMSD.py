import barnaba as bb
import matplotlib.pyplot as plt
from matplotlib import colors
import pandas as pd
import numpy as np
#-------------------------------------------------

# Define trajectory and topology files
# native="1hs3.pdb"
# traj = "../../stripped_trajectories/1hs3foldedDES_production.nc"
# top = "../../stripped_trajectories/1hs3foldedDES_stripped.prmtop"

# Calculate eRMSD between native and all frames in trajectory
# ermsd = bb.ermsd(native, traj, topology=top)

#-------------------------------------------------

# Load all metrics from the master file
data = pd.read_csv("ermsd_metrics.csv")

# Extract metrics as numpy arrays for plotting
frames = data['Frame'].values
ermsd = data['eRMSD'].values
rmsd = data['RMSD'].values
rg = data['RadiusOfGyration'].values
mindist = data['MinimumDistance'].values
looprmsd = data['LoopRMSD'].values
#-------------------------------------------------

# Plot RMSD time series
plt.xlabel("Frame")
plt.ylabel("Loop RMSD from native (nm)")
plt.plot(frames,looprmsd,color="purple", alpha=0.7, linewidth=.1)
plot_file_path = 'LoopRMSDnmr.png'
plt.tight_layout()
plt.savefig(plot_file_path)
plt.show()
plt.close()

# Plot RMSD histogram
plt.hist(looprmsd,density=True,bins=50,alpha=0.5,edgecolor="purple",color="purple")
plt.xlabel("Loop RMSD from native (Å)")
plot_file_path = 'LoopRMSDHistogramnmr.png'
plt.tight_layout()
plt.savefig(plot_file_path)
plt.show()
plt.close()

# Structures with eRMSD lower than 0.7 are typically significantly similar to the reference. 
# Note that structures with low RMSD (less than 0.4 nm) may be very different from native. 
# We can check if this is true by comparing RMSD and eRMSD

# Plot eRMSD vs RMSD 
plt.scatter(ermsd, looprmsd, s=1, alpha=0.5)
plt.xlabel("eRMSD from native")
plt.ylabel("Loop RMSD from native (Å)")
plt.axvline(0.7, ls="--", c='k')
plt.xlim(left=0.2)  # Start at 0 to show the line at 0.7 clearly
plt.tight_layout()
plt.savefig('eRMSD_LoopRMSDnmr.png')
plt.show()
plt.close()

# -----------------------------------------------

# Add 2D histogram for eRMSD vs RMSD
plt.figure(figsize=(8, 6))

# Create the 2D histogram
h, xedges, yedges, img = plt.hist2d(ermsd, looprmsd, bins=50, 
                                    cmap='viridis', 
                                    norm=colors.LogNorm())

# Add a colorbar
cbar = plt.colorbar()
cbar.set_label('Count (log scale)')

# Add labels and reference lines
plt.xlabel("eRMSD from native")
plt.ylabel("Loop RMSD from native (Å)")
plt.axvline(0.7, ls="--", c='k', alpha=0.7)  # White dashed line for better visibility
plt.xlim(left=0.2)

# Add a title
plt.title('2D Histogram: eRMSD vs Loop RMSD')
plt.tight_layout()

# Save and show the figure
plt.savefig('eRMSD_LoopRMSD_2D_histogram.png', dpi=300)
plt.show()
plt.close()

# --------------------------------------------------

# Alternative method using plt.hist2d with density normalization
plt.figure(figsize=(8, 6))

# The density=True parameter normalizes the histogram
h, xedges, yedges, img = plt.hist2d(ermsd, looprmsd, bins=50, 
                                   cmap='viridis', 
                                   density=True)  # This normalizes to probability density

# Add colorbar with correct label
cbar = plt.colorbar()
cbar.set_label('Probability Density')

# Add labels and reference lines
plt.xlabel("eRMSD from native")
plt.ylabel("Loop RMSD from native (Å)")

plt.axvline(0.7, ls="--", c='w', alpha=0.7)

plt.title('2D Probability Density: eRMSD vs Loop RMSD')
plt.tight_layout()
plt.savefig('eRMSD_LoopRMSD_2D_probability_density.png', dpi=300)
plt.show()
plt.close()

# ----------------------------------------------------------------------

# Create a 2D histogram with density=True and no whitespace
# Create figure
plt.figure(figsize=(8, 6))

# Create 2D histogram with density=True
h, xedges, yedges, img = plt.hist2d(ermsd, looprmsd, bins=50, 
                                    density=True,
                                    cmap='viridis')

# Create a new colormap with transparency for zero values
current_cmap = plt.cm.get_cmap('viridis')
current_cmap.set_under('white', alpha=0)  # Set zeros to be transparent

# Replot with the modified colormap and a tiny threshold
plt.clf()  # Clear the current figure
plt.hist2d(ermsd, looprmsd, bins=50, 
           density=True,
           cmap=current_cmap, 
           vmin=1e-10)  # Set a tiny threshold to make zeros transparent

# Add a colorbar
cbar = plt.colorbar()
cbar.set_label('Probability Density')

# Add labels and reference lines
plt.xlabel("eRMSD from native")
plt.ylabel("Loop RMSD from native (Å)")
plt.xlim(left=0.2)
plt.axvline(0.7, ls="--", c='k', alpha=0.7)
plt.title('2D Histogram with Density: eRMSD vs Loop RMSD')
plt.tight_layout()
plt.savefig('eRMSD_LoopRMSD_density_probability_density_transparent.png', dpi=300)
plt.show()
plt.close()

# ----------------------------------------------------------------------

# Create a contour plot of the 2D histogram
# Create the figure
plt.figure(figsize=(8, 6))

# Calculate the 2D histogram with density=True
h, xedges, yedges = np.histogram2d(ermsd, looprmsd, bins=50, density=True)

# Get the X and Y coordinates for the contour plot
X, Y = np.meshgrid(
    (xedges[:-1] + xedges[1:]) / 2,  # Center of bins for x-axis
    (yedges[:-1] + yedges[1:]) / 2,  # Center of bins for y-axis
)

# Create the contour plot
contour = plt.contourf(X, Y, h.T, levels=20, cmap='viridis')
# Note: h needs to be transposed (h.T) for contourf due to axis conventions

# Add contour lines for clearer visualization
contour_lines = plt.contour(X, Y, h.T, levels=10, colors='white', alpha=0.5, linewidths=0.5)

# Add a colorbar
cbar = plt.colorbar(contour)
cbar.set_label('Probability Density')

# Add labels and reference lines
plt.xlabel("eRMSD from native")
plt.ylabel("RMSD from native (Å)")

plt.axvline(0.7, ls="--", c='w', alpha=0.7)
plt.title('Probability Density Contour: eRMSD vs Loop RMSD')
plt.tight_layout()

# Save and show
plt.savefig('eRMSD_LoopRMSD_contour.png', dpi=300)
plt.show()
plt.close()