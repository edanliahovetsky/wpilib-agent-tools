#!/usr/bin/env python3
import argparse
import struct
import sys
import os
import glob
import math
from pathlib import Path
import statistics

try:
    from wpiutil.log import DataLogReader
except ImportError:
    print("Error: 'robotpy-wpiutil' not installed. Run: pip install -r agent/tools/requirements.txt", file=sys.stderr)
    sys.exit(1)

def get_latest_log(logs_dir="agent/logs"):
    list_of_files = glob.glob(os.path.join(logs_dir, "*.wpilog"))
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

def decode_value(data, type_str):
    try:
        if type_str == "double":
            return struct.unpack('<d', data)[0]
        elif type_str == "float":
            return struct.unpack('<f', data)[0]
        elif type_str == "int64" or type_str == "integer":
            return struct.unpack('<q', data)[0]
        elif type_str == "boolean":
            return bool(data[0])
        elif type_str == "string":
            return data.decode('utf-8')
        elif type_str == "double[]":
            count = len(data) // 8
            return list(struct.unpack(f'<{count}d', data))
        elif type_str == "boolean[]":
            return [bool(b) for b in data]
        elif type_str == "float[]":
            count = len(data) // 4
            return list(struct.unpack(f'<{count}f', data))
        else:
            # Fallback for unknown types or raw bytes
            return data
    except Exception as e:
        return f"<decode error: {e}>"

def main():
    parser = argparse.ArgumentParser(description="Analyze WPILog files.")
    parser.add_argument("--file", type=str, help="Path to .wpilog file")
    parser.add_argument("--key", type=str, help="Key to analyze")
    parser.add_argument("--mode", type=str, choices=["timestamps", "values", "avg", "ds", "minmax", "deriv", "integral"], required=True, help="Analysis mode")
    parser.add_argument("--start", type=float, help="Start timestamp (seconds)")
    parser.add_argument("--end", type=float, help="End timestamp (seconds)")
    parser.add_argument("--limit", type=int, help="Limit number of samples (for values mode)")
    
    args = parser.parse_args()

    # Resolve file
    file_path = args.file
    if not file_path:
        file_path = get_latest_log()
        if not file_path:
            print("Error: No log files found in agent/logs/ and no file specified.")
            sys.exit(1)
        print(f"Using latest log: {file_path}")

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    # Read log
    reader = DataLogReader(file_path)
    if not reader:
        print("Error: Could not open log file.")
        sys.exit(1)

    # Scan variables
    entry_map = {} # id -> {name, type}
    target_id = None
    target_type = None
    
    # For DS mode
    ds_keys = {
        "DriverStation/Enabled": None,
        "DriverStation/Autonomous": None, 
        "DriverStation/Test": None,
        "DriverStation/AllianceStation": None,
        "DriverStation/MatchTime": None
    }
    ds_ids = {} # id -> key_name

    # Data collection
    data_points = [] # (time_sec, value)
    
    # First pass: Find ID and Type (and collect data if we can do it in one pass)
    # Since DataLogReader is an iterator, we iterate once.
    
    for record in reader:
        if record.isStart():
            try:
                entry_data = record.getStartData()
                entry_id = entry_data.entry
                name = entry_data.name
                type_str = entry_data.type
                entry_map[entry_id] = {'name': name, 'type': type_str}

                if args.key and name == args.key:
                    target_id = entry_id
                    target_type = type_str
                
                if args.mode == "ds" and name in ds_keys:
                    ds_ids[entry_id] = name

            except AttributeError:
                # Handle potential API differences if getStartData returns simple object or similar
                pass
                
        elif record.isFinish():
            pass
        elif record.isSetMetadata():
            pass
        elif record.isControl():
            pass
        else:
            # Data record
            entry_id = record.getEntry()
            timestamp_micros = record.getTimestamp()
            timestamp_sec = timestamp_micros / 1000000.0
            
            # Check filters
            if args.start and timestamp_sec < args.start:
                continue
            if args.end and timestamp_sec > args.end:
                continue

            # Collect target data
            if entry_id == target_id:
                val = decode_value(record.getRaw(), target_type)
                data_points.append((timestamp_sec, val))
            
            # Collect DS data if mode is ds
            if args.mode == "ds" and entry_id in ds_ids:
                # For DS, we might want to collect all changes? 
                # The prompt says "DS state at a certain time". 
                # We will collect all DS events and reconstruct state later if needed.
                # But since we iterate in order, we can just print or store.
                # Let's store them to find state at 'start' time if provided, or just dump.
                val = decode_value(record.getRaw(), entry_map[entry_id]['type'])
                data_points.append((timestamp_sec, ds_ids[entry_id], val))

    if args.key and target_id is None and args.mode != "ds":
        print(f"Error: Key '{args.key}' not found in log.")
        sys.exit(1)

    # Process Data
    
    if args.mode == "timestamps":
        if not data_points:
            print("No data found for key.")
        else:
            print(f"Start Time: {data_points[0][0]:.6f}s")
            print(f"End Time:   {data_points[-1][0]:.6f}s")
            print(f"Count:      {len(data_points)}")

    elif args.mode == "values":
        count = 0
        for t, v in data_points:
            print(f"{t:.6f}: {v}")
            count += 1
            if args.limit and count >= args.limit:
                break

    elif args.mode == "avg":
        if not data_points:
            print("No data.")
        else:
            # Filter out non-numeric
            values = [v for t, v in data_points if isinstance(v, (int, float))]
            if not values:
                 # Try handling arrays?
                 first_val = data_points[0][1]
                 if isinstance(first_val, list):
                     # Average of vectors?
                     # Calculate element-wise average
                     try:
                        vector_sum = [0.0] * len(first_val)
                        count = 0
                        for t, v in data_points:
                            if isinstance(v, list) and len(v) == len(vector_sum):
                                for i in range(len(v)):
                                    vector_sum[i] += v[i]
                                count += 1
                        avg_vec = [x / count for x in vector_sum]
                        print(f"Average: {avg_vec}")
                     except:
                        print("Could not calculate average for this type.")
                 else:
                    print("No numeric data.")
            else:
                avg = statistics.mean(values)
                print(f"Average: {avg}")

    elif args.mode == "minmax":
        if not data_points:
            print("No data.")
        else:
            # Assuming scalar
            try:
                min_val = min(data_points, key=lambda x: x[1])
                max_val = max(data_points, key=lambda x: x[1])
                print(f"Min: {min_val[1]} at {min_val[0]:.6f}s")
                print(f"Max: {max_val[1]} at {max_val[0]:.6f}s")
            except:
                print("Could not calculate min/max (possibly non-scalar data).")

    elif args.mode == "deriv":
        if len(data_points) < 2:
            print("Not enough data for derivative.")
        else:
            print("Timestamp, Derivative")
            for i in range(1, len(data_points)):
                t1, v1 = data_points[i-1]
                t2, v2 = data_points[i]
                if t2 == t1: continue
                if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                    deriv = (v2 - v1) / (t2 - t1)
                    print(f"{t2:.6f}: {deriv}")

    elif args.mode == "integral":
        if len(data_points) < 2:
            print("Not enough data.")
        else:
            integral = 0.0
            for i in range(1, len(data_points)):
                t1, v1 = data_points[i-1]
                t2, v2 = data_points[i]
                dt = t2 - t1
                if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                    # Trapezoidal
                    integral += (v1 + v2) / 2 * dt
            print(f"Integral: {integral}")

    elif args.mode == "ds":
        # Reconstruct state at target time (args.start) or just dump
        if args.start:
            # Find state just before args.start
            current_state = {k: "Unknown" for k in ds_keys}
            
            # Iterate all data points (which are (t, key, val))
            # Sort by time just in case (should be sorted)
            # data_points for DS is [(t, name, val), ...]
            
            # Note: data_points here contains mixed keys because we collected all DS keys
            # We need to filter to before start
            
            target_time = args.start
            
            # Replay up to target time
            for t, key_name, val in data_points:
                if t <= target_time:
                    current_state[key_name] = val
                else:
                    break
            
            print(f"DS State at {target_time}s:")
            for k, v in current_state.items():
                print(f"  {k}: {v}")
        else:
            print("Dump of DS Events:")
            for t, key_name, val in data_points:
                print(f"{t:.6f}: {key_name} = {val}")

if __name__ == "__main__":
    main()