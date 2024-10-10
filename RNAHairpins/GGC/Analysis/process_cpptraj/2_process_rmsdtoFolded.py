import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time as time

class rmsdToFoldedAnalysis:
    def __init__(self, txt_file_path):
        self.txt_file_path = txt_file_path
        self.csv_file_path = 'rmsd_toFoldedData.csv'
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
            f"Maximum RMSD (Å): {max_value} (Frame: {max_frame})\n"
            f"Minimum RMSD (Å): {min_value} (Frame: {min_frame})\n"
            f"Average RMSD (Å): {average}\n"
            f"RMSD Standard Deviation (Å): {std_dev}\n\n"
            f"Top 5 Largest Values and Corresponding Frames:\n"
            f"{top_5_largest[['Frame', 'RMSD']].to_string(index=False)}\n\n"
            f"Top 5 Smallest Values and Corresponding Frames:\n"
            f"{top_5_smallest[['Frame', 'RMSD']].to_string(index=False)}\n"
        )

        self.append_to_output('------------------- RMSD to Folded ------------------------------  ' + self.time + '\n\n' + output_text + '\n' 
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

        plt.savefig('rmsd_toFoldedPlot.png')
        plt.show()
        
# ____________________RMSD to Folded______________________
# Usage:
# Initialize the class with the .txt file path
rmsdtoFoldedAnalysis = rmsdToFoldedAnalysis('rmsd_toFolded.txt')

# Convert .txt to .csv 
rmsdtoFoldedAnalysis.convert_txt_to_csv()

# Scale the x-axis to the desired length in nanoseconds
rmsdtoFoldedAnalysis.scale_x_to_ns(500)

# Analyze and plot the data
rmsdtoFoldedAnalysis.analyze_and_plot()

print('RMSD to Folded analysis complete')