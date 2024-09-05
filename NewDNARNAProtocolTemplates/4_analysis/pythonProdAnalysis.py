import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# For converting .txt to .csv
#----------------------------------------
## Define the file paths
# txt_file_path = 'minDist.txt'  # Update with your .txt file path
# csv_file_path = 'minDist_data.csv'  # The output .csv file path

## Read the data from the .txt file
# data = pd.read_csv(txt_file_path, sep=r'\s+', header=0, names=['frame', 'MinDist'])

## Save the data as .csv
# data.to_csv(csv_file_path, index=False)
# print(f"Data successfully converted to {csv_file_path}")
#-----------------------------------------------------------

# Load the CSV data
file_path = 'minDist_data.csv'  # Replace with your actual file path
data = pd.read_csv(file_path)

# Extract both columns
frames = data['frame']
min_dist = data['MinDist']

# Calculate the statistics
max_value = min_dist.max()
min_value = min_dist.min()
average = min_dist.mean()
std_dev = min_dist.std()

# Find the frames corresponding to the max and min values
max_frame = data.loc[min_dist.idxmax(), 'frame']
min_frame = data.loc[min_dist.idxmin(), 'frame']

# Display the results
print(f"Maximum Distance: {max_value} (Frame: {max_frame})")
print(f"Minimum Distance: {min_value} (Frame: {min_frame})")
print(f"Average Distance: {average}")
print(f"Distance Standard Deviation: {std_dev}")
#-----------------------------------------------------------------

# Create figure and axes
plt.figure(figsize=(12, 6))

# Plot the data
plt.plot(data['frame'], data['MinDist'], color='purple')

# Set X and Y axes limits
plt.xlim(0, 1000000)

# Add horizontal line
plt.hlines(y=average, xmin=0, xmax=1000000, color='r', linestyle='-')

# Add labels and title, ticks
plt.xlabel('ns')
plt.ylabel('Minimum Distance')
plt.title('Minimum Distance vs. Time')

# num_ticks = 6 # Number of ticks you want
# tick_step = 1000000 / (num_ticks - 1) # Total range divided by number of intervals

# tick_positions = np.arrage(0, 1000001, tick_step) # Tick positions

# # Convert tick positions to corresponding labels
ticks = np.arange(0, 1_000_001, 100_000)
plt.xticks(ticks=ticks, labels=[f'{int(tick):,}' for tick in ticks], rotation=45)

plt.show()