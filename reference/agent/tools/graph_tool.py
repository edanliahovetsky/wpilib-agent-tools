#!/usr/bin/env python3
import argparse
import struct
import sys
import os
import glob
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

try:
    from wpiutil.log import DataLogReader
except ImportError:
    print("Error: 'robotpy-wpiutil' not installed. Run: pip install -r agent/tools/requirements.txt", file=sys.stderr)
    sys.exit(1)

def get_latest_log(logs_dir="agent/logs"):
    # Handle running from root or agent/tools
    if not os.path.exists(logs_dir):
        # Try relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(script_dir, "../../agent/logs")
        
    if not os.path.exists(logs_dir):
         return None

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
            return data
    except Exception as e:
        return None

def calculate_derivative(times, values):
    if len(times) < 2:
        return times, values
    
    derivs = []
    new_times = []
    for i in range(1, len(times)):
        dt = times[i] - times[i-1]
        if dt == 0: continue
        dv = values[i] - values[i-1]
        derivs.append(dv / dt)
        new_times.append(times[i]) # Use end time or midpoint
    return new_times, derivs

def calculate_integral(times, values):
    if len(times) < 2:
        return times, values
    
    integrals = []
    new_times = []
    accumulated = 0.0
    for i in range(1, len(times)):
        dt = times[i] - times[i-1]
        # Trapezoidal rule
        avg_val = (values[i] + values[i-1]) / 2.0
        accumulated += avg_val * dt
        integrals.append(accumulated)
        new_times.append(times[i])
    return new_times, integrals

def main():
    parser = argparse.ArgumentParser(description="Graph data from WPILog files.")
    parser.add_argument("--file", type=str, help="Path to .wpilog file")
    parser.add_argument("--key", type=str, action='append', required=True, help="Key to graph (can be used multiple times)")
    parser.add_argument("--mode", type=str, choices=["values", "deriv", "integral"], default="values", help="Graph mode: values (default), deriv, integral")
    parser.add_argument("--output", type=str, default="graph.png", help="Output filename (saved in agent/visualizations/)")
    parser.add_argument("--start", type=float, help="Start timestamp (seconds)")
    parser.add_argument("--end", type=float, help="End timestamp (seconds)")
    parser.add_argument("--title", type=str, help="Graph title")
    parser.add_argument("--scatter", action="store_true", help="Use scatter plot instead of line")
    
    args = parser.parse_args()
    
    # Resolve file
    file_path = args.file
    if not file_path:
        file_path = get_latest_log()
        if not file_path:
            print("Error: No log files found in agent/logs/ and no file specified.")
            sys.exit(1)
    
    print(f"Reading log: {file_path}")
    
    # Read log
    try:
        reader = DataLogReader(file_path)
    except Exception as e:
        print(f"Error: Could not open log file: {e}")
        sys.exit(1)
        
    if not reader:
        print("Error: Valid header not found.")
        sys.exit(1)

    # Scan for keys
    wanted_keys = set(args.key)
    entry_map = {} # id -> type_str
    found_ids = {} # id -> key_name
    
    # Structure: key -> {'x': [], 'y': []}
    data_store = {k: {'x': [], 'y': []} for k in wanted_keys}
    
    for record in reader:
        if record.isStart():
            entry = record.getStartData()
            if entry.name in wanted_keys:
                found_ids[entry.entry] = entry.name
                entry_map[entry.entry] = entry.type
        elif record.isFinish():
            pass
        elif record.isSetMetadata():
            pass
        elif record.isControl():
            pass
        else:
            entry_id = record.getEntry()
            if entry_id in found_ids:
                ts = record.getTimestamp() / 1000000.0
                
                if args.start and ts < args.start: continue
                if args.end and ts > args.end: continue
                
                key_name = found_ids[entry_id]
                type_str = entry_map[entry_id]
                val = decode_value(record.getRaw(), type_str)
                
                if val is not None:
                    # Handle numeric types
                    if isinstance(val, (int, float)):
                         data_store[key_name]['x'].append(ts)
                         data_store[key_name]['y'].append(val)
                    elif isinstance(val, bool):
                         data_store[key_name]['x'].append(ts)
                         data_store[key_name]['y'].append(1.0 if val else 0.0)
                    elif isinstance(val, list) and len(val) > 0 and isinstance(val[0], (int, float)):
                        # For arrays, take first element (common for pose2d/3d or simply array data)
                        data_store[key_name]['x'].append(ts)
                        data_store[key_name]['y'].append(val[0])

    # Process Data (Deriv/Integral)
    plot_data = {}
    for key, vals in data_store.items():
        if not vals['x']:
            print(f"Warning: No data found for key '{key}'")
            continue
            
        x_vals = vals['x']
        y_vals = vals['y']
        
        if args.mode == "deriv":
            x_vals, y_vals = calculate_derivative(x_vals, y_vals)
            label = f"d({key})/dt"
        elif args.mode == "integral":
            x_vals, y_vals = calculate_integral(x_vals, y_vals)
            label = f"∫({key}) dt"
        else:
            label = key
            
        plot_data[key] = {'x': x_vals, 'y': y_vals, 'label': label}

    if not plot_data:
        print("No data found to graph.")
        sys.exit(1)

    # Plotting
    plt.figure(figsize=(12, 6))
    
    for key, pdata in plot_data.items():
        if args.scatter:
            plt.scatter(pdata['x'], pdata['y'], label=pdata['label'], s=10)
        else:
            plt.plot(pdata['x'], pdata['y'], label=pdata['label'])

    # Title and Labels
    title = args.title if args.title else f"Log Analysis ({args.mode})"
    plt.title(title)
    plt.xlabel("Time (seconds)")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Output path handling
    output_dir = "agent/visualizations"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Ensure filename is just filename, not path
    output_name = os.path.basename(args.output)
    output_path = os.path.join(output_dir, output_name)
    
    plt.savefig(output_path)
    print(f"Graph saved to: {output_path}")

if __name__ == "__main__":
    main()