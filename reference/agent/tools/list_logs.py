#!/usr/bin/env python3
import glob
import os
import time
import argparse
from datetime import datetime
import struct

try:
    from wpiutil.log import DataLogReader
except ImportError:
    print("Error: 'robotpy-wpiutil' not installed.")
    print("Run: pip install -r agent/tools/requirements.txt")
    import sys
    sys.exit(1)

def get_log_info(file_path):
    try:
        reader = DataLogReader(file_path)
        if not reader:
            return None
        
        start_time = 0
        end_time = 0
        entry_map = {} # id -> name
        
        # We only need to scan enough to find duration and maybe some metadata if we want
        # But DataLogReader is an iterator. 
        # To get duration we usually need to read the whole file or at least find the last timestamp.
        # For speed on large logs, this might be slow.
        
        # Optimization: Just read first and last record? 
        # DataLogReader doesn't support random access easily.
        # We will iterate.
        
        count = 0
        for record in reader:
            if record.isStart():
                data = record.getStartData()
                entry_map[data.entry] = data.name
            
            # Timestamp is in micros
            ts = record.timestamp / 1000000.0
            if start_time == 0:
                start_time = ts
            end_time = ts
            count += 1
            
        duration = end_time - start_time
        return {
            "duration": duration,
            "entries": len(entry_map),
            "records": count
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="List available WPILog files.")
    parser.add_argument("--dir", type=str, default="agent/logs", help="Directory containing logs")
    args = parser.parse_args()
    
    log_dir = args.dir
    if not os.path.exists(log_dir):
        print(f"Directory not found: {log_dir}")
        return

    files = glob.glob(os.path.join(log_dir, "*.wpilog"))
    files.sort(key=os.path.getmtime, reverse=True) # Newest first

    print(f"{'Timestamp':<20} {'Size':<10} {'Duration':<10} {'File Name'}")
    print("-" * 80)

    for f in files:
        stat = os.stat(f)
        mod_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        size_mb = stat.st_size / (1024 * 1024)
        filename = os.path.basename(f)
        
        # Optional: Read file to get duration (can be slow for many large files)
        # For now, let's just list them. 
        # If user wants duration, we could add a --scan flag.
        # Let's keep it simple for now.
        
        print(f"{mod_time:<20} {size_mb:6.2f} MB {'-':<10} {filename}")

if __name__ == "__main__":
    main()