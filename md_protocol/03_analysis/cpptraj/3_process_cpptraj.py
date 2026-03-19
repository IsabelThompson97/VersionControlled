import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time as time

class RadiusofGyrationAnalysis:
    def __init__(self, txt_file_path):
        self.txt_file_path = txt_file_path
        self.csv_file_path = 'radGyr.csv' 
        self.output_file_path = 'analysisOutput_2KOCFolded_HRM.txt'
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
        plt.plot(time_ns, data['RadiusofGyration'], color="darkslateblue", alpha=0.95, linewidth=.3)
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

class RMSDtoNMRAnalysis:
    def __init__(self, txt_file_path, csv_file_path, figure_path, figure2):
        self.txt_file_path = txt_file_path
        self.csv_file_path = csv_file_path
        self.figure_path = figure_path
        self.figure2 = figure2
        self.output_file_path = 'analysisOutput_2KOCFolded_HRM.txt'
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
        self.output_file_path = 'analysisOutput_2KOCFolded_HRM.txt'
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

class MinDistAnalysis:
    def __init__(self, txt_file_path):
        self.txt_file_path = txt_file_path
        self.csv_file_path = 'minDistEnds.csv'
        self.output_file_path = 'analysisOutput_2KOCFolded_HRM.txt'
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

        self.append_to_output('------------------- Minimum Distance Res1 - Res14 ------------------------------  ' + self.time + '\n\n' + output_text + '\n' 
                              + '-------------------------------------------------' + '\n\n')

        plt.figure(figsize=(12, 6))
        plt.plot(time_ns, min_dist, color='darkslateblue', alpha=0.95, linewidth=.3)
        plt.xlim(0, time_ns.max())

        plt.hlines(y=average, xmin=0, xmax=time_ns.max(), color='r', linestyle='-')
        
        plt.xlabel('Time (ns)')
        plt.ylabel('Minimum Distance (Å)')
        plt.title('Minimum Distance vs. Time')

        ticks = np.linspace(0, time_ns.max(), num=11)
        plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        plt.savefig('minDist.png')
        plt.show()

class MinDistLoopContactsAnalysis:
    def __init__(self, dataset_name, txt_file_path, csv_file_path, figure_path):
        self.dataset_name = dataset_name
        self.txt_file_path = txt_file_path
        self.csv_file_path = csv_file_path
        self.figure_path = figure_path
        self.output_file_path = 'analysisOutput_2KOCFolded_HRM.txt'
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


        self.append_to_output('------------------- Minimum Distance Loop Contacts -' + self.dataset_name+ '------------------------------  ' + self.time + '\n\n' + output_text + '\n' 
                              + '-------------------------------------------------' + '\n\n')

        plt.figure(figsize=(12, 6))
        plt.plot(time_ns, min_dist, color='darkslateblue', alpha=0.95, linewidth=.3)
        plt.xlim(0, time_ns.max())

        plt.hlines(y=average, xmin=0, xmax=time_ns.max(), color='r', linestyle='-')
        
        plt.xlabel('Time (ns)')
        plt.ylabel('Minimum Distance (Å)')
        plt.title(self.dataset_name+'Minimum Distance vs. Time')

        ticks = np.linspace(0, time_ns.max(), num=11)
        plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        plt.savefig(self.figure_path)
        plt.show()

class HBondsAnalysis:
    def __init__(self, txt_file_path):
        self.txt_file_path = txt_file_path
        self.csv_file_path = 'hbondFrames.csv'
        self.output_file_path = 'analysisOutput_2KOCFolded_HRM.txt'
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
        plt.plot(time_ns, hbonds, color='darkslateblue', alpha=0.95, linewidth=.3)
        plt.xlim(0, time_ns.max())

        plt.hlines(y=average, xmin=0, xmax=time_ns.max(), color='r', linestyle='-')

        plt.xlabel('Time (ns)')
        plt.ylabel('Number of HBonds')
        plt.title('HBonds vs. Time')

        ticks = np.linspace(0, time_ns.max(), num=11)
        plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        plt.savefig('hbondFrames.png')
        plt.show()

class DihedralAnalysis:
    def __init__(self, txt_file_path, csv_file_path, figure_path, figure_path2):
        self.txt_file_path = txt_file_path
        self.csv_file_path = csv_file_path
        self.figure_path = figure_path
        self.figure_path2 = figure_path2
        self.output_file_path = 'analysisOutput_2KOCFolded_HRM.txt'
        self.time = time.asctime()

    def append_to_output(self, text):
        with open(self.output_file_path, 'a') as f:
            f.write(text + '\n\n')

    def convert_txt_to_csv(self):
        column_names = ['Frame', 'G9_Dihedral']
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
        dihedral = data['G9_Dihedral']

        max_value = dihedral.max()
        min_value = dihedral.min()
        average = dihedral.mean()
        std_dev = dihedral.std()

        max_frame = data.loc[dihedral.idxmax(), 'Frame']
        min_frame = data.loc[dihedral.idxmin(), 'Frame']

        top_5_largest = data.nlargest(5, 'G9_Dihedral')
        top_5_smallest = data.nsmallest(5, 'G9_Dihedral')

        output_text = (
            f"Maximum Angle (°): {max_value} (Frame: {max_frame})\n"
            f"Minimum Angle (°): {min_value} (Frame: {min_frame})\n"
            f"Average Angle (°): {average}\n"
            f"Dihedral Standard Deviation (°): {std_dev}\n\n"
            f"Top 5 Largest Values and Corresponding Frames:\n"
            f"{top_5_largest[['Frame', 'G9_Dihedral']].to_string(index=False)}\n\n"
            f"Top 5 Smallest Values and Corresponding Frames:\n"
            f"{top_5_smallest[['Frame', 'G9_Dihedral']].to_string(index=False)}\n"
        )

        self.append_to_output('------------------- G9-Dihedral ------------------------------  ' + self.time + '\n\n' + output_text + '\n' 
                              + '-------------------------------------------------' + '\n\n')

        plt.figure(figsize=(12, 6))
        plt.plot(time_ns, dihedral, color='darkslateblue', alpha=0.95, linewidth=.3)
        plt.xlim(0, time_ns.max())

        plt.hlines(y=average, xmin=0, xmax=time_ns.max(), color='r', linestyle='-')
        
        plt.xlabel('Time (ns)')
        plt.ylabel('G9 Dihedral (°)')
        plt.title('G9 Dihedral (°) vs. Time')

        ticks = np.linspace(0, time_ns.max(), num=11)
        plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        plt.savefig(self.figure_path)
        plt.show()

        plt.figure(figsize=(12, 6))
        plt.hist(dihedral,density=True,bins=50,alpha=0.5,edgecolor="purple",color="purple")
    
        plt.ylabel('Density')
        plt.xlabel('G9 Dihedral (°)')
        plt.title('G9 Dihedral (°) Histogram')

        plt.savefig(self.figure_path2)
        plt.show()

class PuckerAnalysis:
    def __init__(self, txt_file_path, csv_file_path, figure_path):
        self.txt_file_path = txt_file_path
        self.csv_file_path = csv_file_path
        self.figure_path = figure_path
        self.output_file_path = 'analysisOutput_2KOCFolded_HRM.txt'
        self.time = time.asctime()

    def append_to_output(self, text):
        with open(self.output_file_path, 'a') as f:
            f.write(text + '\n\n')

    def convert_txt_to_csv(self):
        column_names = ['Frame', 'Pucker']
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
        pucker = data['Pucker']

        max_value = pucker.max()
        min_value = pucker.min()
        average = pucker.mean()
        std_dev = pucker.std()

        max_frame = data.loc[pucker.idxmax(), 'Frame']
        min_frame = data.loc[pucker.idxmin(), 'Frame']

        top_5_largest = data.nlargest(5, 'Pucker')
        top_5_smallest = data.nsmallest(5, 'Pucker')

        output_text = (
            f"Maximum Angle (°): {max_value} (Frame: {max_frame})\n"
            f"Minimum Angle (°): {min_value} (Frame: {min_frame})\n"
            f"Average Angle (°): {average}\n"
            f"Pucker Standard Deviation (°): {std_dev}\n\n"
            f"Top 5 Largest Values and Corresponding Frames:\n"
            f"{top_5_largest[['Frame', 'Pucker']].to_string(index=False)}\n\n"
            f"Top 5 Smallest Values and Corresponding Frames:\n"
            f"{top_5_smallest[['Frame', 'Pucker']].to_string(index=False)}\n"
        )

        self.append_to_output('-------------------' + self.figure_path + '------------------------------  ' + self.time + '\n\n' + output_text + '\n' 
                              + '-------------------------------------------------' + '\n\n')

        plt.figure(figsize=(12, 6))
        plt.hist(pucker,density=True,bins=50,alpha=0.5,edgecolor="purple",color="purple")
    
        plt.ylabel('Density')
        plt.xlabel('Pucker (°)')
        plt.title('Sugar Pucker (°) Histogram')

        # ticks = np.linspace(0, time_ns.max(), num=11)
        # plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        plt.savefig(self.figure_path)
        plt.show()

class IonRDFAnalysis:
    def __init__(self, ion1, txt_file_path1, ion2, txt_file_path2, csv_file_path, figure_path):
        self.txt_file_path1 = txt_file_path1
        self.txt_file_path2 = txt_file_path2
        self.csv_file_path = csv_file_path
        self.figure_path = figure_path
        self.ion1 = ion1
        self.ion2 = ion2
        self.output_file_path = 'analysisOutput_2KOCFolded_HRM.txt'
        self.time = time.asctime()

    def append_to_output(self, text):
        with open(self.output_file_path, 'a') as f:
            f.write(text + '\n\n')

    def convert_txt_to_csv(self):
        ion1_data = pd.read_csv(self.txt_file_path1, sep=r'\s+', skiprows=1, names=['Distance', self.ion1]) 
        ion2_data = pd.read_csv(self.txt_file_path2, sep=r'\s+', skiprows=1, names=['Distance', self.ion2]) 
        distance = ion1_data['Distance'].values
        ion1_values = ion1_data[self.ion1].values
        ion2_values = ion2_data[self.ion2].values
        data = pd.DataFrame({
            'Distance': distance,
            self.ion1: ion1_values,
            self.ion2: ion2_values
        })
        data.to_csv(self.csv_file_path, index=False)
        self.append_to_output(f"Data successfully converted to {self.csv_file_path}")

    def analyze_and_plot(self):
        data = pd.read_csv(self.csv_file_path)
        distance = data['Distance']
        ion1_values = data[self.ion1]
        ion2_values = data[self.ion2]

        max_ion1 = ion1_values.max()
        max_ion2 = ion2_values.max()

        max1_distance = data.loc[ion1_values.idxmax(), 'Distance']
        max2_distance = data.loc[ion2_values.idxmax(), 'Distance']

        output_text = (
            f'Maximum {self.ion1} RDF Value: {max_ion1} at Distance: {max1_distance} Å\n'
            f'Maximum {self.ion2} RDF Value: {max_ion2} at Distance: {max2_distance} Å\n'
        )

        self.append_to_output('------------------- RDF ' + self.ion1 + ' and ' + self.ion2 + ' ------------------------------  ' + self.csv_file_path + '  ' + self.time + '\n\n' + output_text + '\n'
                              + '-------------------------------------------------' + '\n\n')

        plt.figure(figsize=(12, 6))
        plt.plot(distance, ion1_values, color='darkslateblue', alpha=0.95)
        plt.plot(distance, ion2_values, color='darkorange', alpha=0.95)  
        plt.legend([self.ion1, self.ion2], loc='upper right')

        plt.xlim(0, distance.max())
      
        plt.xlabel('Distance (Å)')
        plt.ylabel('g(r)')
        plt.title('Radial Distribution Function')

        ticks = np.linspace(0, distance.max(), num=11)
        plt.xticks(ticks=ticks, labels=[f'{tick:.1f}' for tick in ticks])

        plt.savefig(self.figure_path)
        plt.show()

##################################### USAGE #######################################

# # ____________________Radius of Gyration______________________
# # Usage:
# # Initialize the class with the .txt file path
# radGyrAnalysis = RadiusofGyrationAnalysis('radGyr.txt')

# # Convert .txt to .csv 
# radGyrAnalysis.convert_txt_to_csv()

# # Scale the x-axis to a given simulation length (e.g., 100 nanoseconds)
# radGyrAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# radGyrAnalysis.analyze_and_plot()

# print('Radius of Gyration analysis complete')


# # ____________________RMSD to NMR______________________
# # Usage:
# # Initialize the class with the .txt file path
# rmsdtoNMRAnalysis = RMSDtoNMRAnalysis('rmsd_toNMR.txt', 'rmsd_toNMR.csv', 'rmsd_toNMR.png', 'rmsd_toNMR_Hist.png')

# # Convert .txt to .csv 
# rmsdtoNMRAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# rmsdtoNMRAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# rmsdtoNMRAnalysis.analyze_and_plot()

# print('RMSD to NMR analysis complete')


# # ____________________RMSD to NMR Backbone______________________
# # Usage:
# # Initialize the class with the .txt file path
# rmsdtoNMRBackboneAnalysis = RMSDtoNMRAnalysis('rmsd_toNMRBackbone.txt', 'rmsd_toNMRBackbone.csv', 'rmsd_toNMRBackbone.png', 'rmsd_toNMRBackbone_Hist.png')

# # Convert .txt to .csv 
# rmsdtoNMRBackboneAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# rmsdtoNMRBackboneAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# rmsdtoNMRBackboneAnalysis.analyze_and_plot()

# print('RMSD to NMR Backbone analysis complete')


# # ____________________RMSD to NMR Loop______________________
# # Usage:
# # Initialize the class with the .txt file path
# rmsdtoNMRLoopAnalysis = RMSDtoNMRAnalysis('rmsd_toNMRLoop.txt','rmsd_toNMRLoop.csv','rmsd_toNMRLoop.png', 'rmsd_toNMRLoop_Hist.png')

# # Convert .txt to .csv 
# rmsdtoNMRLoopAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# rmsdtoNMRLoopAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# rmsdtoNMRLoopAnalysis.analyze_and_plot()

# print('RMSD to NMR Loop analysis complete')


# # ____________________RMSD to NMR Stem______________________
# # Usage:
# # Initialize the class with the .txt file path
# rmsdtoNMRStemAnalysis = RMSDtoNMRAnalysis('rmsd_toNMRStem.txt','rmsd_toNMRStem.csv', 'rmsd_toNMRStem.png', 'rmsd_toNMRStem_Hist.png')

# # Convert .txt to .csv 
# rmsdtoNMRStemAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# rmsdtoNMRStemAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# rmsdtoNMRStemAnalysis.analyze_and_plot()

# print('RMSD to NMR Stem analysis complete')


# # ____________________RMSD to NMR Bases______________________
# # Usage:
# # Initialize the class with the .txt file path
# rmsdtoNMRBasesAnalysis = RMSDtoNMRAnalysis('rmsd_toNMR1-14Bases.txt','rmsd_toNMR1-14Bases.csv', 'rmsd_toNMR1-14Bases.png','rmsd_toNMR1-14Bases_Hist.png')

# # Convert .txt to .csv 
# rmsdtoNMRBasesAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# rmsdtoNMRBasesAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# rmsdtoNMRBasesAnalysis.analyze_and_plot()

# print('RMSD to NMR Bases analysis complete')


# # ____________________RMSD to First______________________
# # Usage:
# # Initialize the class with the .txt file path
# rmsdAnalysis = RMSDAnalysis('rmsd.txt')

# # Convert .txt to .csv 
# rmsdAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# rmsdAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# rmsdAnalysis.analyze_and_plot()

# print('RMSD to First analysis complete')


# # ____________________Minimum Distance 1-14______________________
# # Usage:
# # Initialize the class with the .txt file path
# minDistAnalysis = MinDistAnalysis('minDistEnds.txt')

# # Convert .txt to .csv 
# minDistAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# minDistAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# minDistAnalysis.analyze_and_plot()

# print('Minimum Distance analysis complete')


# # ____________________Minimum Distance G9-U6 Contact Analysis______________________
# # Usage:
# # Initialize the class with the .txt file path
# minDistLoopAnalysis = MinDistLoopContactsAnalysis('minDistG9-U6', 'minDistG9-U6.txt', 'minDistG9-U6.csv', 'minDistG9-U6.png')

# # Convert .txt to .csv 
# minDistLoopAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# minDistLoopAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# minDistLoopAnalysis.analyze_and_plot()

# print('Minimum Distance G9-U6 analysis complete')


# # ____________________Minimum Distance G9-U6sugar-base Contact Analysis______________________
# # Usage:
# # Initialize the class with the .txt file path
# minDistLoopAnalysis = MinDistLoopContactsAnalysis('minDistG9-U6sugar-base', 'minDistG9-U6sugar-base.txt', 'minDistG9-U6sugar-base.csv', 'minDistG9-U6sugar-base.png')

# # Convert .txt to .csv 
# minDistLoopAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# minDistLoopAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# minDistLoopAnalysis.analyze_and_plot()

# print('Minimum Distance G9-U6sugar-base analysis complete')


# # ____________________Minimum Distance G9-U7sugar-base Contact Analysis______________________
# # Usage:
# # Initialize the class with the .txt file path
# minDistLoopAnalysis = MinDistLoopContactsAnalysis('minDistG9-U7sugar-base', 'minDistG9-U7sugar-base.txt', 'minDistG9-U7sugar-base.csv', 'minDistG9-U7sugar-base.png')

# # Convert .txt to .csv 
# minDistLoopAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# minDistLoopAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# minDistLoopAnalysis.analyze_and_plot()

# print('Minimum Distance G9-U7sugar-base analysis complete')


# # ____________________Minimum Distance Loop Contact Analysis U7-C8base-phosphate______________________
# # Usage:
# # Initialize the class with the .txt file path
# minDistLoopAnalysis = MinDistLoopContactsAnalysis('minDistU7-C8base-phosphate', "minDistU7-C8base-phosphate.txt", "minDistU7-C8base-phosphate.csv", "minDistU7-C8base-phosphate.png")
# # Convert .txt to .csv 
# minDistLoopAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# minDistLoopAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# minDistLoopAnalysis.analyze_and_plot()

# print('Minimum Distance U7-C8base-phosphate analysis complete')


# ____________________G9-Dihedral______________________
# Usage:
# Initialize the class with the .txt file path
dihedralAnalysis = DihedralAnalysis('G9_dihedral.txt', 'G9_dihedral.csv', 'G9_dihedral.png', 'G9_dihedral_Hist.png')

# Convert .txt to .csv  
dihedralAnalysis.convert_txt_to_csv()

# Scale the x-axis to the desired length in nanoseconds
dihedralAnalysis.scale_x_to_ns(1000)

# Analyze and plot the data
dihedralAnalysis.analyze_and_plot()

print('G9-Dihedral analysis complete')


# # ____________________U7 Sugar Pucker______________________
# # Usage:
# # Initialize the class with the .txt file path
# U7sugarPuckerAnalysis = PuckerAnalysis('sugarPucker_U7.txt', 'sugarPucker_U7.csv', 'sugarPucker_U7.png')

# # Convert .txt to .csv  
# U7sugarPuckerAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# U7sugarPuckerAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# U7sugarPuckerAnalysis.analyze_and_plot()

# print('U7-sugarPucker analysis complete')

# # ____________________C8 Sugar Pucker______________________
# # Usage:
# # Initialize the class with the .txt file path
# C8sugarPuckerAnalysis = PuckerAnalysis('sugarPucker_C8.txt', 'sugarPucker_C8.csv', 'sugarPucker_C8.png')

# # Convert .txt to .csv  
# C8sugarPuckerAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# C8sugarPuckerAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# C8sugarPuckerAnalysis.analyze_and_plot()

# print('C8-sugarPucker analysis complete')

# # ____________________HBonds______________________
# # Usage:
# # Initialize the class with the .txt file path
# hbondsAnalysis = HBondsAnalysis('hbonds/hbondFrames.txt')

# # Convert .txt to .csv 
# hbondsAnalysis.convert_txt_to_csv()

# # Scale the x-axis to the desired length in nanoseconds
# hbondsAnalysis.scale_x_to_ns(1000)

# # Analyze and plot the data
# hbondsAnalysis.analyze_and_plot()

# print('Hydrogen Bonds per Frame analysis complete')


# # ____________________Radial Distribution Function______________________
# # Usage:
# # Initialize the class with the ion types and their respective .txt file paths
# ionRDFAnalysis = IonRDFAnalysis('Na+', 'RDF-Na.txt', 'Cl-', 'RDF-Cl.txt', 'RDF_ions.csv', 'RDF_ions.png')

# # Convert the .txt files to a single .csv file
# ionRDFAnalysis.convert_txt_to_csv()

# # Analyze and plot the radial distribution function
# ionRDFAnalysis.analyze_and_plot()

# print('Radial Distribution Function analysis complete') 
