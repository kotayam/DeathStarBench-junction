#!/usr/bin/env python3
import csv
import matplotlib.pyplot as plt

# File paths
input_csv = 'dirty_pages_log.csv'
output_png = 'dirty_rate_graph.png'

elapsed_times = []
mbps_rates = []

print(f"Reading data from {input_csv}...")

try:
    with open(input_csv, 'r') as csvfile:
        # Use DictReader to automatically parse the header row
        reader = csv.DictReader(csvfile)
        for row in reader:
            elapsed_times.append(float(row['Elapsed_Seconds']))
            mbps_rates.append(float(row['Rate_MB_per_sec']))

    # Create the plot figure (10x6 inches)
    plt.figure(figsize=(10, 6))
    
    # Plot the data with a blue line
    plt.plot(elapsed_times, mbps_rates, linestyle='-', color='#1f77b4', linewidth=2, label='Memory Dirty Rate')

    # Add labels, title, and grid to make it look professional
    plt.title('Application Memory Mutation vs. Time', fontsize=14, fontweight='bold')
    plt.xlabel('Elapsed Time (Seconds)', fontsize=12)
    plt.ylabel('Mutation Rate (MB/s)', fontsize=12)
    
    # Add a subtle grid for easier reading
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Fill the area under the curve slightly for visual emphasis
    plt.fill_between(elapsed_times, mbps_rates, alpha=0.2, color='#1f77b4')

    plt.tight_layout()

    # Save the graph to disk with high resolution (300 dpi)
    plt.savefig(output_png, dpi=300)
    print(f"✅ Success! Graph saved as '{output_png}'.")

except FileNotFoundError:
    print(f"❌ Error: Could not find '{input_csv}'. Did you run the tracker script first?")
except Exception as e:
    print(f"❌ An error occurred: {e}")
