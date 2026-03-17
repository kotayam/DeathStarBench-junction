#!/usr/bin/env python3
import os
import sys
import time
import struct
import argparse

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
                # The first column is the address range (e.g., "00400000-0040c000")
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
                
                # Seek to the pagemap entry for the start of this VMA
                f.seek(start_page * 8)
                
                bytes_to_read = num_pages * 8
                chunk_size = 8192  # Read in chunks to manage memory
                
                while bytes_to_read > 0:
                    read_size = min(bytes_to_read, chunk_size)
                    try:
                        data = f.read(read_size)
                    except OSError:
                        break # Skip unreadable memory regions
                        
                    if not data:
                        break
                        
                    # Unpack as 64-bit unsigned integers
                    entries = struct.unpack(f"={len(data)//8}Q", data)
                    for entry in entries:
                        # Bit 55 is the soft-dirty bit in the Linux pagemap
                        if (entry >> 55) & 1:
                            dirty_pages += 1
                            
                    bytes_to_read -= read_size
    except Exception as e:
        print(f"Error reading pagemap: {e}")
        
    return dirty_pages

def main():
    parser = argparse.ArgumentParser(description="Track dirty page rate of a process via pagemap.")
    parser.add_argument("pid", type=int, help="Target Process ID (Host PID)")
    parser.add_argument("--interval", type=float, default=1.0, help="Sampling interval in seconds")
    args = parser.parse_args()

    pid = args.pid
    interval = args.interval

    print(f"Tracking dirty pages for PID {pid} every {interval}s...")
    print("Time\t\tDirty Pages\tRate (MB/s)")
    print("-" * 50)

    try:
        while True:
            # 1. Map memory ranges
            vma_ranges = get_vma_ranges(pid)
            
            # 2. Clear the soft-dirty bits
            clear_soft_dirty(pid)
            
            # 3. Wait for the application to modify memory
            time.sleep(interval)
            
            # 4. Count how many pages were dirtied
            dirty_count = count_dirty_pages(pid, vma_ranges)
            
            # 5. Calculate MB/s
            mb_dirtied = (dirty_count * PAGE_SIZE) / (1024 * 1024)
            mb_per_sec = mb_dirtied / interval
            
            current_time = time.strftime("%H:%M:%S")
            print(f"{current_time}\t{dirty_count}\t\t{mb_per_sec:.2f} MB/s")
            
    except KeyboardInterrupt:
        print("\nStopping tracker.")

if __name__ == "__main__":
    main()
