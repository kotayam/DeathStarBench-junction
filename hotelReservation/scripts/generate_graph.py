#!/usr/bin/env python3
import sys
import csv
import matplotlib.pyplot as plt
import os

if len(sys.argv) < 2:
    print("Usage: ./generate_graph.py <input_csv_file>")
    sys.exit(1)

input_csv = sys.argv[1]
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)
base_name = os.path.basename(input_csv)
output_png = os.path.join(output_dir, base_name.replace('.csv', '.png'))

elapsed_times = []
mbps_rates = []

print(f"Reading data from {input_csv}...")

try:
    with open(input_csv, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            elapsed_times.append(float(row['Elapsed_Seconds']))
            mbps_rates.append(float(row['Rate_MB_per_sec']))

    plt.figure(figsize=(10, 6))
    plt.plot(elapsed_times, mbps_rates, linestyle='-', color='#1f77b4', linewidth=2, label='Memory Dirty Rate')

    plt.title(f'Application Dirty Page Rate vs. Time ({input_csv})', fontsize=14, fontweight='bold')
    plt.xlabel('Elapsed Time (Seconds)', fontsize=12)
    plt.ylabel('Dirty Page Rate (MB/s)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.fill_between(elapsed_times, mbps_rates, alpha=0.2, color='#1f77b4')
    plt.tight_layout()

    plt.savefig(output_png, dpi=300)
    print(f"✅ Success! Graph saved as '{output_png}'.")

except FileNotFoundError:
    print(f"❌ Error: Could not find '{input_csv}'.")
    sys.exit(1)
except Exception as e:
    print(f"❌ An error occurred: {e}")
    sys.exit(1)
