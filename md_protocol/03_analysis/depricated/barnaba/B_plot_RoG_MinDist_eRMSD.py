import barnaba as bb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors

#-------------------------------------------------

# Define trajectory and topology files
# native = "1hs3.pdb"
# traj = "../../stripped_trajectories/1hs3foldedDES_production.nc"
# top = "../../stripped_trajectories/1hs3foldedDES_stripped.prmtop"

#-------------------------------------------------

# Calculate eRMSD between native and all frames in trajectory
# ermsd = bb.ermsd(native, traj, topology=top)

# # Instead of calculating eRMSD, load it from CSV file
# ermsd_data = pd.read_csv("ermsd_rmsd_data.csv")
# # Extract eRMSD column as numpy array
# ermsd = ermsd_data['eRMSD'].values  

# # Load Radius of Gyration data
# # If your file is space-delimited .dat, use delim_whitespace=True
# # If it's comma-delimited .csv, remove delim_whitespace parameter
# rg_data = pd.read_csv("../cpptraj/radGyr.csv")
# rg = rg_data['RadiusofGyration'].values

# # Load minimum distance data
# mindist_data = pd.read_csv("../cpptraj/minDist.csv")
# mindist = mindist_data['MinDist'].values

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

# Plot eRMSD vs Radius of Gyration (scatter plot)
plt.figure(figsize=(8, 6))
plt.scatter(ermsd, rg, s=1, alpha=0.5, c='steelblue')
plt.xlabel("eRMSD from native")
plt.ylabel("Radius of Gyration (Å)")
plt.xlim(left=0.2)
plt.axvline(0.7, ls="--", c='k')
plt.title('Scatter Plot: eRMSD vs Radius of Gyration')
plt.tight_layout()
plt.savefig('eRMSD_RoG_scatter.png', dpi=300)
plt.show()
plt.close()

#-------------------------------------------------

# Plot eRMSD vs Radius of Gyration (2D Histogram)
plt.figure(figsize=(8, 6))
h, xedges, yedges, img = plt.hist2d(ermsd, rg, bins=50, 
                                   cmap='viridis', 
                                   norm=colors.LogNorm())
cbar = plt.colorbar()
cbar.set_label('Count (log scale)')
plt.xlabel("eRMSD from native")
plt.ylabel("Radius of Gyration (Å)")
plt.xlim(left=0.2)
plt.axvline(0.7, ls="--", c='k', alpha=0.7)
plt.title('2D Histogram: eRMSD vs Radius of Gyration')
plt.tight_layout()
plt.savefig('eRMSD_RoG_2D_histogram.png', dpi=300)
plt.show()
plt.close()

#-------------------------------------------------

# Alternative method using plt.hist2d with density normalization
plt.figure(figsize=(8, 6))

# The density=True parameter normalizes the histogram
h, xedges, yedges, img = plt.hist2d(ermsd, rg, bins=50, 
                                   cmap='viridis', 
                                   density=True)  # This normalizes to probability density

# Add colorbar with correct label
cbar = plt.colorbar()
cbar.set_label('Probability Density')

# Add labels and reference lines
plt.xlabel("eRMSD from native")
plt.ylabel("Radius of Gyration (Å)")

plt.axvline(0.7, ls="--", c='w', alpha=0.7)

plt.title('2D Probability Density: eRMSD vs RoG')
plt.tight_layout()
plt.savefig('eRMSD_RoG_2D_probability_density.png', dpi=300)
plt.show()
plt.close()

# ----------------------------------------------------------------------

# Create a 2D histogram with density=True and no whitespace
# Create figure
plt.figure(figsize=(8, 6))

# Create 2D histogram with density=True
h, xedges, yedges, img = plt.hist2d(ermsd, rg, bins=50, 
                                    density=True,
                                    cmap='viridis')

# Create a new colormap with transparency for zero values
current_cmap = plt.cm.get_cmap('viridis')
current_cmap.set_under('white', alpha=0)  # Set zeros to be transparent

# Replot with the modified colormap and a tiny threshold
plt.clf()  # Clear the current figure
plt.hist2d(ermsd, rg, bins=50, 
           density=True,
           cmap=current_cmap, 
           vmin=1e-10)  # Set a tiny threshold to make zeros transparent

# Add a colorbar
cbar = plt.colorbar()
cbar.set_label('Probability Density')

# Add labels and reference lines
plt.xlabel("eRMSD from native")
plt.ylabel("Radius of Gyration (Å)")
plt.xlim(left=0.2)
plt.axvline(0.7, ls="--", c='k', alpha=0.7)
plt.title('2D Histogram with Density: eRMSD vs RoG')
plt.tight_layout()
plt.savefig('eRMSD_RoG_density_probability_density_transparent.png', dpi=300)
plt.show()
plt.close()

# ----------------------------------------------------------------------

# Create a contour plot of the 2D histogram
# Create the figure
plt.figure(figsize=(8, 6))

# Calculate the 2D histogram with density=True
h, xedges, yedges = np.histogram2d(ermsd, rg, bins=50, density=True)

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
plt.ylabel("Radius of Gyration (Å)")

plt.axvline(0.7, ls="--", c='w', alpha=0.7)
plt.title('Probability Density Contour: eRMSD vs RoG')
plt.tight_layout()

# Save and show
plt.savefig('eRMSD_RoG_contour.png', dpi=300)
plt.show()
plt.close()

#-------------------------------------------------

# Scatter plot for minimum distance and eRMSD
plt.figure(figsize=(8, 6))
plt.scatter(ermsd, mindist, s=1, alpha=0.5, c='steelblue')
plt.xlabel("eRMSD from native")
plt.ylabel("Minimum End-to-End Distance (Å)")
plt.xlim(left=0.2)
plt.axvline(0.7, ls="--", c='k')
plt.title('Scatter Plot: eRMSD vs Minimum Distance')
plt.tight_layout()
plt.savefig('eRMSD_MinDist_scatter.png', dpi=300)
plt.show()
plt.close()

#-------------------------------------------------

# Plot eRMSD vs Minimum Distance (2D Histogram)
plt.figure(figsize=(8, 6))
h, xedges, yedges, img = plt.hist2d(ermsd, mindist, bins=50, 
                                   cmap='viridis', 
                                   norm=colors.LogNorm())
cbar = plt.colorbar()
cbar.set_label('Count (log scale)')
plt.xlabel("eRMSD from native")
plt.ylabel("Minimum End-to-End Distance (Å)")
plt.xlim(left=0.2)
plt.axvline(0.7, ls="--", c='k', alpha=0.7)
plt.title('2D Histogram: eRMSD vs Minimum Distance')
plt.tight_layout()
plt.savefig('eRMSD_MinDist_2D_histogram.png', dpi=300)
plt.show()
plt.close()

#-------------------------------------------------

# Alternative method using plt.hist2d with density normalization
plt.figure(figsize=(8, 6))

# The density=True parameter normalizes the histogram
h, xedges, yedges, img = plt.hist2d(ermsd, mindist, bins=50, 
                                   cmap='viridis', 
                                   density=True)  # This normalizes to probability density

# Add colorbar with correct label
cbar = plt.colorbar()
cbar.set_label('Probability Density')

# Add labels and reference lines
plt.xlabel("eRMSD from native")
plt.ylabel("Minimum End-to-End Distance (Å)")

plt.axvline(0.7, ls="--", c='w', alpha=0.7)

plt.title('2D Probability Density: eRMSD vs Minimum Distance')
plt.tight_layout()
plt.savefig('eRMSD_MinDist_2D_probability_density.png', dpi=300)
plt.show()
plt.close()

# ----------------------------------------------------------------------

# Create a 2D histogram with density=True and no whitespace
# Create figure
plt.figure(figsize=(8, 6))

# Create 2D histogram with density=True
h, xedges, yedges, img = plt.hist2d(ermsd, mindist, bins=50, 
                                    density=True,
                                    cmap='viridis')

# Create a new colormap with transparency for zero values
current_cmap = plt.cm.get_cmap('viridis')
current_cmap.set_under('white', alpha=0)  # Set zeros to be transparent

# Replot with the modified colormap and a tiny threshold
plt.clf()  # Clear the current figure
plt.hist2d(ermsd, mindist, bins=50, 
           density=True,
           cmap=current_cmap, 
           vmin=1e-10)  # Set a tiny threshold to make zeros transparent

# Add a colorbar
cbar = plt.colorbar()
cbar.set_label('Probability Density')

# Add labels and reference lines
plt.xlabel("eRMSD from native")
plt.ylabel("Minimum End-to-End Distance (Å)")
plt.xlim(left=0.2)
plt.axvline(0.7, ls="--", c='k', alpha=0.7)
plt.title('2D Histogram with Density: eRMSD vs Minimum Distance')
plt.tight_layout()
plt.savefig('eRMSD_MinDist_density_probability_density_transparent.png', dpi=300)
plt.show()
plt.close()

# ----------------------------------------------------------------------

# Create a contour plot of the 2D histogram
# Create the figure
plt.figure(figsize=(8, 6))

# Calculate the 2D histogram with density=True
h, xedges, yedges = np.histogram2d(ermsd, mindist, bins=50, density=True)

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
plt.ylabel("Minimum End-to-End Distance (Å)")

plt.axvline(0.7, ls="--", c='w', alpha=0.7)
plt.title('Probability Density Contour: eRMSD vs Minimum Distance')
plt.tight_layout()

# Save and show
plt.savefig('eRMSD_MinDist_contour.png', dpi=300)
plt.show()
plt.close()