#!/usr/bin/env python3
import csv
import matplotlib.pyplot as plt
import os
import sys

input_file = './output/benchmark_results.csv'
output_dir = './output'

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Data arrays
targets = []
actuals = []
p50s, p75s, p90s, p99s, p999s = [], [], [], [], []
memcached_mbps = []
reservation_mbps = []

print(f"Reading data from {input_file}...")

try:
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip rows where Actual_Throughput_RPS is empty
            if not row['Actual_Throughput_RPS'].strip():
                continue
                
            targets.append(float(row['Target_Load_RPS']))
            actuals.append(float(row['Actual_Throughput_RPS']))
            p50s.append(float(row['P50_Latency_ms']))
            p75s.append(float(row['P75_Latency_ms']))
            p90s.append(float(row['P90_Latency_ms']))
            p99s.append(float(row['P99_Latency_ms']))
            p999s.append(float(row['P99.9_Latency_ms']))
            
            # Handle potentially empty memory columns
            mem_m = row['Memcached_Avg_MBps'].strip()
            mem_r = row['Reservation_Avg_MBps'].strip()
            memcached_mbps.append(float(mem_m) if mem_m else None)
            reservation_mbps.append(float(mem_r) if mem_r else None)
            
except FileNotFoundError:
    print(f"❌ Error: {input_file} not found. Please create it in the same directory.")
    sys.exit(1)

print("Generating graphs...")

# ---------------------------------------------------------
# Graph 1: Saturation Curve (Target vs Actual Throughput)
# ---------------------------------------------------------
plt.figure(figsize=(10, 6))
plt.plot(targets, actuals, marker='o', linewidth=2, label='Actual Throughput', color='blue')
plt.plot(targets, targets, linestyle='--', linewidth=2, label='Ideal (1:1)', color='gray')
plt.title('System Saturation: Target vs. Actual Throughput', fontsize=14, fontweight='bold')
plt.xlabel('Target Load (Requests/sec)', fontsize=12)
plt.ylabel('Actual Throughput (Requests/sec)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=11)
plt.tight_layout()
plt.savefig(f"{output_dir}/1_saturation_curve.png", dpi=300)
plt.close()

# ---------------------------------------------------------
# Graph 2: The Hockey Stick (Throughput vs P99 Latency)
# ---------------------------------------------------------
plt.figure(figsize=(10, 6))
plt.plot(actuals, p99s, marker='o', linewidth=2, color='red')
plt.title('P99 Latency vs. Throughput', fontsize=14, fontweight='bold')
plt.xlabel('Actual Throughput (Requests/sec)', fontsize=12)
plt.ylabel('P99 Latency (ms)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(f"{output_dir}/2_hockey_stick.png", dpi=300)
plt.close()

# ---------------------------------------------------------
# Graph 3: Latency Distribution across Tiers
# ---------------------------------------------------------
plt.figure(figsize=(10, 6))
percentiles = [50, 75, 90, 99, 99.9]
percentile_labels = ['P50', 'P75', 'P90', 'P99', 'P99.9']

for i in range(len(targets)):
    latencies = [p50s[i], p75s[i], p90s[i], p99s[i], p999s[i]]
    plt.plot(percentile_labels, latencies, marker='o', linewidth=2, label=f"{targets[i]} RPS Target")

plt.title('Latency Distribution by Percentile', fontsize=14, fontweight='bold')
plt.xlabel('Percentile', fontsize=12)
plt.ylabel('Latency (ms) - Log Scale', fontsize=12)
plt.yscale('log') # Log scale is crucial for viewing huge latency spikes
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend(fontsize=10)
plt.tight_layout()
plt.savefig(f"{output_dir}/3_latency_distribution.png", dpi=300)
plt.close()

# ---------------------------------------------------------
# Graph 4: Memory Mutation vs. Throughput
# ---------------------------------------------------------
# Only plot if we actually have memory data
if any(m is not None for m in memcached_mbps) or any(r is not None for r in reservation_mbps):
    plt.figure(figsize=(10, 6))
    if any(m is not None for m in memcached_mbps):
        plt.plot(actuals, memcached_mbps, marker='o', linewidth=2, label='Memcached', color='purple')
    if any(r is not None for r in reservation_mbps):
        plt.plot(actuals, reservation_mbps, marker='o', linewidth=2, label='Reservation', color='green')
        
    plt.title('Dirty Page Rate Scaling vs. Throughput', fontsize=14, fontweight='bold')
    plt.xlabel('Actual Throughput (Requests/sec)', fontsize=12)
    plt.ylabel('Average Dirty Page Rate (MB/s)', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/4_memory_mutation.png", dpi=300)
    plt.close()
    print("✅ Graph 4 created (Memory data found).")
else:
    print("⚠️ Skipping Graph 4 (No memory data found in CSV yet).")

print(f"✅ All done! Check the '{output_dir}' folder for your PNGs.")
