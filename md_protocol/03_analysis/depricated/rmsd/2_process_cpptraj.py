import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time as time

class RMSDtoFoldedAnalysis:
    def __init__(self, txt_file_path, csv_file_path, figure_path, figure2):
        self.txt_file_path = txt_file_path
        self.csv_file_path = csv_file_path
        self.figure_path = figure_path
        self.figure2 = figure2
        self.output_file_path = 'analysisOutput_1hs3foldedDES.txt'
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

        max_frame = data.loc[rmsd.idxmax(), 'Frame']
        min_frame = data.loc[rmsd.idxmin(), 'Frame']

        top_5_largest = data.nlargest(5, 'RMSD')
        top_5_smallest = data.nsmallest(5, 'RMSD')

        output_text = (
            f"Maximum RMSD (Å): {max_value} (Frame: {max_frame})\n"
            f"Minimum RMSD (Å): {min_value} (Frame: {min_frame})\n"
            f"Average RMSD (Å): {average}\n"
            f"RMSD Standard Deviation (Å): {std_dev}\n\n"
            f"Top 5 Largest Values and Corresponding Frames:\n"
            f"{top_5_largest[['Frame', 'RMSD']].to_string(index=False)}\n\n"
            f"Top 5 Smallest Values and Corresponding Frames:\n"
            f"{top_5_smallest[['Frame', 'RMSD']].to_string(index=False)}\n"
        )

        self.append_to_output('------------------- RMSD to NMR ------------------------------  ' + self.csv_file_path + '  ' + self.time + '\n\n' + output_text + '\n' 
                              + '-------------------------------------------------' + '\n\n')

        plt.figure(figsize=(12, 6))
        plt.plot(time_ns, rmsd, color='darkslateblue', alpha=0.95, linewidth=.3)
        plt.xlim(0, time_ns.max())
        plt.ylim(0,4)

        plt.hlines(y=average, xmin=0, xmax=time_ns.max(), color='r', linestyle='-')

        plt.xlabel('Time (ns)')
        plt.ylabel('RMSD (Å)')
        plt.title('RMSD vs. Time')

        ticks = np.linspace(0, time_ns.max(), num=11)
        plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        plt.savefig(self.figure_path)
        plt.show()

        plt.figure(figsize=(12, 6))
    
        # Calculate number of bins using Sturges' formula: k = ⌈log₂(n) + 1⌉
        n = len(rmsd)
        num_bins = int(np.ceil(np.log2(n) + 1))
        
        # Create the histogram
        n, bins, patches = plt.hist(rmsd, bins=num_bins, color='darkslateblue', alpha=0.75, edgecolor='black')
        
        # Add a vertical line for the mean
        plt.axvline(x=average, color='r', linestyle='-', label=f'Mean: {average:.2f} Å')
        
        # Add a vertical line for the median
        median = rmsd.median()
        plt.axvline(x=median, color='g', linestyle='--', label=f'Median: {median:.2f} Å')
        
        plt.xlabel('RMSD (Å)')
        plt.ylabel('Frequency')
        plt.title('Distribution of RMSD Values')
        plt.legend()
        
        plt.savefig(self.figure2)
        plt.show()

class RMSDAnalysis:
    def __init__(self, txt_file_path):
        self.txt_file_path = txt_file_path
        self.csv_file_path = 'rmsd.csv'
        self.output_file_path = 'analysisOutput_1hs3foldedDES.txt'
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

        max_frame = data.loc[rmsd.idxmax(), 'Frame']
        min_frame = data.loc[rmsd.idxmin(), 'Frame']

        top_5_largest = data.nlargest(5, 'RMSD')
        top_5_smallest = data.nsmallest(5, 'RMSD')

        output_text = (
            f"Maximum RMSD (Å): {max_value} (Frame: {max_frame})\n"
            f"Minimum RMSD (Å): {min_value} (Frame: {min_frame})\n"
            f"Average RMSD (Å): {average}\n"
            f"RMSD Standard Deviation (Å): {std_dev}\n\n"
            f"Top 5 Largest Values and Corresponding Frames:\n"
            f"{top_5_largest[['Frame', 'RMSD']].to_string(index=False)}\n\n"
            f"Top 5 Smallest Values and Corresponding Frames:\n"
            f"{top_5_smallest[['Frame', 'RMSD']].to_string(index=False)}\n"
        )

        self.append_to_output('------------------- RMSD to First------------------------------  ' + self.time + '\n\n' + output_text + '\n' 
                              + '-------------------------------------------------' + '\n\n')

        plt.figure(figsize=(12, 6))
        plt.plot(time_ns, rmsd, color='darkslateblue', alpha=0.95, linewidth=.3)
        plt.xlim(0, time_ns.max())

        plt.hlines(y=average, xmin=0, xmax=time_ns.max(), color='r', linestyle='-')

        plt.xlabel('Time (ns)')
        plt.ylabel('RMSD (Å)')
        plt.title('RMSD vs. Time')

        ticks = np.linspace(0, time_ns.max(), num=11)
        plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        plt.savefig('rmsd.png')
        plt.show()



##################################### USAGE #######################################

# # ____________________RMSD to First______________________
# # Usage:
# # Initialize the class with the .txt file path
# rmsdAnalysis = RMSDAnalysis('rmsd1-12.txt')

# # Convert .txt to .csv 
# rmsdAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# rmsdAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# rmsdAnalysis.analyze_and_plot()

# print('RMSD to first analysis complete')

# # ____________________RMSD to NMR 1-12______________________
# # Usage:
# # Initialize the class with the .txt file path
rmsdtoFoldedAnalysis = RMSDtoFoldedAnalysis('rmsd_toNMR1-12.txt', 'rmsd_toNMR1-12.csv', 'rmsd_toNMR1-12_2.png','rmsd_hist.png')

# Convert .txt to .csv 
rmsdtoFoldedAnalysis.convert_txt_to_csv()

# Scale the x-axis to the desired length in nanoseconds
rmsdtoFoldedAnalysis.scale_x_to_ns(1000)

# Analyze and plot the data
rmsdtoFoldedAnalysis.analyze_and_plot()

print('RMSD to NMR analysis complete')

# # ____________________RMSD to NMR Backbone______________________
# # Usage:
# # Initialize the class with the .txt file path
# rmsdtoFoldedAnalysis = RMSDtoFoldedAnalysis('rmsd_toNMRBackbone.txt', 'rmsd_toNMRBackbone.csv', 'rmsd_toNMRBackbone.png')

# # Convert .txt to .csv 
# rmsdtoFoldedAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# rmsdtoFoldedAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# rmsdtoFoldedAnalysis.analyze_and_plot()

# print('RMSD to NMR Backbone analysis complete')

# # ____________________RMSD to NMR Loop______________________
# # Usage:
# # Initialize the class with the .txt file path
# rmsdtoFoldedAnalysis = RMSDtoFoldedAnalysis('rmsd_toNMRLoop.txt','rmsd_toNMRLoop.csv','rmsd_toNMRLoop.png')

# # Convert .txt to .csv 
# rmsdtoFoldedAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# rmsdtoFoldedAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# rmsdtoFoldedAnalysis.analyze_and_plot()

# print('RMSD to NMR Loop analysis complete')

# # ____________________RMSD to NMR Stem______________________
# # Usage:
# # Initialize the class with the .txt file path
# rmsdtoFoldedAnalysis = RMSDtoFoldedAnalysis('rmsd_toNMRStem.txt','rmsd_toNMRStem.csv', 'rmsd_toNMRStem.png')

# # Convert .txt to .csv 
# rmsdtoFoldedAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# rmsdtoFoldedAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# rmsdtoFoldedAnalysis.analyze_and_plot()

# print('RMSD to NMR Stem analysis complete')

# ____________________RMSD to NMR Bases______________________
# Usage:
# Initialize the class with the .txt file path
# rmsdtoFoldedAnalysis = RMSDtoFoldedAnalysis('rmsd_toNMR1-12Bases.txt','rmsd_toNMR1-12Bases.csv', 'rmsd_toNMR1-12Bases.png')

# # Convert .txt to .csv 
# rmsdtoFoldedAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# rmsdtoFoldedAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# rmsdtoFoldedAnalysis.analyze_and_plot()

# print('RMSD to NMR Bases analysis complete')

