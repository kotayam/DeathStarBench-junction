#!/usr/bin/env python3
import sys
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Ensure the user provided at least one CSV file
if len(sys.argv) < 2:
    print("Usage: ./generate_multigraph.py <csv_file1> <csv_file2> ...")
    sys.exit(1)

csv_files = sys.argv[1:]
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)
timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = f"combined_dirty_rate_{timestamp_str}.png"
output_png = os.path.join(output_dir, output_filename)

# Create a slightly wider figure to accommodate the legend and time axis
plt.figure(figsize=(12, 7))

for file in csv_files:
    times = []
    mbps_rates = []
    print(f"Reading data from {file}...")
    try:
        with open(file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert the "HH:MM:SS" string into a chronological datetime object
                time_obj = datetime.strptime(row['Timestamp'], '%H:%M:%S')
                times.append(time_obj)
                mbps_rates.append(float(row['Rate_MB_per_sec']))
        
        # Plot the line for this specific CSV, using the filename as the legend label
        plt.plot(times, mbps_rates, linestyle='-', linewidth=2, label=file.replace('.csv', ''))
    
    except FileNotFoundError:
        print(f"❌ Error: Could not find '{file}'. Skipping.")
    except Exception as e:
        print(f"❌ An error occurred with '{file}': {e}")

# Format the X-axis to display the wall-clock time cleanly
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
plt.gcf().autofmt_xdate() # Auto-rotate the timestamps so they don't overlap

# Add labels, title, and grid
plt.title('Combined Memory Mutation Rates', fontsize=14, fontweight='bold')
plt.xlabel('Wall Clock Time', fontsize=12)
plt.ylabel('Mutation Rate (MB/s)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)

# Add a legend so you know which line is which container
plt.legend(loc='upper right', fontsize=10)
plt.tight_layout()

# Save the combined graph
plt.savefig(output_png, dpi=300)
print(f"✅ Success! Combined graph saved as '{output_png}'.")
