import barnaba as bb
import numpy as np
import pandas as pd

# Define trajectory and topology files
native = "1hs3.pdb"
traj = "../../stripped_trajectories/1hs3foldedDES_production.nc"
top = "../../stripped_trajectories/1hs3foldedDES_stripped.prmtop"

# Calculate eRMSD between native and all frames in trajectory
ermsd = bb.ermsd(native, traj, topology=top)

# Calculate RMSD for all heavy atoms after optimal superposition
rmsd = bb.rmsd(native, traj, topology=top, heavy_atom=True)

# Create a frame number array
num_frames = len(ermsd)  # Assuming all arrays have the same length
frames = np.arange(num_frames)  # Creates array [0, 1, 2, ..., num_frames-1]

# Load all other metrics
try:
    # Load Radius of Gyration data
    rg_data = pd.read_csv("../cpptraj/radGyr.csv")
    rg = rg_data['RadiusofGyration'].values
    
    # Load minimum distance data
    mindist_data = pd.read_csv("../cpptraj/minDist.csv")
    mindist = mindist_data['MinDist'].values
    
    # Load loop RMSD data
    looprmsd_data = pd.read_csv("../newRMSD/rmsd_toNMRLoop.csv")
    looprmsd = looprmsd_data['RMSD'].values
    
    # Create a comprehensive DataFrame with all metrics
    all_metrics = {
        'Frame': frames,
        'eRMSD': ermsd,
        'RMSD': rmsd,
        'RadiusOfGyration': rg,
        'MinimumDistance': mindist,
        'LoopRMSD': looprmsd
    }
    
except FileNotFoundError as e:
    print(f"Warning: Some data files not found: {e}")
    print("Creating a partial metrics file with available data")
    
    # Create a basic DataFrame with calculated metrics
    all_metrics = {
        'Frame': frames,
        'eRMSD': ermsd,
        'RMSD': rmsd
    }
    
    # Add metrics if files exist
    try:
        all_metrics['RadiusOfGyration'] = rg
    except NameError:
        pass
    
    try:
        all_metrics['MinimumDistance'] = mindist
    except NameError:
        pass
    
    try:
        all_metrics['LoopRMSD'] = looprmsd
    except NameError:
        pass

# Create the final DataFrame and save to CSV
df_all_metrics = pd.DataFrame(all_metrics)
master_file_path = 'ermsd_metrics.csv'
df_all_metrics.to_csv(master_file_path, index=False)

print(f"All available metrics saved to {master_file_path}")