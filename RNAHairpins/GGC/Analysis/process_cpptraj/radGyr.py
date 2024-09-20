import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time as time

class RadiusofGyrationAnalysis:
    def __init__(self, txt_file_path):
        # Initialize the file paths
        self.txt_file_path = txt_file_path
        self.csv_file_path = 'radGyrData.csv'  # Output .csv file path
        self.output_file_path = 'AnalysisOutput.txt'  # Output .txt file path

    def append_to_output(self, text):
        self.time = time.asctime()
        with open(self.output_file_path, 'a') as f:
            f.write(text + '\n\n')

    def convert_txt_to_csv(self):
        # Define your custom column names
        column_names = ['Frame', 'RadiusofGyration']
        
        # Read the .txt file while skipping the first line, assigning custom column names, and handling whitespace
        data = pd.read_csv(self.txt_file_path, sep=r'\s+', skiprows=1, names=column_names)
        
        # Save the data as .csv
        data.to_csv(self.csv_file_path, index=False)
        self.append_to_output(f"Data successfully converted to {self.csv_file_path}")

    def scale_x_axis_to_ns(self, total_simulation_ns):
        # Load the CSV data
        data = pd.read_csv(self.csv_file_path)

        # Calculate the total number of frames
        total_frames = data['Frame'].max()

        # Scale Frame column to nanoseconds and create new "Time(ns)" column
        data['Time(ns)'] = data['Frame'] * (total_simulation_ns / total_frames)

        # Save the new data with the Time(ns) column
        scaled_csv_file_path = 'radGyrData.csv'
        data.to_csv(scaled_csv_file_path, index=False)
        self.csv_file_path = scaled_csv_file_path  # Update to use this file in future
        self.append_to_output(f"Data scaled to simulation length and saved to {scaled_csv_file_path}")

    def analyze_and_plot(self):
        # Load the scaled CSV data
        data = pd.read_csv(self.csv_file_path)

        # Extract both columns
        time_ns = data['Time(ns)']
        radGyr = data['RadiusofGyration']

        # Calculate the statistics
        max_value = radGyr.max()
        min_value = radGyr.min()
        average = radGyr.mean()
        std_dev = radGyr.std()

        # Find the frames corresponding to the max and min values
        max_frame = data.loc[radGyr.idxmax(), 'Frame']
        min_frame = data.loc[radGyr.idxmin(), 'Frame']

        # Find the top 5 largest and smallest values
        top_5_largest = data.nlargest(5, 'RadiusofGyration')
        top_5_smallest = data.nsmallest(5, 'RadiusofGyration')

        # Create a text output
        output_text = (
            f"Maximum Radius of Gyration: {max_value} (Frame: {max_frame})\n"
            f"Minimum Radius of Gyration: {min_value} (Frame: {min_frame})\n"
            f"Average Radius of Gyration: {average}\n"
            f"Radius of Gyration Standard Deviation: {std_dev}\n\n"
            f"Top 5 Largest Values and Corresponding Frames:\n"
            f"{top_5_largest[['Frame', 'RadiusofGyration']].to_string(index=False)}\n\n"
            f"Top 5 Smallest Values and Corresponding Frames:\n"
            f"{top_5_smallest[['Frame', 'RadiusofGyration']].to_string(index=False)}\n"
        )

        # Append the text output to the file
        self.append_to_output('------------------- Radius of Gyration ------------------------------  ' + self.time + '\n\n' + output_text + '\n' 
                              + '-------------------------------------------------' + '\n\n')

        # Plot the data using Time(ns) for the x-axis
        plt.figure(figsize=(12, 6))
        plt.plot(time_ns, data['RadiusofGyration'], color='purple', alpha=0.75, linewidth=.3)

        # Add horizontal line for the average value
        plt.hlines(y=average, xmin=time_ns.min(), xmax=time_ns.max(), color='r', linestyle='-')

        # Add labels and title
        plt.xlabel('Time (ns)')
        plt.ylabel('Radius of Gyration')
        plt.title('Radius of Gyration vs. Time (ns)')

        # Save the plot to a file
        plot_file_path = 'radGyrPlot.png'
        plt.savefig(plot_file_path)

        # Show the plot
        plt.show()

## ____________________Radius of Gyration______________________
# Usage:
# Initialize the class with the .txt file path
radGyrAnalysis = RadiusofGyrationAnalysis('radGyr.txt')

# Convert .txt to .csv 
radGyrAnalysis.convert_txt_to_csv()

# Scale the x-axis to a given simulation length (e.g., 100 nanoseconds)
radGyrAnalysis.scale_x_axis_to_ns(100)

# Analyze and plot the data
radGyrAnalysis.analyze_and_plot()

print('Radius of Gyration analysis complete')