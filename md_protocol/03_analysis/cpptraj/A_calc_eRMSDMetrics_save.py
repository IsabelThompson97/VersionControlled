import barnaba as bb
import numpy as np
import pandas as pd

# Define trajectory and topology files
native = "2KOCFolded_NMR.pdb"
traj = "../../stripped_trajectories/2KOCFolded_HRM_productionStripped.nc"
top = "../../stripped_trajectories/2KOCFolded_HRM_stripped.prmtop"

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
    rg_data = pd.read_csv("radGyr.csv")
    rg = rg_data['RadiusofGyration'].values
    
    # Load minimum distance data
    mindist_data = pd.read_csv("minDistEnds.csv")
    mindistends = mindist_data['MinDist'].values
    
    # Load loop RMSD data
    looprmsd_data = pd.read_csv("rmsd_toNMRLoop.csv")
    looprmsd = looprmsd_data['RMSD'].values

    # Load minDist contacts data

    mindistG9_6_data = pd.read_csv("minDistG9-6.csv")
    mindistG9_6 = mindistG9_6_data['MinDist'].values

    mindist_G9_6_sugar_base_data = pd.read_csv("minDistG9-6sugar-base.csv")
    mindist_G9_6_sugar_base = mindist_G9_6_sugar_base_data['MinDist'].values

    mindistG9_7_sugar_base_data = pd.read_csv("minDistG9-7sugar-base.csv")
    mindistG9_7_sugar_base = mindistG9_7_sugar_base_data['MinDist'].values

    mindistG7_8_base_phosphate_data = pd.read_csv("minDistG7-8base-phosphate.csv")
    mindistG7_8_base_phosphate = mindistG7_8_base_phosphate_data['MinDist'].values
    
    # Create a comprehensive DataFrame with all metrics
    all_metrics = {
        'Frame': frames,
        'eRMSD': ermsd,
        'RMSD': rmsd,
        'RadiusOfGyration': rg,
        'MinimumDistanceEnds': mindistends,
        'MinimumDistanceG9-6': mindistG9_6,
        'MinimumDistanceG9-6SugarBase': mindist_G9_6_sugar_base,
        'MinimumDistanceG9-7SugarBase': mindistG9_7_sugar_base,
        'MinimumDistanceG7-8BasePhosphate': mindistG7_8_base_phosphate,
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