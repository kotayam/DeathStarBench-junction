#!/usr/bin/env python3
import argparse
import csv
import matplotlib.pyplot as plt
from datetime import datetime
import os
import sys

# Set up argument parsing
parser = argparse.ArgumentParser(description="Compare multiple dirty page rate CSVs on a single graph.")
parser.add_argument('-t', '--title', type=str, default='Dirty Page Rate Comparison', help='The title for the generated graph (enclose in quotes)')
parser.add_argument('csv_files', nargs='+', help='The CSV files to plot (e.g., ./output/*.csv)')

args = parser.parse_args()

csv_files = args.csv_files
graph_title = args.title

output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)

timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = f"workload_comparison_{timestamp_str}.png"
output_png = os.path.join(output_dir, output_filename)

# Made slightly larger for multiple labels
plt.figure(figsize=(14, 8)) 

for file in csv_files:
    elapsed = []
    mbps_rates = []
    print(f"Reading data from {file}...")
    try:
        with open(file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                elapsed.append(float(row['Elapsed_Seconds']))
                mbps_rates.append(float(row['Rate_MB_per_sec']))
        
        # Clean up the label name
        label_name = os.path.basename(file).replace('.csv', '')
        line_style = '-' 
        plt.plot(elapsed, mbps_rates, linestyle=line_style, linewidth=2, label=label_name)
    
    except FileNotFoundError:
        print(f"❌ Critical Error: Could not find '{file}'. Exiting.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An error occurred with '{file}': {e}")
        sys.exit(1)

# Add labels, dynamic title, and grid
plt.title(graph_title, fontsize=16, fontweight='bold')
plt.xlabel('Elapsed Time in Workload (Seconds)', fontsize=14)
plt.ylabel('Dirty Page Rate (MB/s)', fontsize=14)
plt.grid(True, linestyle='--', alpha=0.7)

# Ensure the graph starts at 0 on the X-axis
plt.xlim(left=0)

# Place the legend outside the graph so lines of text don't block the data
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
plt.tight_layout()

plt.savefig(output_png, dpi=300)
print(f"✅ Success! Comparison graph saved as '{output_png}'.")
