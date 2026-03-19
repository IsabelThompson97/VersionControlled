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
n_movie_frames = 500  # Number of frames in the movie
min_frames_per_step = 10000  # Starting point: first movie frame includes 0 → 50,000 trajectory frames

def create_cumulative_movie_frames(save_individual_frames=True):
    """
    Create frames showing cumulative probability density over time
    Each frame includes all data from start up to a certain point
    """
    
    # Define FIXED axis ranges for consistent movie frames
    ermsd_range = (0.2, 1.7)  # Fixed x-axis range
    rmsd_range = (0.0, 0.8)   # Fixed y-axis range
    
    # Create bins with fixed ranges
    ermsd_bins = np.linspace(ermsd_range[0], ermsd_range[1], 51)
    rmsd_bins = np.linspace(rmsd_range[0], rmsd_range[1], 51)
    
    # Calculate frame indices for each movie frame using LINEAR progression
    total_frames = len(frames)
    
    # Create linear spacing from min_frames_per_step to total_frames
    end_indices = np.linspace(min_frames_per_step, total_frames, n_movie_frames).astype(int)
    
    # Ensure we don't exceed total frames and remove any duplicates
    end_indices = np.unique(np.clip(end_indices, min_frames_per_step, total_frames))
    
    # Calculate global max density for consistent color scaling (using all data)
    h_global, _, _ = np.histogram2d(ermsd, rmsd, bins=[ermsd_bins, rmsd_bins], density=True)
    global_max_density = h_global.max()
    
    # Create output directory for frames
    if save_individual_frames and not os.path.exists('cumulative_movie_frames'):
        os.makedirs('cumulative_movie_frames')
    
    print(f"Creating {len(end_indices)} cumulative frames...")
    print(f"Frame progression: {min_frames_per_step:,} → {total_frames:,} frames")
    
    for i, end_idx in enumerate(end_indices):
        # Always start from the beginning, end at current point
        start_idx = 0
        current_end = min(end_idx, total_frames)
        
        # Extract cumulative data up to this point
        cumulative_ermsd = ermsd[start_idx:current_end]
        cumulative_rmsd = rmsd[start_idx:current_end]
        cumulative_frames = frames[start_idx:current_end]
        
        # Calculate 2D histogram for cumulative data
        h, xedges, yedges = np.histogram2d(
            cumulative_ermsd, cumulative_rmsd, 
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
        # levels = np.linspace(0, global_max_density, 21)
        contour = ax.contourf(X, Y, h.T, levels=20, cmap='viridis', extend='max')
        
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
        
        # Add time information - showing cumulative progress
        time_start = cumulative_frames[0] if len(cumulative_frames) > 0 else frames[0]
        time_end = cumulative_frames[-1] if len(cumulative_frames) > 0 else current_end
        completion_pct = (current_end / total_frames) * 100
        ax.set_title(f'Cumulative Probability Density\nFrames {time_start:,} - {time_end:,} '
                    f'({len(cumulative_frames):,} frames, {completion_pct:.1f}% complete)', 
                    fontsize=14)
        
        # Add progress bar
        progress_text = f'Frame {i+1}/{len(end_indices)}'
        ax.text(0.02, 0.98, progress_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Add completion percentage as visual indicator
        ax.text(0.98, 0.98, f'{completion_pct:.1f}%', transform=ax.transAxes, 
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
                fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        
        if save_individual_frames:
            # Save individual frame
            plt.savefig(f'cumulative_movie_frames/frame_{i:03d}.png', dpi=150, bbox_inches='tight')
        
        plt.close()
        
        # Progress indicator
        if (i + 1) % 10 == 0:
            print(f"Completed {i+1}/{len(end_indices)} frames ({completion_pct:.1f}% of trajectory)")
    
    print("All cumulative frames created!")
    return len(end_indices)

def create_cumulative_animated_gif():
    """
    Create an animated GIF showing cumulative probability density evolution
    """
    print("Creating cumulative animated movie...")
    
    # Define FIXED axis ranges
    ermsd_range = (0.2, 1.7)  # Fixed x-axis range  
    rmsd_range = (0.0, 0.8)   # Fixed y-axis range
    ermsd_bins = np.linspace(ermsd_range[0], ermsd_range[1], 51)
    rmsd_bins = np.linspace(rmsd_range[0], rmsd_range[1], 51)
    
    # Calculate frame progression using LINEAR spacing
    total_frames = len(frames)
    end_indices = np.linspace(min_frames_per_step, total_frames, n_movie_frames).astype(int)
    end_indices = np.unique(np.clip(end_indices, min_frames_per_step, total_frames))
    
    # Calculate global max density
    h_global, _, _ = np.histogram2d(ermsd, rmsd, bins=[ermsd_bins, rmsd_bins], density=True)
    global_max_density = h_global.max()
    
    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(10, 8))
    
    def animate(frame_idx):
        ax.clear()
        
        # Get cumulative data up to this frame
        current_end = min(end_indices[frame_idx], total_frames)
        cumulative_ermsd = ermsd[0:current_end]
        cumulative_rmsd = rmsd[0:current_end]
        cumulative_frames = frames[0:current_end]
        
        # Calculate histogram
        h, xedges, yedges = np.histogram2d(
            cumulative_ermsd, cumulative_rmsd, 
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
        
        # Title with cumulative info
        time_start = cumulative_frames[0] if len(cumulative_frames) > 0 else frames[0]
        time_end = cumulative_frames[-1] if len(cumulative_frames) > 0 else current_end
        completion_pct = (current_end / total_frames) * 100
        ax.set_title(f'Cumulative Probability Density\nFrames {time_start:,} - {time_end:,} ({completion_pct:.1f}% complete)', 
                    fontsize=14)
        
        # Progress indicators
        progress_text = f'Frame {frame_idx+1}/{len(end_indices)}'
        ax.text(0.02, 0.98, progress_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.text(0.98, 0.98, f'{completion_pct:.1f}%', transform=ax.transAxes, 
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
                fontsize=10, fontweight='bold')
        
        return contour.collections
    
    # Create animation
    ani = animation.FuncAnimation(fig, animate, frames=len(end_indices), 
                                 interval=200, blit=False, repeat=True)
    
    # Save as GIF
    print("Saving cumulative animation...")
    ani.save('D_cumulative_probability_density_evolution.gif', writer='pillow', fps=5, dpi=100)
    plt.close()
    
    print("Cumulative animation saved as 'D_cumulative_probability_density_evolution.gif'")


# Main execution
if __name__ == "__main__":
    print(f"Processing {len(frames):,} frames from MD trajectory...")
    print(f"eRMSD range: {ermsd.min():.3f} - {ermsd.max():.3f}")
    print(f"RMSD range: {rmsd.min():.3f} - {rmsd.max():.3f}")
    print(f"Will create cumulative movie showing growth from frame {frames[0]:,} to frame {frames[-1]:,}")
    print(f"Total frames in trajectory: {len(frames):,}")
    
    # Create cumulative frames
    n_frames = create_cumulative_movie_frames(save_individual_frames=True)
    
    # Create animated GIF (always works)
    create_cumulative_animated_gif()
    

    
    print("\nCumulative movie creation complete!")
    print("Generated files:")
    print("- Individual frames: cumulative_movie_frames/frame_*.png")
    print("- Animated GIF: cumulative_probability_density_evolution.gif")
 
    print("\nThe movie shows how the probability density landscape builds up over time,")
    print("starting with early frames and gradually including the full trajectory.")