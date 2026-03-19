import barnaba as bb 
import matplotlib.pyplot as plt 
from matplotlib import colors 
import pandas as pd 
import numpy as np
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import os

# Load all metrics from the master file 
data = pd.read_csv("ermsd_metrics.csv")  

# Extract metrics as numpy arrays 
frames = data['Frame'].values 
ermsd = data['eRMSD'].values 
rmsd = data['RMSD'].values 
rg = data['RadiusOfGyration'].values 
mindist = data['MinimumDistance'].values 
looprmsd = data['LoopRMSD'].values

# Configuration parameters
n_time_windows = 500  # Number of frames in the movie
overlap_fraction = 0.2  # Fraction of overlap between consecutive windows
min_frames_per_window = 10000  # Minimum frames needed for meaningful statistics

def create_movie_frames(save_individual_frames=True):
    """
    Create individual frames for the probability density evolution movie
    """
    
    # Calculate window parameters
    total_frames = len(frames)
    frames_per_window = total_frames // n_time_windows
    overlap_frames = int(frames_per_window * overlap_fraction)
    
    # Ensure we have enough frames per window
    if frames_per_window < min_frames_per_window:
        print(f"Warning: Only {frames_per_window} frames per window. Consider reducing n_time_windows.")
    
    # Define FIXED axis ranges for consistent movie frames
    ermsd_range = (0.2, 1.7)  # Fixed x-axis range
    rmsd_range = (0.0, 0.8)   # Fixed y-axis range
    
    # Create bins with fixed ranges
    ermsd_bins = np.linspace(ermsd_range[0], ermsd_range[1], 51)
    rmsd_bins = np.linspace(rmsd_range[0], rmsd_range[1], 51)
    
    # Calculate global max density for consistent color scaling
    h_global, _, _ = np.histogram2d(ermsd, rmsd, bins=[ermsd_bins, rmsd_bins], density=True)
    global_max_density = h_global.max()
    
    # Create output directory for frames
    if save_individual_frames and not os.path.exists('movie_frames'):
        os.makedirs('movie_frames')
    
    print(f"Creating {n_time_windows} frames...")
    
    for i in range(n_time_windows):
        # Calculate window indices
        start_idx = max(0, i * frames_per_window - overlap_frames)
        end_idx = min(total_frames, (i + 1) * frames_per_window)
        
        # Extract data for this window
        window_ermsd = ermsd[start_idx:end_idx]
        window_rmsd = rmsd[start_idx:end_idx]
        window_frames = frames[start_idx:end_idx]
        
        # Calculate 2D histogram for this window
        h, xedges, yedges = np.histogram2d(
            window_ermsd, window_rmsd, 
            bins=[ermsd_bins, rmsd_bins], 
            density=True
        )
        
        # Get the X and Y coordinates for the contour plot
        X, Y = np.meshgrid(
            (xedges[:-1] + xedges[1:]) / 2,
            (yedges[:-1] + yedges[1:]) / 2
        )
        
        # Create the figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create contour plot with consistent levels
        levels = np.linspace(0, global_max_density, 50)
        contour = ax.contourf(X, Y, h.T, levels=levels, cmap='viridis', extend='max')
        
        # Add contour lines
        contour_lines = ax.contour(X, Y, h.T, levels=10, colors='white', alpha=0.5, linewidths=0.5)
        
        # Add colorbar
        cbar = plt.colorbar(contour, ax=ax)
        cbar.set_label('Probability Density', fontsize=12)
        
        # Add labels and styling with FIXED axis limits
        ax.set_xlabel("eRMSD from native", fontsize=12)
        ax.set_ylabel("RMSD from native (nm)", fontsize=12)
        ax.set_xlim(ermsd_range)  # Fixed x-axis limits
        ax.set_ylim(rmsd_range)   # Fixed y-axis limits
        ax.axvline(0.7, ls="--", c='white', alpha=0.7, linewidth=1)
        
        # Add time information
        time_start = window_frames[0] if len(window_frames) > 0 else start_idx
        time_end = window_frames[-1] if len(window_frames) > 0 else end_idx
        ax.set_title(f'Probability Density Evolution\nFrames {time_start:,} - {time_end:,} '
                    f'({len(window_frames):,} frames)', fontsize=14)
        
        # Add progress indicator
        progress_text = f'Frame {i+1}/{n_time_windows}'
        ax.text(0.02, 0.98, progress_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        if save_individual_frames:
            # Save individual frame
            plt.savefig(f'movie_frames/frame_{i:03d}.png', dpi=150, bbox_inches='tight')
        
        plt.close()
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"Completed {i+1}/{n_time_windows} frames")
    
    print("All frames created!")
    return n_time_windows

def create_animated_gif():
    """
    Create an animated GIF from the generated frames using matplotlib animation
    """
    print("Creating animated movie...")
    
    # Animation parameters
    total_frames = len(frames)
    frames_per_window = total_frames // n_time_windows
    overlap_frames = int(frames_per_window * overlap_fraction)
    
    # Define FIXED axis ranges
    ermsd_range = (0.2, 1.7)  # Fixed x-axis range  
    rmsd_range = (0.0, 0.8)   # Fixed y-axis range
    ermsd_bins = np.linspace(ermsd_range[0], ermsd_range[1], 51)
    rmsd_bins = np.linspace(rmsd_range[0], rmsd_range[1], 51)
    
    # Calculate global max density
    h_global, _, _ = np.histogram2d(ermsd, rmsd, bins=[ermsd_bins, rmsd_bins], density=True)
    global_max_density = h_global.max()
    
    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(10, 8))
    
    def animate(frame_idx):
        ax.clear()
        
        # Calculate window indices
        start_idx = max(0, frame_idx * frames_per_window - overlap_frames)
        end_idx = min(total_frames, (frame_idx + 1) * frames_per_window)
        
        # Extract data for this window
        window_ermsd = ermsd[start_idx:end_idx]
        window_rmsd = rmsd[start_idx:end_idx]
        window_frames = frames[start_idx:end_idx]
        
        # Calculate histogram
        h, xedges, yedges = np.histogram2d(
            window_ermsd, window_rmsd, 
            bins=[ermsd_bins, rmsd_bins], 
            density=True
        )
        
        # Coordinates for contour plot
        X, Y = np.meshgrid(
            (xedges[:-1] + xedges[1:]) / 2,
            (yedges[:-1] + yedges[1:]) / 2
        )
        
        # Create contour plot
        levels = np.linspace(0, global_max_density, 21)
        contour = ax.contourf(X, Y, h.T, levels=levels, cmap='viridis', extend='max')
        ax.contour(X, Y, h.T, levels=10, colors='white', alpha=0.5, linewidths=0.5)
        
        # Styling with FIXED axis limits
        ax.set_xlabel("eRMSD from native", fontsize=12)
        ax.set_ylabel("RMSD from native (nm)", fontsize=12)
        ax.set_xlim(ermsd_range)  # Fixed x-axis limits
        ax.set_ylim(rmsd_range)   # Fixed y-axis limits
        ax.axvline(0.7, ls="--", c='white', alpha=0.7, linewidth=1)
        
        # Title with time info
        time_start = window_frames[0] if len(window_frames) > 0 else start_idx
        time_end = window_frames[-1] if len(window_frames) > 0 else end_idx
        ax.set_title(f'Probability Density Evolution\nFrames {time_start:,} - {time_end:,}', fontsize=14)
        
        # Progress indicator
        progress_text = f'Frame {frame_idx+1}/{n_time_windows}'
        ax.text(0.02, 0.98, progress_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        return contour.collections
    
    # Create animation
    ani = animation.FuncAnimation(fig, animate, frames=n_time_windows, 
                                 interval=200, blit=False, repeat=True)
    
    # Save as GIF
    print("Saving animation...")
    ani.save('D_probability_density_evolution.gif', writer='pillow', fps=5, dpi=100)
    plt.close()
    
    print("Animation saved as 'D_probability_density_evolution.gif'")


# Main execution
if __name__ == "__main__":
    print(f"Processing {len(frames):,} frames from MD trajectory...")
    print(f"eRMSD range: {ermsd.min():.3f} - {ermsd.max():.3f}")
    print(f"RMSD range: {rmsd.min():.3f} - {rmsd.max():.3f}")
    
    # Create individual frames
    n_frames = create_movie_frames(save_individual_frames=True)
    
    # Create animated GIF (always works)
    create_animated_gif()
    
    
    print("\nMovie creation complete!")
    print("Generated files:")
    print("- Individual frames: movie_frames/frame_*.png")
    print("- Animated GIF: probability_density_evolution.gif")
