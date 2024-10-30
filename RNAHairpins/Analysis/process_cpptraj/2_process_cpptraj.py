import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time as time

class RadiusofGyrationAnalysis:
    def __init__(self, txt_file_path):
        self.txt_file_path = txt_file_path
        self.csv_file_path = 'radGyr.csv' 
        self.output_file_path = 'AnalysisOutput.txt'
        self.time = time.asctime()

    def append_to_output(self, text):
        with open(self.output_file_path, 'a') as f:
            f.write(text + '\n\n')

    def convert_txt_to_csv(self):
        column_names = ['Frame', 'RadiusofGyration']
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
        radGyr = data['RadiusofGyration']

        max_value = radGyr.max()
        min_value = radGyr.min()
        average = radGyr.mean()
        std_dev = radGyr.std()

        max_frame = data.loc[radGyr.idxmax(), 'Frame']
        min_frame = data.loc[radGyr.idxmin(), 'Frame']

        top_5_largest = data.nlargest(5, 'RadiusofGyration')
        top_5_smallest = data.nsmallest(5, 'RadiusofGyration')

        output_text = (
            f"Maximum Radius of Gyration (Å): {max_value} (Frame: {max_frame})\n"
            f"Minimum Radius of Gyration (Å): {min_value} (Frame: {min_frame})\n"
            f"Average Radius of Gyration (Å): {average}\n"
            f"Radius of Gyration Standard Deviation (Å): {std_dev}\n\n"
            f"Top 5 Largest Values and Corresponding Frames:\n"
            f"{top_5_largest[['Frame', 'RadiusofGyration']].to_string(index=False)}\n\n"
            f"Top 5 Smallest Values and Corresponding Frames:\n"
            f"{top_5_smallest[['Frame', 'RadiusofGyration']].to_string(index=False)}\n"
        )

        self.append_to_output('------------------- Radius of Gyration ------------------------------  ' + self.time + '\n\n' + output_text + '\n' 
                              + '-------------------------------------------------' + '\n\n')

        plt.figure(figsize=(12, 6))
        plt.plot(time_ns, data['RadiusofGyration'], color='purple', alpha=0.75, linewidth=.3)
        plt.xlim(0, time_ns.max())

        plt.hlines(y=average, xmin=time_ns.min(), xmax=time_ns.max(), color='r', linestyle='-')

        plt.xlabel('Time (ns)')
        plt.ylabel('Radius of Gyration (Å)')
        plt.title('Radius of Gyration vs. Time (ns)')

        ticks = np.linspace(0, time_ns.max(), num=11)
        plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        plot_file_path = 'radGyr.png'
        plt.savefig(plot_file_path)

        plt.show()

class RMSDtoFoldedAnalysis:
    def __init__(self, txt_file_path):
        self.txt_file_path = txt_file_path
        self.csv_file_path = 'rmsd_toFolded.csv'
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

        plt.savefig('rmsd_toFolded.png')
        plt.show()

class RMSDAnalysis:
    def __init__(self, txt_file_path):
        self.txt_file_path = txt_file_path
        self.csv_file_path = 'rmsd.csv'
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
        plt.plot(time_ns, rmsd, color='purple', alpha=0.75, linewidth=.3)
        plt.xlim(0, time_ns.max())

        plt.hlines(y=average, xmin=0, xmax=time_ns.max(), color='r', linestyle='-')

        plt.xlabel('Time (ns)')
        plt.ylabel('RMSD (Å)')
        plt.title('RMSD vs. Time')

        ticks = np.linspace(0, time_ns.max(), num=11)
        plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        plt.savefig('rmsd.png')
        plt.show()

class MinDistAnalysis:
    def __init__(self, txt_file_path):
        self.txt_file_path = txt_file_path
        self.csv_file_path = 'minDist.csv'
        self.output_file_path = 'AnalysisOutput.txt'
        self.time = time.asctime()

    def append_to_output(self, text):
        with open(self.output_file_path, 'a') as f:
            f.write(text + '\n\n')

    def convert_txt_to_csv(self):
        column_names = ['Frame', 'MinDist']
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

        max_frame = data.loc[min_dist.idxmax(), 'Frame']
        min_frame = data.loc[min_dist.idxmin(), 'Frame']

        top_5_largest = data.nlargest(5, 'MinDist')
        top_5_smallest = data.nsmallest(5, 'MinDist')

        output_text = (
            f"Maximum Distance (Å): {max_value} (Frame: {max_frame})\n"
            f"Minimum Distance (Å): {min_value} (Frame: {min_frame})\n"
            f"Average Distance (Å): {average}\n"
            f"Distance Standard Deviation (Å): {std_dev}\n\n"
            f"Top 5 Largest Values and Corresponding Frames:\n"
            f"{top_5_largest[['Frame', 'MinDist']].to_string(index=False)}\n\n"
            f"Top 5 Smallest Values and Corresponding Frames:\n"
            f"{top_5_smallest[['Frame', 'MinDist']].to_string(index=False)}\n"
        )

        self.append_to_output('------------------- Minimum Distance Res1 - Res12 ------------------------------  ' + self.time + '\n\n' + output_text + '\n' 
                              + '-------------------------------------------------' + '\n\n')

        plt.figure(figsize=(12, 6))
        plt.plot(time_ns, min_dist, color='purple', alpha=0.75, linewidth=.3)
        plt.xlim(0, time_ns.max())

        plt.hlines(y=average, xmin=0, xmax=time_ns.max(), color='r', linestyle='-')
        
        plt.xlabel('Time (ns)')
        plt.ylabel('Minimum Distance (Å)')
        plt.title('Minimum Distance vs. Time')

        ticks = np.linspace(0, time_ns.max(), num=11)
        plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        plt.savefig('minDist.png')
        plt.show()

class MinDistNucleotideAnalysis:
    def __init__(self, txt_file_path):
        # Initialize the file paths
        self.txt_file_path = txt_file_path
        self.csv_file_path = 'minDistNucleotideO.csv'  # Output .csv file path
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
            f"Maximum Distance (Å): {max_value} (Frame: {max_frame})\n"
            f"Minimum Distance (Å): {min_value} (Frame: {min_frame})\n"
            f"Average Distance (Å): {average}\n"
            f"Distance Standard Deviation (Å): {std_dev}\n\n"
            f"Top 5 Largest Values and Corresponding Frames:\n"
            f"{top_5_largest[['Frame', 'MinDist']].to_string(index=False)}\n\n"
            f"Top 5 Smallest Values and Corresponding Frames:\n"
            f"{top_5_smallest[['Frame', 'MinDist']].to_string(index=False)}\n"
        )


        self.append_to_output('------------------- Minimum Distance Res1 - Res12 Nucleotide O ------------------------------  ' + self.time + '\n\n' + output_text + '\n' 
                              + '-------------------------------------------------' + '\n\n')

        plt.figure(figsize=(12, 6))
        plt.plot(time_ns, min_dist, color='purple', alpha=0.75, linewidth=.3)
        plt.xlim(0, time_ns.max())

        plt.hlines(y=average, xmin=0, xmax=time_ns.max(), color='r', linestyle='-')
        
        plt.xlabel('Time (ns)')
        plt.ylabel('Minimum Distance (Å)')
        plt.title('Minimum Distance vs. Time')

        ticks = np.linspace(0, time_ns.max(), num=11)
        plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        plt.savefig('minDistNucletoideO.png')
        plt.show()

class MinDistRiboseAnalysis:
    def __init__(self, txt_file_path):
        # Initialize the file paths
        self.txt_file_path = txt_file_path
        self.csv_file_path = 'minDistRiboseO.csv'  # Output .csv file path
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
            f"Maximum Distance (Å): {max_value} (Frame: {max_frame})\n"
            f"Minimum Distance (Å): {min_value} (Frame: {min_frame})\n"
            f"Average Distance (Å): {average}\n"
            f"Distance Standard Deviation (Å): {std_dev}\n\n"
            f"Top 5 Largest Values and Corresponding Frames:\n"
            f"{top_5_largest[['Frame', 'MinDist']].to_string(index=False)}\n\n"
            f"Top 5 Smallest Values and Corresponding Frames:\n"
            f"{top_5_smallest[['Frame', 'MinDist']].to_string(index=False)}\n"
        )


        self.append_to_output('------------------- Minimum Distance Res1 - Res12 Ribose O ------------------------------  ' + self.time + '\n\n' + output_text + '\n' 
                              + '-------------------------------------------------' + '\n\n')

        plt.figure(figsize=(12, 6))
        plt.plot(time_ns, min_dist, color='purple', alpha=0.75, linewidth=.3)
        plt.xlim(0, time_ns.max())

        plt.hlines(y=average, xmin=0, xmax=time_ns.max(), color='r', linestyle='-')
        
        plt.xlabel('Time (ns)')
        plt.ylabel('Minimum Distance (Å)')
        plt.title('Minimum Distance vs. Time')

        ticks = np.linspace(0, time_ns.max(), num=11)
        plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        plt.savefig('minDistRiboseO.png')
        plt.show()

class HBondsAnalysis:
    def __init__(self, txt_file_path):
        self.txt_file_path = txt_file_path
        self.csv_file_path = 'hbondFrames.csv'
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

        max_frame = data.loc[hbonds.idxmax(), 'Frame']
        min_frame = data.loc[hbonds.idxmin(), 'Frame']

        top_5_largest = data.nlargest(5, 'HBonds')
        top_5_smallest = data.nsmallest(5, 'HBonds')

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

        self.append_to_output('------------------- HBonds per Frame ------------------------------  ' + self.time + '\n\n' + output_text + '\n' 
                              + '-------------------------------------------------' + '\n\n')

        plt.figure(figsize=(12, 6))
        plt.plot(time_ns, hbonds, color='purple', alpha=0.75, linewidth=.3)
        plt.xlim(0, time_ns.max())

        plt.hlines(y=average, xmin=0, xmax=time_ns.max(), color='r', linestyle='-')

        plt.xlabel('Time (ns)')
        plt.ylabel('Number of HBonds')
        plt.title('HBonds vs. Time')

        ticks = np.linspace(0, time_ns.max(), num=11)
        plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        plt.savefig('hbondFrames.png')
        plt.show()

##################################### USAGE #######################################

## ____________________Radius of Gyration______________________
# Usage:
# Initialize the class with the .txt file path
radGyrAnalysis = RadiusofGyrationAnalysis('radGyr.txt')

# Convert .txt to .csv 
radGyrAnalysis.convert_txt_to_csv()

# Scale the x-axis to a given simulation length (e.g., 100 nanoseconds)
radGyrAnalysis.scale_x_to_ns(500)

# Analyze and plot the data
radGyrAnalysis.analyze_and_plot()

print('Radius of Gyration analysis complete')

# ____________________RMSD to Folded______________________
# Usage:
# Initialize the class with the .txt file path
rmsdtoFoldedAnalysis = RMSDToFoldedAnalysis('rmsd_toFolded.txt')

# Convert .txt to .csv 
rmsdtoFoldedAnalysis.convert_txt_to_csv()

# Scale the x-axis to the desired length in nanoseconds
rmsdtoFoldedAnalysis.scale_x_to_ns(500)

# Analyze and plot the data
rmsdtoFoldedAnalysis.analyze_and_plot()

print('RMSD to Folded analysis complete')

# ____________________RMSD to First______________________
# Usage:
# Initialize the class with the .txt file path
rmsdAnalysis = RMSDAnalysis('rmsd.txt')

# Convert .txt to .csv 
rmsdAnalysis.convert_txt_to_csv()

# Scale the x-axis to the desired length in nanoseconds
rmsdAnalysis.scale_x_to_ns(500)

# Analyze and plot the data
rmsdAnalysis.analyze_and_plot()

print('RMSD analysis complete')

# ____________________Minimum Distance______________________
# Usage:
# Initialize the class with the .txt file path
minDistAnalysis = MinDistAnalysis('minDist.txt')

# Convert .txt to .csv 
minDistAnalysis.convert_txt_to_csv()

# Scale the x-axis to the desired length in nanoseconds
minDistAnalysis.scale_x_to_ns(500)

# Analyze and plot the data
minDistAnalysis.analyze_and_plot()

print('Minimum Distance analysis complete')

# ____________________Minimum Distance Nucleotide O______________________
# Usage:
# Initialize the class with the .txt file path
minDistNucleotideAnalysis = MinDistNucleotideAnalysis('minDistNucleotideO.txt')

# Convert .txt to .csv 
minDistNucleotideAnalysis.convert_txt_to_csv()

# Scale the x-axis to the desired length in nanoseconds
minDistNucleotideAnalysis.scale_x_to_ns(500)

# Analyze and plot the data
minDistNucleotideAnalysis.analyze_and_plot()

print('Minimum Distance Nucleotide O analysis complete')

# ____________________Minimum Distance Ribose O______________________
# Usage:
# Initialize the class with the .txt file path
minDistRiboseAnalysis = MinDistRiboseAnalysis('minDistRiboseO.txt')

# Convert .txt to .csv 
minDistRiboseAnalysis.convert_txt_to_csv()

# Scale the x-axis to the desired length in nanoseconds
minDistRiboseAnalysis.scale_x_to_ns(500)

# Analyze and plot the data
minDistRiboseAnalysis.analyze_and_plot()

print('Minimum Distance Ribose O analysis complete')

# ____________________HBonds______________________
# Usage:
# Initialize the class with the .txt file path
hbondsAnalysis = HBondsAnalysis('hbondFrames.txt')

# Convert .txt to .csv 
hbondsAnalysis.convert_txt_to_csv()

# Scale the x-axis to the desired length in nanoseconds
hbondsAnalysis.scale_x_to_ns(500)

# Analyze and plot the data
hbondsAnalysis.analyze_and_plot()

print('Hydrogen Bonds per Frame analysis complete')