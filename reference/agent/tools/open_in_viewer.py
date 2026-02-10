#!/usr/bin/env python3
import os
import sys
import glob
import subprocess
import argparse

def get_latest_log(logs_dir="agent/logs"):
    list_of_files = glob.glob(os.path.join(logs_dir, "*.wpilog"))
    if not list_of_files:
        return None
    return max(list_of_files, key=os.path.getctime)

def find_advantagescope():
    # Common locations on macOS
    paths = [
        "/Applications/AdvantageScope.app",
        os.path.expanduser("~/Applications/AdvantageScope.app"),
        "/Users/edan/wpilib/2025/advantagescope/AdvantageScope (WPILib).app" # Found via mdfind
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def main():
    parser = argparse.ArgumentParser(description="Open log in AdvantageScope.")
    parser.add_argument("--file", type=str, help="Path to .wpilog file")
    args = parser.parse_args()

    file_path = args.file
    if not file_path:
        file_path = get_latest_log()
        if not file_path:
            print("No log files found.")
            sys.exit(1)
    
    print(f"Opening: {file_path}")
    
    app_path = find_advantagescope()
    if not app_path:
        print("AdvantageScope application not found.")
        print("Please ensure it is installed in /Applications or ~/Applications.")
        sys.exit(1)
    
    print(f"Using AdvantageScope at: {app_path}")
    
    # macOS specific open command
    if sys.platform == "darwin":
        subprocess.run(["open", "-a", app_path, file_path])
    else:
        print("This script currently only supports macOS for opening apps.")
        # TODO: Add Windows/Linux support if needed (using 'start' or 'xdg-open')

if __name__ == "__main__":
    main()