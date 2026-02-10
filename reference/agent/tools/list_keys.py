#!/usr/bin/env python3
import argparse
import glob
import os
import sys

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

def main():
    parser = argparse.ArgumentParser(description="List all keys in a WPILog file.")
    parser.add_argument("--file", type=str, help="Path to .wpilog file")
    parser.add_argument("--filter", type=str, help="Filter keys by substring")
    args = parser.parse_args()

    file_path = args.file
    if not file_path:
        file_path = get_latest_log()
        if not file_path:
            print("Error: No log files found in agent/logs/.")
            sys.exit(1)
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    print(f"Reading keys from: {file_path}")
    print("-" * 40)

    try:
        reader = DataLogReader(file_path)
        for record in reader:
            if record.isStart():
                try:
                    data = record.getStartData()
                    name = data.name
                    if args.filter:
                        if args.filter.lower() in name.lower():
                            print(name)
                    else:
                        print(name)
                except AttributeError:
                    pass
    except Exception as e:
        print(f"Error reading log: {e}")

if __name__ == "__main__":
    main()