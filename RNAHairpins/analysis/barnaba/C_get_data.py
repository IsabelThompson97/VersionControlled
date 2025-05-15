# Usage: python get_data.py frame1 frame2 frame3 ... [output_file]
# This script extracts data for specific frames from master_trajectory_metrics.csv

import pandas as pd
import sys

def extract_frame_data(frame_list, output_file="frame_data.txt"):
    """Extract data for specific frames and save to file."""
    # Load data from master file
    data = pd.read_csv("ermsd_metrics.csv")
    
    # Get values for specified frames
    result = data[data['Frame'].isin(frame_list)]
    
    # Save results to output file
    with open(output_file, 'w') as f:
        f.write(result.to_string(index=False))
        
    print(f"Data for frames {frame_list} saved to {output_file}")

if __name__ == "__main__":
    # Get frame numbers from command line arguments
    if len(sys.argv) < 2:
        print("Usage: python get_data.py frame1 frame2 frame3 ... [output_file]")
        sys.exit(1)
    
    # Check if the last argument is a potential output file (doesn't start with a digit)
    if sys.argv[-1][0].isdigit():
        frames = [int(arg) for arg in sys.argv[1:]]
        output_file = "frame_data.txt"
    else:
        frames = [int(arg) for arg in sys.argv[1:-1]]
        output_file = sys.argv[-1]
    
    extract_frame_data(frames, output_file)