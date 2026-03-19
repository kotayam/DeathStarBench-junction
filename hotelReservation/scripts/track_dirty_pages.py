#!/usr/bin/env python3
import os
import sys
import time
import struct
import argparse
import csv
import socket

PAGE_SIZE = os.sysconf("SC_PAGE_SIZE") # Typically 4096 bytes

def get_vma_ranges(pid):
    """Reads /proc/[pid]/maps to get valid virtual memory ranges."""
    ranges = []
    try:
        with open(f"/proc/{pid}/maps", "r") as f:
            for line in f:
                parts = line.split()
                if not parts:
                    continue
                addr_range = parts[0]
                start_hex, end_hex = addr_range.split("-")
                ranges.append((int(start_hex, 16), int(end_hex, 16)))
    except FileNotFoundError:
        print(f"Error: Process {pid} not found.")
        sys.exit(1)
    return ranges

def clear_soft_dirty(pid):
    """Writes '4' to clear_refs to reset the soft-dirty tracking bit."""
    try:
        with open(f"/proc/{pid}/clear_refs", "w") as f:
            f.write("4\n")
    except PermissionError:
        print("Error: Must run as root (sudo) to write to clear_refs.")
        sys.exit(1)

def count_dirty_pages(pid, ranges):
    """Reads /proc/[pid]/pagemap to count pages with the soft-dirty bit (55) set."""
    dirty_pages = 0
    try:
        with open(f"/proc/{pid}/pagemap", "rb") as f:
            for start, end in ranges:
                start_page = start // PAGE_SIZE
                num_pages = (end - start) // PAGE_SIZE
                f.seek(start_page * 8)
                bytes_to_read = num_pages * 8
                chunk_size = 8192
                
                while bytes_to_read > 0:
                    read_size = min(bytes_to_read, chunk_size)
                    try:
                        data = f.read(read_size)
                    except OSError:
                        break 
                        
                    if not data:
                        break
                        
                    entries = struct.unpack(f"={len(data)//8}Q", data)
                    for entry in entries:
                        if (entry >> 55) & 1:
                            dirty_pages += 1
                            
                    bytes_to_read -= read_size
    except Exception as e:
        print(f"Error reading pagemap: {e}")
        
    return dirty_pages

def main():
    parser = argparse.ArgumentParser(description="Track dirty page rate of a process.")
    parser.add_argument("pid", type=int, help="Target Process ID (Host PID)")
    parser.add_argument("--interval", type=float, default=1.0, help="Sampling interval in seconds")
    parser.add_argument("--output", type=str, default=None, help="Output CSV file name")
    args = parser.parse_args()

    pid = args.pid
    interval = args.interval
    # only use the node name
    hostname = socket.gethostname().split('.')[0]
    
    # Dynamically generate filename if not explicitly provided
    output_file = args.output if args.output else f"dirty_pages_{hostname}_{pid}.csv"

    print(f"Tracking dirty pages for PID {pid} every {interval}s...")
    print(f"Saving data to: {output_file}")
    print("Elapsed(s)\tTime\t\tDirty Pages\tRate (MB/s)")
    print("-" * 60)

    start_time = time.time()

    try:
        with open(output_file, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Elapsed_Seconds", "Timestamp", "Dirty_Pages", "Rate_MB_per_sec"])
            
            while True:
                vma_ranges = get_vma_ranges(pid)
                clear_soft_dirty(pid)
                
                time.sleep(interval)
                
                dirty_count = count_dirty_pages(pid, vma_ranges)
                
                mb_dirtied = (dirty_count * PAGE_SIZE) / (1024 * 1024)
                mb_per_sec = mb_dirtied / interval
                
                current_time = time.strftime("%H:%M:%S")
                elapsed_sec = time.time() - start_time
                
                print(f"{elapsed_sec:.1f}\t\t{current_time}\t{dirty_count}\t\t{mb_per_sec:.2f} MB/s")
                
                csv_writer.writerow([f"{elapsed_sec:.2f}", current_time, dirty_count, f"{mb_per_sec:.4f}"])
                csvfile.flush()
                
    except KeyboardInterrupt:
        print("\nStopping tracker. Data saved.")

if __name__ == "__main__":
    main()
