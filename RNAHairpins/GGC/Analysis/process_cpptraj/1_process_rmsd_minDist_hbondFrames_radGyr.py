import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time as time

class RadiusofGyrationAnalysis:
    def __init__(self, txt_file_path):
        # Initialize the file paths
        self.txt_file_path = txt_file_path
        self.csv_file_path = 'radGyrDataHeavyOnly.csv'  # Output .csv file path
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
        scaled_csv_file_path = 'radGyrDataHeavyOnly.csv'
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
        self.append_to_output('------------------- Radius of Gyration Heavy Only ------------------------------  ' + self.time + '\n\n' + output_text + '\n' 
                              + '-------------------------------------------------' + '\n\n')

        # Plot the data using Time(ns) for the x-axis
        plt.figure(figsize=(12, 6))
        plt.plot(time_ns, data['RadiusofGyration'], color='purple', alpha=0.75, linewidth=.3)
        plt.xlim(0, time_ns.max())

        # Add horizontal line for the average value
        plt.hlines(y=average, xmin=time_ns.min(), xmax=time_ns.max(), color='r', linestyle='-')

        # Add labels and title
        plt.xlabel('Time (ns)')
        plt.ylabel('Radius of Gyration')
        plt.title('Radius of Gyration vs. Time (ns)')

        ticks = np.linspace(0, time_ns.max(), num=11)
        plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        # Save the plot to a file
        plot_file_path = 'radGyrPlotHeavyOnly.png'
        plt.savefig(plot_file_path)

        # Show the plot
        plt.show()

class MinDistAnalysis:
    def __init__(self, txt_file_path):
        # Initialize the file paths
        self.txt_file_path = txt_file_path
        self.csv_file_path = 'minDistData.csv'  # Output .csv file path
        self.output_file_path = 'AnalysisOutput.txt'  # Output .txt file path
        self.time = time.asctime()

    def append_to_output(self, text):
        with open(self.output_file_path, 'a') as f:
            f.write(text + '\n\n')

    def convert_txt_to_csv(self):
        column_names = ['Frame', 'MinDist']  # Custom column names
        data = pd.read_csv(self.txt_file_path, sep=r'\s+', skiprows=1, names=column_names)
        data.to_csv(self.csv_file_path, index=False)
        self.append_to_output(f"Data successfully converted to {self.csv_file_path}")

    def scale_x_to_ns(self, total_ns):
        data = pd.read_csv(self.csv_file_path)
        total_frames = data['Frame'].max()
        data['Time(ns)'] = data['Frame'] * (total_ns / total_frames)
        data.to_csv(self.csv_file_path, index=False)
        self.append_to_output(f"Data scaled to {total_ns} ns and saved to {self.csv_file_path}")

    def analyze_and_plot(self):
        data = pd.read_csv(self.csv_file_path)
        time_ns = data['Time(ns)']
        min_dist = data['MinDist']

        max_value = min_dist.max()
        min_value = min_dist.min()
        average = min_dist.mean()
        std_dev = min_dist.std()

        # Find the frames corresponding to the max and min values
        max_frame = data.loc[min_dist.idxmax(), 'Frame']
        min_frame = data.loc[min_dist.idxmin(), 'Frame']

        # Find the top 5 largest and smallest values
        top_5_largest = data.nlargest(5, 'MinDist')
        top_5_smallest = data.nsmallest(5, 'MinDist')

        # Create a text output
        output_text = (
            f"Maximum Distance: {max_value} (Frame: {max_frame})\n"
            f"Minimum Distance: {min_value} (Frame: {min_frame})\n"
            f"Average Distance: {average}\n"
            f"Distance Standard Deviation: {std_dev}\n\n"
            f"Top 5 Largest Values and Corresponding Frames:\n"
            f"{top_5_largest[['Frame', 'MinDist']].to_string(index=False)}\n\n"
            f"Top 5 Smallest Values and Corresponding Frames:\n"
            f"{top_5_smallest[['Frame', 'MinDist']].to_string(index=False)}\n"
        )


        self.append_to_output('------------------- Minimum Distance ------------------------------  ' + self.time + '\n\n' + output_text + '\n' 
                              + '-------------------------------------------------' + '\n\n')

        plt.figure(figsize=(12, 6))
        plt.plot(time_ns, min_dist, color='purple', alpha=0.75, linewidth=.3)
        plt.xlim(0, time_ns.max())

        plt.hlines(y=average, xmin=0, xmax=time_ns.max(), color='r', linestyle='-')
        
        plt.xlabel('Time (ns)')
        plt.ylabel('Minimum Distance')
        plt.title('Minimum Distance vs. Time')

        ticks = np.linspace(0, time_ns.max(), num=11)
        plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        plt.savefig('minDistPlot.png')
        plt.show()

class RMSDAnalysis:
    def __init__(self, txt_file_path):
        self.txt_file_path = txt_file_path
        self.csv_file_path = 'rmsdData.csv'
        self.output_file_path = 'AnalysisOutput.txt'
        self.time = time.asctime()

    def append_to_output(self, text):
        with open(self.output_file_path, 'a') as f:
            f.write(text + '\n\n')

    def convert_txt_to_csv(self):
        column_names = ['Frame', 'RMSD']
        data = pd.read_csv(self.txt_file_path, sep=r'\s+', skiprows=1, names=column_names)
        data.to_csv(self.csv_file_path, index=False)
        self.append_to_output(f"Data successfully converted to {self.csv_file_path}")

    def scale_x_to_ns(self, total_ns):
        data = pd.read_csv(self.csv_file_path)
        total_frames = data['Frame'].max()
        data['Time(ns)'] = data['Frame'] * (total_ns / total_frames)
        data.to_csv(self.csv_file_path, index=False)
        self.append_to_output(f"Data scaled to {total_ns} ns and saved to {self.csv_file_path}")

    def analyze_and_plot(self):
        data = pd.read_csv(self.csv_file_path)
        time_ns = data['Time(ns)']
        rmsd = data['RMSD']

        max_value = rmsd.max()
        min_value = rmsd.min()
        average = rmsd.mean()
        std_dev = rmsd.std()

        # Find the frames corresponding to the max and min values
        max_frame = data.loc[rmsd.idxmax(), 'Frame']
        min_frame = data.loc[rmsd.idxmin(), 'Frame']

        # Find the top 5 largest and smallest values
        top_5_largest = data.nlargest(5, 'RMSD')
        top_5_smallest = data.nsmallest(5, 'RMSD')

        # Create a text output
        output_text = (
            f"Maximum RMSD: {max_value} (Frame: {max_frame})\n"
            f"Minimum RMSD: {min_value} (Frame: {min_frame})\n"
            f"Average RMSD: {average}\n"
            f"RMSD Standard Deviation: {std_dev}\n\n"
            f"Top 5 Largest Values and Corresponding Frames:\n"
            f"{top_5_largest[['Frame', 'RMSD']].to_string(index=False)}\n\n"
            f"Top 5 Smallest Values and Corresponding Frames:\n"
            f"{top_5_smallest[['Frame', 'RMSD']].to_string(index=False)}\n"
        )

        self.append_to_output('------------------- RMSD ------------------------------  ' + self.time + '\n\n' + output_text + '\n' 
                              + '-------------------------------------------------' + '\n\n')

        plt.figure(figsize=(12, 6))
        plt.plot(time_ns, rmsd, color='purple', alpha=0.75, linewidth=.3)
        plt.xlim(0, time_ns.max())

        plt.hlines(y=average, xmin=0, xmax=time_ns.max(), color='r', linestyle='-')

        plt.xlabel('Time (ns)')
        plt.ylabel('RMSD (Å)')
        plt.title('RMSD vs. Time')

        ticks = np.linspace(0, time_ns.max(), num=11)
        plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        plt.savefig('rmsdPlot.png')
        plt.show()
        
class HBondsAnalysis:
    def __init__(self, txt_file_path):
        self.txt_file_path = txt_file_path
        self.csv_file_path = 'hbondFramesData.csv'
        self.output_file_path = 'AnalysisOutput.txt'
        self.time = time.asctime()

    def append_to_output(self, text):
        with open(self.output_file_path, 'a') as f:
            f.write(text + '\n\n')

    def convert_txt_to_csv(self):
        column_names = ['Frame', 'HBonds']
        data = pd.read_csv(self.txt_file_path, sep=r'\s+', skiprows=1, names=column_names)
        data.to_csv(self.csv_file_path, index=False)
        self.append_to_output(f"Data successfully converted to {self.csv_file_path}")

    def scale_x_to_ns(self, total_ns):
        data = pd.read_csv(self.csv_file_path)
        total_frames = data['Frame'].max()
        data['Time(ns)'] = data['Frame'] * (total_ns / total_frames)
        data.to_csv(self.csv_file_path, index=False)
        self.append_to_output(f"Data scaled to {total_ns} ns and saved to {self.csv_file_path}")

    def analyze_and_plot(self):
        data = pd.read_csv(self.csv_file_path)
        time_ns = data['Time(ns)']
        hbonds = data['HBonds']

        max_value = hbonds.max()
        min_value = hbonds.min()
        average = hbonds.mean()
        std_dev = hbonds.std()

        # Find the frames corresponding to the max and min values
        max_frame = data.loc[hbonds.idxmax(), 'Frame']
        min_frame = data.loc[hbonds.idxmin(), 'Frame']

        # Find the top 5 largest and smallest values
        top_5_largest = data.nlargest(5, 'HBonds')
        top_5_smallest = data.nsmallest(5, 'HBonds')

        # Create a text output
        output_text = (
            f"Maximum Number of HBonds: {max_value} (Frame: {max_frame})\n"
            f"Minimum Number of HBonds: {min_value} (Frame: {min_frame})\n"
            f"Average Number of HBonds: {average}\n"
            f"Number of HBonds Standard Deviation: {std_dev}\n\n"
            f"Top 5 Largest Values and Corresponding Frames:\n"
            f"{top_5_largest[['Frame', 'HBonds']].to_string(index=False)}\n\n"
            f"Top 5 Smallest Values and Corresponding Frames:\n"
            f"{top_5_smallest[['Frame', 'HBonds']].to_string(index=False)}\n"
        )

        self.append_to_output('------------------- HBonds ------------------------------  ' + self.time + '\n\n' + output_text + '\n' 
                              + '-------------------------------------------------' + '\n\n')

        # Plot the data using Time(ns) for the x-axis
        plt.figure(figsize=(12, 6))
        plt.plot(time_ns, hbonds, color='purple', alpha=0.75, linewidth=.3)
        plt.xlim(0, time_ns.max())

        # Add horizontal line for the average value
        plt.hlines(y=average, xmin=0, xmax=time_ns.max(), color='r', linestyle='-')

        # Add labels and title
        plt.xlabel('Time (ns)')
        plt.ylabel('Number of HBonds')
        plt.title('HBonds vs. Time')

        ticks = np.linspace(0, time_ns.max(), num=11)
        plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        plt.savefig('hbondFramesPlot.png')
        plt.show()

##################################### USAGE #######################################

## ____________________Radius of Gyration______________________
# Usage:
# Initialize the class with the .txt file path
radGyrAnalysis = RadiusofGyrationAnalysis('radGyrHeavyOnly.txt')

# Convert .txt to .csv 
radGyrAnalysis.convert_txt_to_csv()

# Scale the x-axis to a given simulation length (e.g., 100 nanoseconds)
radGyrAnalysis.scale_x_axis_to_ns(1000)

# Analyze and plot the data
radGyrAnalysis.analyze_and_plot()

print('Radius of Gyration analysis complete')

# ____________________Minimum Distance______________________
# Usage:
# Initialize the class with the .txt file path
minDistAnalysis = MinDistAnalysis('minDist.txt')

# Convert .txt to .csv 
minDistAnalysis.convert_txt_to_csv()

# Scale the x-axis to the desired length in nanoseconds
minDistAnalysis.scale_x_to_ns(1000)

# Analyze and plot the data
minDistAnalysis.analyze_and_plot()

print('Minimum Distance analysis complete')

# ____________________RMSD______________________
# Usage:
# Initialize the class with the .txt file path
rmsdAnalysis = RMSDAnalysis('rmsd.txt')

# Convert .txt to .csv 
rmsdAnalysis.convert_txt_to_csv()

# Scale the x-axis to the desired length in nanoseconds
rmsdAnalysis.scale_x_to_ns(1000)

# Analyze and plot the data
rmsdAnalysis.analyze_and_plot()

print('RMSD analysis complete')

# ____________________HBonds______________________
# Usage:
# Initialize the class with the .txt file path
hbondsAnalysis = HBondsAnalysis('hbondFrames.txt')

# Convert .txt to .csv 
hbondsAnalysis.convert_txt_to_csv()

# Scale the x-axis to the desired length in nanoseconds
hbondsAnalysis.scale_x_to_ns(1000)

# Analyze and plot the data
hbondsAnalysis.analyze_and_plot()

print('Hydrogen Bond analysis complete')
